from __future__ import unicode_literals

from django.db import models
from webapp.models import User

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from datetime import timedelta
from django.utils import timezone

import json
import requests

class Server(models.Model):
    name = models.CharField(max_length=20)
    coap_address = models.GenericIPAddressField()
    coap_port = models.IntegerField(blank=False, null=False)

    proxy_address = models.GenericIPAddressField()
    proxy_port = models.IntegerField(blank=False, null=False)

    multicast = models.BooleanField(blank=False, null=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)


    active = models.BooleanField(default=True)
    last_access = models.DateTimeField(auto_now_add=True)

    timeout = models.IntegerField(blank=False, null=False)

    class Meta:
        unique_together = (("coap_address", "user"),)
    
    def state(self):
        if timezone.now() >= self.last_access + timedelta(seconds=self.timeout):
            last_active = self.active
            self.active = False
            self.save()
            if not self.active and last_active:
                act = LogAction(action=LogAction.STAT_DOWN,\
                                description="Server with ID "+str(self.id)+" is Down",\
                                instance_class=LogAction.SERVER,\
                                instance_id=int(self.id),\
                                user=self.user)
                act.save()

class House(models.Model):

    name = models.CharField(max_length=20)

    server = models.OneToOneField(Server, on_delete=models.SET_NULL, null=True, blank=True)

    user = models.ForeignKey(User, related_name="houses", on_delete=models.CASCADE, editable=False)

    class Meta:
        unique_together = (("name", "user"), ("server","user"))

class Area(models.Model):
    name = models.CharField(max_length=20)
    order = models.IntegerField()

    house = models.ForeignKey(House, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    class Meta:
        unique_together = (("name", "house"),)

class Division(models.Model):
    name = models.CharField(max_length=20)

    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    class Meta:
        unique_together = (("name", "area"),)

class Device(models.Model):

    name = models.CharField(max_length=20)
    address = models.GenericIPAddressField()

    local_id = models.IntegerField()

    device_type = models.ForeignKey("DeviceType", on_delete=models.PROTECT)

    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)

    services = models.ManyToManyField("CustomService", blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    active = models.BooleanField(default=True)
    last_access = models.DateTimeField(auto_now_add=True)

    timeout = models.IntegerField(blank=False, null=False)

    def save(self, *args, **kwargs):
        if not self.id:
            super(Device, self).save(*args, **kwargs) # Call the "real" save() method.
            if self.device_type:
                for p in self.device_type.properties.all():
                    prop = Property(related_device=self, property_type=p)
                    prop.save()
        else:
            super(Device, self).save(*args, **kwargs) # Call the "real" save() method.
            if self.device_type and not self.property_set.all():
                for p in self.device_type.properties.all():
                    prop = Property(related_device=self, property_type=p)
                    prop.save()

    @property
    def properties(self):
        prop = {}
        for p in self.property_set.all():
            prop[p.name] = p.value

        return prop

    @property
    def state(self):
        prop = {}
        for p in self.property_set.all():
            prop[p.name] = p.value

        if timezone.now() >= self.last_access + timedelta(seconds=self.timeout):
            last_active = self.active
            self.active = False
            self.save()
            if not self.active and last_active:
                act = LogAction(action=LogAction.STAT_DOWN,\
                                description="Device with ID "+str(self.id)+" is Down",\
                                instance_class=LogAction.DEVICE,\
                                instance_id=int(self.id),\
                                user=self.user)
                act.save()

        if self.active:
            status = "running"
        else:
            status = "down"
        return {"status":status, "state":prop, "device_id":self.local_id}

    class Meta:
        unique_together = (("address", "server"),)

#### DEVICE MODELING #####
class DeviceType(models.Model):
    name = models.CharField(max_length=30)
    properties = models.ManyToManyField("PropertyType")

    user = models.ForeignKey(User, related_name="devicetypes", on_delete=models.CASCADE,\
                                editable=False, null=True, blank=True)

    class Meta:
        unique_together = (("name", "user"),)

class PropertyType(models.Model):
    READONLY = "RO"
    WRITEONLY = "WO"
    READWRITE = "RW"
    ACCESS_MODES = ((READONLY, "RO"), (WRITEONLY, "WO"), (READWRITE, "RW"))


    SCALAR = "SCALAR"
    ENUM = "ENUM"
    VALUE_TYPES = ((SCALAR, "Scalar"), (ENUM, "Enumerated"))

    name = models.CharField(max_length=20)
    access_mode = models.CharField(max_length=2, choices=ACCESS_MODES, default=READONLY)

    value_type_class = models.CharField(max_length=4, choices=VALUE_TYPES)
    value_type_id = models.IntegerField()

    user = models.ForeignKey(User, related_name="propertytypes", on_delete=models.CASCADE,\
                                editable=False, null=True, blank=True)

    class Meta:
        unique_together = (("name", "user"),)

    @property
    def value_type(self):
        if self.value_type_class == self.SCALAR:
            return ScalarValueType.objects.get(id=self.value_type_id)
        elif self.value_type_class == self.ENUM:
            return EnumValueType.objects.get(id=self.value_type_id)

class Property(models.Model):
    related_device = models.ForeignKey(Device, on_delete=models.CASCADE)
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)

    name = models.CharField(max_length=20)
    value = models.CharField(max_length=20)

    class Meta:
        unique_together = (("related_device", "property_type"),)

    def save(self, *args, **kwargs):
        super(Property, self).save(*args, **kwargs) # Call the "real" save() method.
        self.name = self.property_type.name

        if not self.value and isinstance(self.property_type.value_type, ScalarValueType):
            self.value = self.property_type.value_type.default_value
        elif not self.value and isinstance(self.property_type.value_type, EnumValueType):
            self.value = self.property_type.value_type.default_value.name

        super(Property, self).save(*args, **kwargs) # Call the "real" save() method.    

class ScalarValueType(models.Model):
    name = models.CharField(max_length=20)
    units = models.CharField(max_length=10)

    default_value = models.FloatField(default=0)

    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=0)
    step = models.FloatField(default=0)

    user = models.ForeignKey(User, related_name="scalarvaluetypes", on_delete=models.CASCADE,\
                                editable=False, null=True, blank=True)

    class Meta:
        unique_together = (("name", "user"),)

class EnumValueType(models.Model):
    name = models.CharField(max_length=30)
    choices = models.ManyToManyField("Choice")

    default_value = models.ForeignKey("Choice", related_name="+")

    user = models.ForeignKey(User, related_name="enumvaluetypes", on_delete=models.CASCADE,\
                                editable=False, null=True, blank=True)

    class Meta:
        unique_together = (("name", "user"),)

class Choice(models.Model):
    name = models.CharField(max_length=20)
    value = models.CharField(max_length=20)

    user = models.ForeignKey(User, related_name="enumchoices", on_delete=models.CASCADE,\
                                editable=False, null=True, blank=True)

    class Meta:
        unique_together = (("name", "user"),)

class Service(models.Model):
    name = models.CharField(max_length=30)

class CustomService(models.Model):
    name = models.CharField(max_length=30, null=True)

    core_service_ref = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)

    user = models.ForeignKey(User, related_name="services", on_delete=models.CASCADE,\
                                editable=False)

    class Meta:
        unique_together = (("name", "user"),)

#
### LOGGING CHANGES ###
class PropertyChange(models.Model):

    CLOUD = "CLOUD"
    DEVICE = "DEVICE"
    SOURCES = ((CLOUD, "CLOUD"), (DEVICE, "DEVICE"))

    device_id = models.ForeignKey(Device, on_delete=models.DO_NOTHING)
    new_state_text = models.TextField()

    source = models.CharField(max_length=6, choices=SOURCES)
    timestamp = models.DateTimeField(auto_now=True)

    @property
    def new_state(self):
        state = json.loads(json.dumps(self.new_state_text))
        # print state
        return state

class LogAction(models.Model):

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    READ = "READ"
    DELETE = "DELETE"
    ERROR = "ERROR"
    STAT_DOWN = "STATUS DOWN"
    STAT_UP = "STATUS UP"

    ACTIONS = ((CREATE, "CREATE"), (UPDATE, "UPDATE"),\
                (READ, "READ"), (DELETE, "DELETE"), (ERROR, "ERROR"),\
                (STAT_DOWN, "STATUS DOWN"), (STAT_UP, "STATUS UP"))

    HOUSE = "HOUSE"
    AREA = "AREA"
    DIVISION = "DIVISION"
    SERVER = "SERVER"
    DEVICE = "DEVICE"
    SERVICE = "SERVICE"

    INST_CLASSES = ((HOUSE, "HOUSE"), (AREA, "AREA"), (DIVISION, "DIVISION"), (SERVER, "SERVER"), (DEVICE, "DEVICE"), (SERVICE, "SERVICE"))

    action = models.CharField(max_length=15, choices=ACTIONS)
    description = models.TextField()

    instance_class = models.CharField(max_length=10, choices=INST_CLASSES)
    instance_id = models.IntegerField()

    timestamp = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
