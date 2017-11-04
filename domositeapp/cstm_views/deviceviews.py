
from datetime import timedelta
import json
import copy

import requests

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import permissions, generics, status, serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from domositeapp import permissions as custom_perm
from domositeapp.renderers import CustomHTMLRenderer
from domositeapp.models import Device, PropertyChange, PropertyType, LogAction, DeviceType
from domositeapp.serializers import DeviceSerializer, DevicePresentSerializer,\
                                    PropertySerializer, PropertyChangeSerializer
from domositeapp.forms import DeviceCreationForm, ScalarTypeForm, EnumTypeForm

import time

class CustomDevicesView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = DeviceSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Device.objects.filter(user=user)

    def perform_create(self, serializer):
        data = serializer.validated_data

        try:
            if data["server"] not in self.request.user.server_set.all():
                raise serializers.ValidationError({"server":["Server with ID ("+str(data["server"].id)+") does not exist"]})
        except KeyError:
            raise serializers.ValidationError({"server":["This field is required"]})

        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"address":\
                                                ["device with this address already exists."]})

        act = LogAction(action=LogAction.CREATE,\
                        description="Registered new Device with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.DEVICE,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()
        act = LogAction(action=LogAction.STAT_UP,\
                        description="Device with ID "+str(serializer.data["id"])+" is now Running",\
                        instance_class=LogAction.DEVICE,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_update(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"address":\
                                                ["device with this address already exists."]})

        act = LogAction(action=LogAction.UPDATE,\
                        description="Updated Device with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.DEVICE,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_destroy(self, instance):
        if not instance.active:
            id_str = str(instance.id)
            instance.delete()

            act = LogAction(action=LogAction.DELETE,\
                            description="Deleted Device with ID "+id_str,\
                            instance_class=LogAction.DEVICE,\
                            instance_id=int(id_str),\
                            user=self.request.user)
            act.save()
            return True
        else:
            raise PermissionDenied(detail="Device is currently running so it can not be deleted.")

    def get_history_records(self, instance, change_id=None, start=None, end=None, source=None, state_filter={}, nb_results=20):

        if start is None:
            start = timezone.now()-timedelta(days=730000)

        if end is None:
            end = timezone.now()

        if source is None:
            if change_id is None:
                hist = PropertyChange.objects.filter(device_id=instance,\
                                                timestamp__range=(start, end)).order_by("-timestamp")
            else:
                hist = PropertyChange.objects.filter(device_id=instance,\
                                                id=change_id,\
                                                timestamp__range=(start, end)).order_by("-timestamp")
        else:
            if change_id is None:
                hist = PropertyChange.objects.filter(device_id=instance,\
                                                source=source,\
                                                timestamp__range=(start, end)).order_by("-timestamp")
            else:
                hist = PropertyChange.objects.filter(device_id=instance,\
                                                source=source,\
                                                id=change_id,\
                                                timestamp__range=(start, end)).order_by("-timestamp")
        
        if nb_results:
            hist_data = PropertyChangeSerializer(hist[:nb_results], many=True)
        else:
            hist_data = PropertyChangeSerializer(hist, many=True)

        act = LogAction(action=LogAction.READ,\
                        description="Retrieved Device with ID "+str(instance.id)+" property history",\
                        instance_class=LogAction.DEVICE,\
                        instance_id=int(instance.id),\
                        user=self.request.user)
        act.save()

        aux = hist_data.data
        data = []
        dim = len(state_filter.keys())
        for p_ch in aux:
            filtered = dim
            p_ch["new_state"] = json.loads(p_ch["new_state"])
            for key, val in state_filter.iteritems():
                if str(p_ch["new_state"][key]) == str(val):
                    filtered -= 1

            if filtered == 0:      
                data.append(p_ch)
        
        return data

#
#### HTML VIEWS
class ListHTMLView(CustomDevicesView, LoginRequiredMixin, generics.ListAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./devices/devices.html"
    serializer_class = DevicePresentSerializer

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"devices":resp.data}, status=resp.status_code)


class DetailHTMLView(CustomDevicesView, LoginRequiredMixin, generics.RetrieveAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./devices/deviceDetail.html"
    serializer_class = DevicePresentSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        form = DeviceCreationForm(user=self.request.user, initial=serializer.data)

        prop_forms = {}
        for p in instance.property_set.all():
            if p.property_type.value_type_class == PropertyType.SCALAR:
                prop_forms[p.name] = ScalarTypeForm(p)
            else:
                prop_forms[p.name] = EnumTypeForm(p)

        try:
            history = self.get_history_records(instance)
        except ValidationError as err:
            Response({"detail":err.detail}, status=err.default_code)

        return Response({"form": form, "ele":serializer.data,\
                        "property_forms":prop_forms, "history":history})

#
##### API VIEWS #######
class ListJSONView(CustomDevicesView, generics.ListCreateAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        try:
            server_id = request.GET["server"]
            resp_q = Device.objects.filter(server=int(server_id))
            resp = DevicePresentSerializer(resp_q, many=True)
            for d in resp.data:
                d.pop("state")
            return Response({"devices":resp.data})
        except:
            pass

        try:
            division_id = request.GET["division"]
            resp_q = Device.objects.filter(division=int(division_id))
            resp = DevicePresentSerializer(resp_q, many=True)
            for d in resp.data:
                d.pop("state")
            return Response({"devices":resp.data})
        except:
            pass

        try:
            type_id = request.GET["type"]
            resp_q = Device.objects.filter(device_type=int(type_id))
            resp = DevicePresentSerializer(resp_q, many=True)
            for d in resp.data:
                d.pop("state")
            return Response({"devices":resp.data})
        except:
            pass

        try:
            services_id = request.GET["services"]
            resp_q = Device.objects.filter(services=int(services_id))
            resp = DevicePresentSerializer(resp_q, many=True)
            for d in resp.data:
                d.pop("state")
            return Response({"devices":resp.data})
        except:
            pass

        resp = self.list(request, *args, **kwargs)
        for d in resp.data:
            d.pop("state")
        return Response({"devices":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return redirect("devicesAPI")
        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class DetailJSONView(CustomDevicesView, generics.RetrieveUpdateDestroyAPIView):
    #all come from generics.RetrieveUpdateDestroyAPIView
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = copy.deepcopy(serializer.data)
        data.pop("state")
        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()

        try:
            fromserver = bool(request.GET.get("fromserver"))
        except KeyError:
            fromserver = False

        #print "Fromserver: "+str(fromserver)

        if (not fromserver) and instance.active:
            
            headers = {"content-type":"application/json"}
            url = "http://"+str(instance.server.proxy_address)+":"+str(instance.server.proxy_port)+"/devices/"+str(instance.local_id)
            try:
                req_data = {"name": data["name"]}
                resp = requests.put(url, data=json.dumps(req_data), headers=headers, timeout=10)

                resp_data = json.loads(resp.text)
                if resp.status_code != 200:
                    return Response(data=resp_data, status=resp.status_code)
            except requests.ConnectionError:
                resp_data = {"error_code": 504, "error_msg": "Home Server is Down"}
                last_active = instance.active
                instance.active = False
                instance.save()
                if not instance.active and  last_active:
                    act = LogAction(action=LogAction.STAT_DOWN,\
                                    description="Device with ID "+str(instance.id)+" is Down",\
                                    instance_class=LogAction.DEVICE,\
                                    instance_id=int(instance.id),\
                                    user=self.request.user)
                    act.save()
                return Response(data=resp_data, status=status.HTTP_504_GATEWAY_TIMEOUT)
            except:
                resp_data = {"error_code": 400, "error_msg": "Name field is required"}
                return Response(data=resp_data, status=status.HTTP_400_BAD_REQUEST)

            try:
                req_data = data["services"]
                resp = requests.put(url+"/services", data=json.dumps(req_data), headers=headers, timeout=10)

                resp_data = json.loads(resp.text)
                if resp.status_code != 200:
                    return Response(data=resp_data, status=resp.status_code)
            except requests.ConnectionError:
                resp_data = {"error_code": 504, "error_msg": "Home Server is Down"}
                last_active = instance.active
                instance.active = False
                instance.save()
                if not instance.active and  last_active:
                    act = LogAction(action=LogAction.STAT_DOWN,\
                                    description="Device with ID "+str(instance.id)+" is Down",\
                                    instance_class=LogAction.DEVICE,\
                                    instance_id=int(instance.id),\
                                    user=self.request.user)
                    act.save()
                return Response(data=resp_data, status=status.HTTP_504_GATEWAY_TIMEOUT)
            except:
                resp_data = {"error_code": 400, "error_msg": "Services field is required"}
                return Response(data=resp_data, status=status.HTTP_400_BAD_REQUEST)

            new_data = {}
            
            try:
                new_data["division"] = data["division"]
            except:
                resp_data = {"error_code": 400, "error_msg": "Division field is required"}
                return Response(data=resp_data, status=status.HTTP_400_BAD_REQUEST)

            new_data["name"] = data["name"]
            new_data["services"] = data["services"]
            serializer = self.get_serializer(instance, data=new_data, partial=partial)
            serializer.is_valid(raise_exception=True)

        elif fromserver:
            last_active = instance.active
            instance.active = True
            instance.last_access = timezone.now()

            try: 
                dev_type_id = data["device_type"]
                instance.property_set.all().delete()
                d_type = DeviceType.objects.get(id=dev_type_id)
                instance.device_type = d_type
            except:
                pass
            instance.save()

            if instance.active and not last_active:
                act = LogAction(action=LogAction.STAT_UP,\
                                description="Device with ID "+str(instance.id)+" is now Running",\
                                instance_class=LogAction.DEVICE,\
                                instance_id=int(instance.id),\
                                user=self.request.user)
                act.save()
            
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
        else:
            return Response(data={"detail":"The device is not running so it can not be updated from the cloud."}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If "prefetch_related" has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        
        data = serializer.data
        data.pop("state")
        return Response(data)


class StateJSONView(CustomDevicesView, generics.GenericAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        device = self.get_object()
        return Response(device.state)

    def patch(self, request, *args, **kwargs):

        device = self.get_object()
        fromserver = False
        try:
            fromserver = bool(request.GET.get("fromserver"))
        except:
            fromserver = False

        if fromserver:
            #print "Fromserver"
            last_active = device.active
            server_last_active = device.server.active
            device.active = True
            device.server.active = True
            device.last_access = timezone.now()
            device.server.last_access = timezone.now()

            device.server.save()
            device.save()

            if device.active and not last_active:
                act = LogAction(action=LogAction.STAT_UP,\
                                description="Device with ID "+str(device.id)+" is now Running",\
                                instance_class=LogAction.DEVICE,\
                                instance_id=int(device.id),\
                                user=self.request.user)
                act.save()
            
            if device.server.active and not server_last_active:
                act = LogAction(action=LogAction.STAT_UP,\
                                    description="Server with ID "+str(device.server.id)+" is now Running",\
                                    instance_class=LogAction.SERVER,\
                                    instance_id=int(device.server.id),\
                                    user=self.request.user)
                act.save()
            
            new_state = {}
            for prop in request.data["current_state"]:
                p = device.property_set.get(property_type=prop["property_id"])
                ser = PropertySerializer(p, {"name":prop["name"], "value":prop["value"]})
                if ser.is_valid(raise_exception=True):
                    new_state[prop["name"]] = prop["value"]
                    ser.save()
            
            p_ch = PropertyChange(new_state_text=json.dumps(new_state),\
                                        source="DEVICE", device_id=device)
            p_ch.save()
            return Response()
        else:
            #print "NOT Fromserver"
            headers = {"content-type":"application/json"}
            url = "http://"+str(device.server.proxy_address)+":"+str(device.server.proxy_port)+"/devices/"\
                        +str(device.local_id)+"/state"
            #print url
            if not request.data:
                return Response(data={"detail":"A json body like {\"property_name\":\"property_value\" must be provided}"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                resp = requests.put(url, data=json.dumps(request.data), headers=headers, timeout=device.server.timeout)
                data = json.loads(resp.text)

                #print "RESP CODE:"+str(resp.status_code)+"\n"
                if resp.status_code == 200:
                    return Response(data=device.state, status=resp.status_code)
                    # tryout = 0
                    # resp_get = None
                    # while data["wanted_state"] != data["current_state"] and (tryout < 3):
                    #     resp_get = get_device_state(device_id)
                    #     resp_json = json.loads(resp_get)
                    #     tryout += 1

                    # if resp_json["wanted_state"] == resp_json["current_state"]:
                    #     if not resp_get:
                    #         resp_get = get_device_state(device_id)
                    #     return resp_get
                    # else:
                    #     #print "DEVICE IS NOT RESPONDING"
                    #     raise AppError(502, "The device is not responding")

                    # new_state = {}
                    # for prop, value in data["current_state"].iteritems():
                    #     p = device.property_set.get(name=str(prop))
                    #     ser = PropertySerializer(p, {"name":prop, "value":value})
                    #     if ser.is_valid(raise_exception=True):
                    #         new_state[prop] = value
                    #         ser.save()
                    
                    # p_ch = PropertyChange(new_state_text=json.dumps(new_state),\
                    #                     source="CLOUD", device_id=device)
                    # p_ch.save()
                elif resp.status_code == 502 or resp.status_code == 404:
                    last_active = device.active
                    device.active = False
                    device.last_access = timezone.now()
                    device.save()
                    if not device.active and last_active:
                        act = LogAction(action=LogAction.STAT_DOWN,\
                                        description="Device with ID "+str(device.id)+" is Down",\
                                        instance_class=LogAction.DEVICE,\
                                        instance_id=int(device.id),\
                                        user=self.request.user)
                        act.save()
                    
                    return Response(data=data, status=resp.status_code)
                elif resp.status_code == 504:
                    last_dev_active = device.active
                    last_serv_active = device.server.active
                    device.server.active = False
                    device.active = False
                    device.last_access = timezone.now()

                    device.server.save()
                    device.save()

                    if not device.active and last_dev_active:
                        act = LogAction(action=LogAction.STAT_DOWN,\
                                        description="Device with ID "+str(device.id)+" is Down",\
                                        instance_class=LogAction.DEVICE,\
                                        instance_id=int(device.id),\
                                        user=self.request.user)
                        act.save()

                    if not device.server.active and last_serv_active:
                        act = LogAction(action=LogAction.STAT_DOWN,\
                                        description="Server with ID "+str(device.server.id)+" is Down",\
                                        instance_class=LogAction.DEVICE,\
                                        instance_id=int(device.server.id),\
                                        user=self.request.user)
                        act.save()

                data = {"error_code": 504, "error_msg": "Home Server is Down"}
                return Response(data=data, status=resp.status_code)
            except requests.ConnectionError:
                data = {"error_code": 504, "error_msg": "Home Server is Down"}
                last_active = device.server.active
                device.server.active = False
                device.server.save()
                if not device.server.active and last_active:
                    act = LogAction(action=LogAction.STAT_DOWN,\
                                    description="Server with ID "+str(device.server.id)+" is Down",\
                                    instance_class=LogAction.DEVICE,\
                                    instance_id=int(device.server.id),\
                                    user=self.request.user)
                    act.save()
                return Response(data=data, status=status.HTTP_504_GATEWAY_TIMEOUT)

            except ValidationError as err:
                return Response(data={"detail":err}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except:
                return Response(data={"detail":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

class ChangesHistoryJSONView(CustomDevicesView, generics.GenericAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            start = request.GET["start"]
        except:
            start = None

        try:
            end = request.GET["end"]
        except:
            end = None
        
        try:
            source = request.GET["source"]
        except:
            source = None

        try:
            limit = request.GET["limit"]
            limit = int(limit)
        except:
            limit = None
        
        try:
            id_str = request.GET["id"]
            id_str = int(id_str)
        except:
            id_str = None
        
        try:
            state_filter = {}
            for prop_name, prop_value in instance.properties.iteritems():
                try:
                    check = float(prop_value)
                    state_filter[prop_name] = float(request.GET[prop_name])
                except:
                    try:
                        check = str(prop_value)
                        state_filter[prop_name] = str(request.GET[prop_name])
                    except:
                        pass
        except:
            state_filter = {}

        try:
            hist_data = self.get_history_records(instance, change_id=id_str, start=start,\
                                                end=end, source=source,\
                                                state_filter=state_filter, nb_results=limit)

            return Response(hist_data)
        except ValidationError as err:
            return Response({"detail":err.message}, status=status.HTTP_400_BAD_REQUEST)


def periodic_state_check():
    print "Started Devices Monitoring"
    while(1):
        try:
            for d in Device.objects.all():
                d.state
            
            time.sleep(10)
            print "checking devices"
        except:
            pass