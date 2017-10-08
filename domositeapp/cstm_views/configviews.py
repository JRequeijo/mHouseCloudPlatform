
from django.shortcuts import redirect
from django.db import IntegrityError

from rest_framework import permissions, generics, mixins, status, serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.compat import is_authenticated

from domositeapp import permissions as custom_perm
from domositeapp.renderers import CustomHTMLRenderer
from domositeapp.models import Choice, EnumValueType, ScalarValueType,\
                                PropertyType, DeviceType, Service, Server
from domositeapp.serializers import ChoiceSerializer, EnumValueTypeSerializer,\
                                    ScalarValueTypeSerializer, PropertyTypeSerializer,\
                                    DeviceTypeSerializer, ServiceSerializer
from domositeapp.forms import ChoiceCreationForm, EnumCreationForm,\
                              ScalarCreationForm, PropertyTypeCreationForm, DeviceTypeCreationForm

import requests
import json
import thread

def update_configs_on_servers(view, c_type):
    servers = Server.objects.filter(user=view.request.user)
    configs = view.get_serializer(view.get_queryset(), many=True)

    if c_type == "ENUM_TYPES":
        for enum in configs.data:
            choice_ids = enum["choices"]
            default = enum["default_value"]
            data = {}
            for c in choice_ids:
                choice = Choice.objects.get(id=c)
                data[choice.name] = str(choice.value)
                if c == default:
                    enum["default_value"] = choice.name

            enum["choices"] = data


    for s in servers:
        url = "http://"+str(s.proxy_address)+":"+str(s.proxy_port)+"/configs?type="+str(c_type)
        try:
            resp = requests.put(url, data=json.dumps({c_type:configs.data}),\
                                    headers={"content-type":"application/json"})
        except:
            pass

class CustomConfigsView():

    def get_configs(self):
        user = self.request.user
        if is_authenticated(user):
            q = DeviceType.objects.filter(user=None)|DeviceType.objects.filter(user=user)
            dev_types_ser = DeviceTypeSerializer(q, many=True)

            q = PropertyType.objects.filter(user=None)|PropertyType.objects.filter(user=user)
            prop_types_ser = PropertyTypeSerializer(q, many=True)

            q = ScalarValueType.objects.filter(user=None)|ScalarValueType.objects.filter(user=user)
            scalar_types_ser = ScalarValueTypeSerializer(q, many=True)

            q = EnumValueType.objects.filter(user=None)|EnumValueType.objects.filter(user=user)
            enum_types_ser = EnumValueTypeSerializer(q, many=True)

            q = Choice.objects.filter(user=None)|Choice.objects.filter(user=user)
            choices_ser = ChoiceSerializer(q, many=True)

            choice_form = ChoiceCreationForm()
            enum_form = EnumCreationForm(self.request.user)
            scalar_form = ScalarCreationForm()
            prop_type_form = PropertyTypeCreationForm()
            dev_type_form = DeviceTypeCreationForm(self.request.user)

            services = ServiceSerializer(Service.objects.all(), many=True)

            val_types = {"scalars":scalar_types_ser.data,\
                        "enums":enum_types_ser.data,\
                        "choices":choices_ser.data}

            configs = {"device_types":dev_types_ser.data,\
                    "property_types":prop_types_ser.data,\
                    "value_types":val_types,\
                    "services":services.data}

            data={"configs":configs,
                    "choice_form":choice_form,
                    "enum_form":enum_form,
                    "scalar_form":scalar_form,
                    "prop_type_form":prop_type_form,
                    "dev_type_form":dev_type_form}
            
            return data

        else:
            dev_types_ser = DeviceTypeSerializer(DeviceType.objects.filter(user=None), many=True)
            prop_types_ser = PropertyTypeSerializer(PropertyType.objects.filter(user=None), many=True)
            scalar_types_ser = ScalarValueTypeSerializer(ScalarValueType.objects.filter(user=None), many=True)
            enum_types_ser = EnumValueTypeSerializer(EnumValueType.objects.filter(user=None), many=True)
            choices_ser = ChoiceSerializer(Choice.objects.filter(user=None), many=True)

            services = ServiceSerializer(Service.objects.all(), many=True)

            val_types = {"scalars":scalar_types_ser.data,\
                        "enums":enum_types_ser.data,\
                        "choices":choices_ser.data}

            configs = {"device_types":dev_types_ser.data,\
                    "property_types":prop_types_ser.data,\
                    "value_types":val_types,\
                    "services":services.data}

            data={"configs":configs}
            
            return data
#
### HTML VIEWS ###
class ConfigsHTMLView(CustomConfigsView, generics.GenericAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./configs/configs.html"

    def get(self, request, *args, **kwargs):
        return Response(data=self.get_configs())

#
######################### API VIEWS ###########################
#### ALL CONFIGS ###########
class ConfigsJSONView(CustomConfigsView, generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = [JSONRenderer,]
    def get(self, request, *args, **kwargs):
        return Response(data=self.get_configs()["configs"])

#
### DEVICE TYPES ###
class CustomDeviceTypesView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = DeviceTypeSerializer
    renderer_classes = [JSONRenderer,]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return DeviceType.objects.filter(user=None)|DeviceType.objects.filter(user=user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            if data["name"] in [d.name for d in DeviceType.objects.filter(user=None)]:
                raise serializers.ValidationError({"name":\
                                                    ["core device type with this name already exists."]})
        except KeyError:
            raise serializers.ValidationError({"name":["This field is required"]})
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["device type with this name already exists."]})
    
class DeviceTypesListView(CustomDeviceTypesView, generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"device_types":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            thread.start_new_thread(update_configs_on_servers, (self, "DEVICE_TYPES"))
            return redirect("devicetypesAPI")
        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class DeviceTypesDetailView(CustomDeviceTypesView, generics.RetrieveDestroyAPIView):
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.device_set.count() == 0:
            self.perform_destroy(instance)
            thread.start_new_thread(update_configs_on_servers, (self, "DEVICE_TYPES"))
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

#
### PROPERTY TYPES ###
class CustomPropertyTypesView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = PropertyTypeSerializer
    renderer_classes = [JSONRenderer,]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return PropertyType.objects.filter(user=None)|PropertyType.objects.filter(user=user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            if data["name"] in [p.name for p in PropertyType.objects.filter(user=None)]:
                raise serializers.ValidationError({"name":\
                                                    ["core property type with this name already exists."]})
        except KeyError:
            raise serializers.ValidationError({"name":["This field is required"]})

        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["property type with this name already exists."]})

class PropertyTypesListView(CustomPropertyTypesView, generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"property_types":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            thread.start_new_thread(update_configs_on_servers, (self, "PROPERTY_TYPES"))
            return redirect("propertytypesAPI")
        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class PropertyTypesDetailView(CustomPropertyTypesView, generics.RetrieveDestroyAPIView):
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.devicetype_set.count() == 0:
            self.perform_destroy(instance)
            thread.start_new_thread(update_configs_on_servers, (self, "PROPERTY_TYPES"))
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

#
############ VALUE TYPES #########
### SCALARS ###
class CustomScalarView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = ScalarValueTypeSerializer
    renderer_classes = [JSONRenderer,]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return ScalarValueType.objects.filter(user=None)|ScalarValueType.objects.filter(user=user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            if data["name"] in [s.name for s in ScalarValueType.objects.filter(user=None)]:
                raise serializers.ValidationError({"name":\
                                                    ["core scalar with this name already exists."]})
        except KeyError:
            raise serializers.ValidationError({"name":["This field is required"]})
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["scalar with this name already exists."]})

class ScalarListView(CustomScalarView, generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"scalars":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            thread.start_new_thread(update_configs_on_servers, (self, "SCALAR_TYPES"))
            return redirect("scalartypesAPI")
        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class ScalarDetailView(CustomScalarView, generics.RetrieveDestroyAPIView):
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if PropertyType.objects.filter(user=self.request.user, value_type_class="SCALAR", value_type_id=instance.id).count() == 0:
            self.perform_destroy(instance)
            thread.start_new_thread(update_configs_on_servers, (self, "SCALAR_TYPES"))
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
#
### ENUMS ###
class CustomEnumView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = EnumValueTypeSerializer
    renderer_classes = [JSONRenderer,]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return EnumValueType.objects.filter(user=None)|EnumValueType.objects.filter(user=user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            if data["name"] in [en.name for en in EnumValueType.objects.filter(user=None)]:
                raise serializers.ValidationError({"name":\
                                                    ["core enumerated with this name already exists."]})
        except KeyError:
            raise serializers.ValidationError({"name":["This field is required"]})
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["enumerated with this name already exists."]})

class EnumListView(CustomEnumView, generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"enums":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            thread.start_new_thread(update_configs_on_servers, (self, "ENUM_TYPES"))
            return redirect("enumtypesAPI")
        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class EnumDetailView(CustomEnumView, generics.RetrieveDestroyAPIView):
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if PropertyType.objects.filter(user=self.request.user, value_type_class="ENUM", value_type_id=instance.id).count() == 0:
            self.perform_destroy(instance)
            thread.start_new_thread(update_configs_on_servers, (self, "ENUM_TYPES"))
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
#
#
### CHOICES ###
class CustomChoicesView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = ChoiceSerializer
    renderer_classes = [JSONRenderer,]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Choice.objects.filter(user=None)|Choice.objects.filter(user=user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            if data["name"] in [c.name for c in Choice.objects.filter(user=None)]:
                raise serializers.ValidationError({"name":\
                                                    ["core choice with this name already exists."]})
        except KeyError:
            raise serializers.ValidationError({"name":["This field is required"]})
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["choice with this name already exists."]})

class ChoiceListView(CustomChoicesView, generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"choices":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return redirect("choicesAPI")
        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class ChoiceDetailView(CustomChoicesView, generics.RetrieveDestroyAPIView):
    #all come from generics.RetrieveUpdateDestroyAPIView
    def delete(self, request, *args, **kwargs): 
        instance = self.get_object()
        if instance.enumvaluetype_set.count() == 0:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)