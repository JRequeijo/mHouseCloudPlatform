
from django.db.models import Count
from django.shortcuts import redirect
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone


from rest_framework import permissions, generics, serializers, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from domositeapp import permissions as custom_perm
from domositeapp.renderers import CustomHTMLRenderer
from domositeapp.models import Server, LogAction
from domositeapp.serializers import ServerSerializer, DevicePresentSerializer
from domositeapp.forms import ServerCreationForm

import requests
import json
import thread
import time

class CustomServersView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = ServerSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Server.objects.filter(user=user).annotate(device_count=Count("device__id"))

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"coap_address":\
                                                ["Server with this coap_address already exists."]})
        act = LogAction(action=LogAction.CREATE,\
                        description="Registered new Server with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.SERVER,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()
        act = LogAction(action=LogAction.STAT_UP,\
                        description="Server with ID "+str(serializer.data["id"])+" is now Running",\
                        instance_class=LogAction.SERVER,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_update(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"coap_address":\
                                                ["Server with this coap_address already exists."]})
        act = LogAction(action=LogAction.UPDATE,\
                        description="Updated Server with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.SERVER,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_destroy(self, instance):
        if not instance.active:
            id_str = str(instance.id)
            instance.delete()

            act = LogAction(action=LogAction.DELETE,\
                            description="Deleted Server with ID "+id_str,\
                            instance_class=LogAction.SERVER,\
                            instance_id=int(id_str),\
                            user=self.request.user)
            act.save()

            return True
        else:
            raise PermissionDenied(detail="Server is currently running so it can not be deleted.")

#
#### HTML VIEWS #####
class ListHTMLView(CustomServersView, LoginRequiredMixin, generics.ListAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./servers/servers.html"

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"servers":resp.data}, status=resp.status_code)

class DetailHTMLView(CustomServersView, LoginRequiredMixin, generics.RetrieveAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./servers/serverDetail.html"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        devices = DevicePresentSerializer(instance.device_set, many=True)

        form = ServerCreationForm(initial=serializer.data)
        return Response({"form": form, "ele":serializer.data, "devices":devices.data})

#
##### API VIEWS #####
class ListJSONView(CustomServersView, generics.ListCreateAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"servers":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return redirect("serversAPI")
        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class DetailJSONView(CustomServersView, generics.RetrieveUpdateDestroyAPIView):
    #all come from generics.RetrieveUpdateDestroyAPIView
    renderer_classes = [JSONRenderer,]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()

        try:
            fromserver = bool(request.GET.get("fromserver"))
        except KeyError:
            fromserver = False

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if (not fromserver) and instance.active:
            headers = {"content-type":"application/json"}
            url = "http://"+str(instance.proxy_address)+":"+str(instance.proxy_port)+"/info"
            try:
                req_data = {"name": data["name"]}
                resp = requests.put(url, data=json.dumps(req_data), headers=headers, timeout=5)

                data = json.loads(resp.text)
                if resp.status_code != 200:
                    return Response(data=data, status=resp.status_code)
            except requests.ConnectionError:
                data = {"error_code": 504, "error_msg": "Home Server is Down"}
                last_active = instance.active
                instance.active = False
                instance.save()
                if not instance.active and last_active:
                    act = LogAction(action=LogAction.STAT_DOWN,\
                                    description="Server with ID "+str(instance.id)+" is Down",\
                                    instance_class=LogAction.SERVER,\
                                    instance_id=int(instance.id),\
                                    user=self.request.user)
                    act.save()
                return Response(data=data, status=status.HTTP_504_GATEWAY_TIMEOUT)

        if fromserver:
            instance.last_access = timezone.now()
            last_active = instance.active
            instance.active = True
            instance.save()
            if instance.active and not last_active:
                act = LogAction(action=LogAction.STAT_UP,\
                                description="Server with ID "+str(instance.id)+" is now Running",\
                                instance_class=LogAction.SERVER,\
                                instance_id=int(instance.id),\
                                user=self.request.user)
                act.save()

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If "prefetch_related" has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class StateJSONView(CustomServersView, generics.GenericAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        server = self.get_object()
        if server.active:
            resp = {"server_id":server.id, "name":server.name,\
                    "multicast":server.multicast, "coap_address":server.coap_address,\
                    "coap_port":server.coap_port, "proxy_address":server.proxy_address,\
                    "proxy_port":server.proxy_port, "status":"running"}
        else:
            resp = {"status":"down"}
        return Response(resp)

    def patch(self, request, *args, **kwargs):
        server = self.get_object()
        data = request.data.copy()
        try:
            fromserver = bool(request.GET.get("fromserver"))
        except KeyError:
            fromserver = False
        
        if fromserver:
            if data["status"] == "running":
                server.last_access = timezone.now()
                last_active = server.active
                server.active = True
                server.save()

                if server.active and not last_active:
                    act = LogAction(action=LogAction.STAT_UP,\
                                    description="Server with ID "+str(server.id)+" is now Running",\
                                    instance_class=LogAction.SERVER,\
                                    instance_id=int(server.id),\
                                    user=server.user)
                    act.save()
        
        return Response()

    

class ServerDevicesJSONView(CustomServersView, generics.GenericAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        server = self.get_object()
        resp = server.device_set.all()
        resp = DevicePresentSerializer(resp, many=True)
        for d in resp.data:
            d.pop("server")
            d.pop("state")
        data = {"devices":resp.data}
        return Response(data)

def periodic_state_check():
    print "Started Servers Monitoring"
    while(1):
        try:
            for s in Server.objects.all():
                s.state()
            
            time.sleep(10)
            print "checking servers"
        except:
            pass

