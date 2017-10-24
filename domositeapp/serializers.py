from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from domositeapp.models import *

class HouseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    area_count = serializers.ReadOnlyField()
    class Meta:
        model = House
        fields = ("id", "name", "server", "user", "area_count")

class HousePresentSerializer(HouseSerializer):
    server = serializers.ReadOnlyField(source="server.name")

class AreaSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    division_count = serializers.ReadOnlyField()
    class Meta:
        model = Area
        fields = ("id", "name", "order", "house", "user", "division_count")

class AreaPresentSerializer(AreaSerializer):
    house = serializers.ReadOnlyField(source="house.name")

class DivisionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    device_count = serializers.ReadOnlyField()
    class Meta:
        model = Division
        fields = ("id", "name", "area", "user", "device_count")

class DivisionPresentSerializer(DivisionSerializer):
    area = serializers.ReadOnlyField(source="area.name")


class DeviceSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    class Meta:
        model = Device
        fields = ("id", "name", "server", "address", "division", "services",\
                    "local_id", "device_type", "state", "user", "active", "timeout")

class DevicePresentSerializer(DeviceSerializer):
    server = serializers.ReadOnlyField(source="server.name")
    device_type = serializers.ReadOnlyField(source="device_type.name")
    division = serializers.ReadOnlyField(source="division.name")

class ServerSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    multicast = serializers.BooleanField(required=True)
    device_count = serializers.ReadOnlyField()

    class Meta:
        model = Server
        fields = ("id", "name", "coap_address", "coap_port", "proxy_address", "proxy_port",\
                    "multicast", "user", "active", "device_count", "timeout")

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "name")

class CustomServiceSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    device_count = serializers.ReadOnlyField()
    class Meta:
        model = CustomService
        fields = ("id", "name", "user", "core_service_ref", "device_count")

#
### DEVICE MODELING SERIALIZERS ###
class DeviceTypeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    class Meta:
        model = DeviceType
        fields = ("id", "name", "properties", "user")

class PropertyTypeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    class Meta:
        model = PropertyType
        fields = ("id", "name", "access_mode", "value_type_class", "value_type_id", "user")

    def validate_value_type_id(self, value):
        if self.initial_data["value_type_class"] == self.Meta.model.SCALAR:
            if value not in [ele.id for ele in ScalarValueType.objects.all()]:
                raise serializers.ValidationError("The SCALAR value type with ID "+\
                                                            str(value)+" does not exist")
        elif self.initial_data["value_type_class"] == self.Meta.model.ENUM:
            if value not in [ele.id for ele in EnumValueType.objects.all()]:
                raise serializers.ValidationError("The ENUM value type with ID "+\
                                                            str(value)+" does not exist")
        else:
            raise serializers.ValidationError("The Value_Type_Class does not exist")
        return value


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ("id", "name", "value")

class ScalarValueTypeSerializer(serializers.ModelSerializer):

    default_value = serializers.FloatField(required=True)

    min_value = serializers.FloatField(required=True)
    max_value = serializers.FloatField(required=True)
    step = serializers.FloatField(required=True)

    user = serializers.ReadOnlyField(source="user.username")
    class Meta:
        model = ScalarValueType
        fields = ("id", "name", "units", "default_value", "min_value", "max_value", "step", "user")

    def validate_default_value(self, value):
        if (value < self.initial_data["min_value"]) or (value > self.initial_data["max_value"]):
            raise serializers.ValidationError("The default value must be a value between min_value and max_value")
        return value

    def validate_step(self, value):
        if (value < 0) or (value > self.initial_data["max_value"]):
            raise serializers.ValidationError("The step value must be a positive number smaller than max_value")
        return value

    def validate(self, data):
        if data["min_value"] > data["max_value"]:
            raise serializers.ValidationError("The default value must be a value between min_value and max_value")
        return data

class EnumValueTypeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    class Meta:
        model = EnumValueType
        fields = ("id", "name", "choices", "default_value", "user")

    def validate(self, data):
        if data["default_value"] not in [c for c in data["choices"]]:
            raise serializers.ValidationError("The default value must be in choices")
        return data

class ChoiceSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    class Meta:
        model = Choice
        fields = ("id", "name", "value", "user")
#
### CHANGES HISTORY SERIALIZERS ###
class PropertyChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyChange
        fields = ("id", "new_state", "source", "timestamp")

class LogActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogAction
        fields = ("id", "action", "description", "timestamp", "instance_class", "instance_id")



