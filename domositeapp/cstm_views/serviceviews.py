
from django.db.models import Count
from django.shortcuts import redirect
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import permissions, serializers, generics, mixins
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

from domositeapp import permissions as custom_perm
from domositeapp.renderers import CustomHTMLRenderer
from domositeapp.models import CustomService, Service, Server, LogAction
from domositeapp.serializers import CustomServiceSerializer, DevicePresentSerializer
from domositeapp.forms import ServiceCreationForm

import requests
import json
import thread

def update_service_on_servers(view):
    servers = Server.objects.filter(user=view.request.user)
    services = view.get_serializer(view.get_queryset(), many=True)
    for s in servers:
        url = "http://"+str(s.proxy_address)+":"+str(s.proxy_port)+"/services"
        try:
            resp = requests.put(url, data=json.dumps({"SERVICES":services.data}),\
                                    headers={"content-type":"application/json"})
        except:
            pass

class CustomServicesView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = CustomServiceSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return CustomService.objects.filter(user=user).annotate(device_count=Count("device__id"))

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            if "core_service_ref" in data.keys() and data["core_service_ref"] is not None:
                serializer.validated_data["name"] = data["core_service_ref"].name
            elif data["name"] in [h.name for h in Service.objects.all()]:
                raise serializers.ValidationError({"name":\
                                                    ["core service with this name already exists."]})
        except KeyError as err:
            raise serializers.ValidationError({err:["This field is required."]})
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["custom service with this name already exists."]})

        act = LogAction(action=LogAction.CREATE,\
                        description="Created new Service with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.SERVICE,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            if "core_service_ref" in data.keys() and data["core_service_ref"] is not None:
                serializer.validated_data["name"] = data["core_service_ref"].name
            elif data["name"] in [h.name for h in Service.objects.all()]:
                raise serializers.ValidationError({"name":\
                                                    ["core service with this name already exists."]})
        except KeyError as err:
            raise serializers.ValidationError({err:["This field is required."]})
            
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["custom service with this name already exists."]})

        act = LogAction(action=LogAction.UPDATE,\
                        description="Updated Service with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.SERVICE,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_destroy(self, instance):
        id_str = str(instance.id)
        instance.delete()

        act = LogAction(action=LogAction.DELETE,\
                        description="Deleted Service with ID "+id_str,\
                        instance_class=LogAction.SERVICE,\
                        instance_id=int(id_str),\
                        user=self.request.user)
        act.save()
#
#### HTML VIEWS ####
class ListHTMLView(CustomServicesView, LoginRequiredMixin, generics.ListAPIView):
    renderer_classes = [CustomHTMLRenderer,]

    template_name = "./services/services.html"

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        form = ServiceCreationForm()
        return Response({"form":form, "services":resp.data}, status=resp.status_code)

class DetailHTMLView(CustomServicesView, LoginRequiredMixin, generics.RetrieveAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./services/serviceDetail.html"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        devices = DevicePresentSerializer(instance.device_set, many=True)

        form = ServiceCreationForm(initial=serializer.data)
        return Response({"form": form, "ele":serializer.data, "devices":devices.data})

#
### API VIEWS ####
class ListJSONView(CustomServicesView, generics.ListCreateAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"services":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            thread.start_new_thread(update_service_on_servers, (self,))
            return redirect("servicesAPI")

        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class DetailJSONView(CustomServicesView, generics.RetrieveUpdateDestroyAPIView):
    #all come from generics.RetrieveUpdateDestroyAPIView
    renderer_classes = [JSONRenderer,]

    def put(self, request, *args, **kwargs):
        resp = self.update(request, *args, **kwargs)
        thread.start_new_thread(update_service_on_servers, (self,))
        return resp

    def patch(self, request, *args, **kwargs):
        resp = self.partial_update(request, *args, **kwargs)
        thread.start_new_thread(update_service_on_servers, (self,))
        return resp

    def delete(self, request, *args, **kwargs):
        resp = self.destroy(request, *args, **kwargs)
        thread.start_new_thread(update_service_on_servers, (self,))
        return resp

class ServiceDevicesJSONView(CustomServicesView, generics.GenericAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        service = self.get_object()
        resp = service.device_set.all()
        resp = DevicePresentSerializer(resp, many=True)
        for d in resp.data:
            d.pop("services")
            d.pop("state")
        data = {"devices":resp.data}
        return Response(data)