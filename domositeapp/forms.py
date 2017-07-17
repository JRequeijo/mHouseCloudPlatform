from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, \
    PasswordResetForm, SetPasswordForm
from django.utils.translation import ugettext, ugettext_lazy as _

from domositeapp.models import *
from domositeapp.serializers import *
from django.forms import ModelForm
from django import forms
from django.forms.models import fields_for_model

class HouseCreationForm(ModelForm):

    class Meta:
        model = House
        fields = ["name", "server"]

    aux = fields_for_model(House)
    name = aux["name"]

    name.label =_("House name")
    name.widget.attrs.update({"class":"form-control", "autofocus":""})

    def __init__(self, user, *args, **kwargs):
        super(HouseCreationForm, self).__init__(*args, **kwargs)
        self.fields["server"].widget.attrs.update({"class":"form-control"})
        self.fields["server"].choices = [("","--------")]
        self.fields["server"].choices.extend([(s.id, s.name) for s in Server.objects.filter(user=user)])


class AreaCreationForm(ModelForm):

    class Meta:
        model = Area
        fields = ["name", "order", "house"]


    aux = fields_for_model(Area)
    name = aux["name"]
    order = aux["order"]
    house = aux["house"]

    name.label =_("Area name")
    name.widget.attrs.update({"class":"form-control", "autofocus":""})

    order.widget.attrs.update({"class":"form-control"})
    house.widget.attrs.update({"class":"form-control"})

    house.choices = [("","--------")]
    
    def __init__(self, user, *args, **kwargs):
        super(AreaCreationForm, self).__init__(*args, **kwargs)
        self.fields["house"].choices = [("","--------")]
        self.fields["house"].choices.extend([(h.id, h.name) for h in House.objects.filter(user=user)])


class DivisionCreationForm(ModelForm):

    class Meta:
        model = Division
        fields = ["name", "area"]


    aux = fields_for_model(Division)
    name = aux["name"]
    area = aux["area"]

    name.label =_("Division name")
    name.widget.attrs.update({"class":"form-control", "autofocus":""})

    area.widget.attrs.update({"class":"form-control"})

    area.choices = [("","--------")]
    
    def __init__(self, user, *args, **kwargs):
        super(DivisionCreationForm, self).__init__(*args, **kwargs)
        self.fields["area"].choices = [("","--------")]
        self.fields["area"].choices.extend([(a.id, a.name) for a in Area.objects.filter(user=user)])


class DeviceCreationForm(ModelForm):

    class Meta:
        model = Device
        fields = ["name", "division", "services"]

    aux = fields_for_model(Device)
    name = aux["name"]
    division = aux["division"]
    services = aux["services"]

    name.label =_("Device name")
    name.widget.attrs.update({"class":"form-control"})

    division.widget.attrs.update({"class":"form-control"})
    services.widget.attrs.update({"class":"form-control"})

    def __init__(self, user, *args, **kwargs):
        super(DeviceCreationForm, self).__init__(*args, **kwargs)
        self.fields["division"].choices = [("","--------")]

        try:
            dev_id = kwargs["initial"]["id"]
            device = Device.objects.get(id=dev_id)

            divs = Division.objects.filter(area__house__server=device.server)
            self.fields["division"].choices.extend([(d.id, d.name) for d in divs])
            self.initial["division"] = device.division
        except:
            pass

        self.fields["services"].choices = [("","--------")]
        servs = CustomService.objects.filter(user=user)
        self.fields["services"].choices.extend([(s.id, s.name) for s in servs])

class ServerCreationForm(ModelForm):

    class Meta:
        model = Server
        fields = ["name"]

    aux = fields_for_model(Server)
    name = aux["name"]

    name.label = _("Server name")
    name.widget.attrs.update({"class":"form-control", "autofocus":""})

class ServiceCreationForm(ModelForm):

    class Meta:
        model = CustomService
        fields = ["name", "core_service_ref"]

    aux = fields_for_model(CustomService)
    name = aux["name"]

    name.label =_("Service name")
    name.widget.attrs.update({"class":"form-control", "autofocus":""})

    def __init__(self, *args, **kwargs):
        super(ServiceCreationForm, self).__init__(*args, **kwargs)
        self.fields["core_service_ref"].label =_("Service Core Reference")
        self.fields["core_service_ref"].widget.attrs.update({"class":"form-control", "onchange":"addNameAuto(this)"})
        self.fields["core_service_ref"].choices = [("","--------")]
        self.fields["core_service_ref"].choices.extend([(s.id, s.name) for s in Service.objects.all()])


#
#### DEVICE MODELING FORMS ####
class DeviceTypeCreationForm(ModelForm):

    class Meta:
        model = DeviceType
        fields = ["name", "properties"]

    def __init__(self, user, *args, **kwargs):
        super(DeviceTypeCreationForm, self).__init__(*args, **kwargs)
        self.fields["name"].label =_("Device Type Name")
        self.fields["name"].widget.attrs.update({"class":"form-control", "autofocus":""})
        self.fields["properties"].label =_("Device Properties")
        self.fields["properties"].widget.attrs.update({"class":"form-control"})
        self.fields["properties"].choices = []
        self.fields["properties"].choices.extend([(p.id, str(p.id)+" - "+p.name)\
         for p in PropertyType.objects.filter(user=None)|PropertyType.objects.filter(user=user)])

class PropertyTypeCreationForm(ModelForm):

    class Meta:
        model = PropertyType
        fields = ["name", "access_mode", "value_type_class", "value_type_id"]

    def __init__(self, *args, **kwargs):
        super(PropertyTypeCreationForm, self).__init__(*args, **kwargs)
        self.fields["name"].label =_("Property Type Name")
        self.fields["name"].widget.attrs.update({"class":"form-control", "autofocus":""})
        self.fields["access_mode"].label =_("Property Type Access Mode")
        self.fields["access_mode"].widget.attrs.update({"class":"form-control"})
        self.fields["value_type_class"].label =_("Property Value Type Class")
        self.fields["value_type_class"].widget.attrs.update({"class":"form-control"})
        self.fields["value_type_id"].label =_("Property Value Type ID")
        self.fields["value_type_id"].widget.attrs.update({"class":"form-control"})

class ScalarCreationForm(ModelForm):

    class Meta:
        model = ScalarValueType
        fields = ["name", "units", "min_value", "max_value", "default_value", "step"]

    def __init__(self, *args, **kwargs):
        super(ScalarCreationForm, self).__init__(*args, **kwargs)
        self.fields["name"].label =_("Scalar Name")
        self.fields["name"].widget.attrs.update({"class":"form-control", "autofocus":""})
        self.fields["units"].label =_("Scalar Units")
        self.fields["units"].widget.attrs.update({"class":"form-control"})
        self.fields["min_value"].label =_("Scalar Minimum Value")
        self.fields["min_value"].widget.attrs.update({"class":"form-control"})
        self.fields["max_value"].label =_("Scalar Maximum Value")
        self.fields["max_value"].widget.attrs.update({"class":"form-control"})
        self.fields["default_value"].label =_("Scalar Default Value")
        self.fields["default_value"].widget.attrs.update({"class":"form-control"})
        self.fields["step"].label =_("Scalar Step Value")
        self.fields["step"].widget.attrs.update({"class":"form-control"})

class EnumCreationForm(ModelForm):

    class Meta:
        model = EnumValueType
        fields = ["name", "choices"]

    default_value = forms.TypedChoiceField()
    default_value.label =_("Default Value")
    default_value.widget.attrs.update({"class":"form-control", "id":"id_enum_def_val"})

    def __init__(self, user, *args, **kwargs):
        super(EnumCreationForm, self).__init__(*args, **kwargs)
        self.fields["name"].label =_("Enumerated Name")
        self.fields["name"].widget.attrs.update({"class":"form-control", "autofocus":""})
        self.fields["choices"].label =_("Enumerated Choices")
        self.fields["choices"].widget.attrs.update({"class":"form-control", 
                                                    "onchange":"actualizeDefaultValues(this)"})
        self.fields["choices"].choices = []
        self.fields["choices"].choices.extend([(c.id, str(c.id)+" - "+c.name)\
         for c in Choice.objects.filter(user=None)|Choice.objects.filter(user=user)])

class ChoiceCreationForm(ModelForm):

    class Meta:
        model = Choice
        fields = ["name", "value"]

    def __init__(self, *args, **kwargs):
        super(ChoiceCreationForm, self).__init__(*args, **kwargs)
        self.fields["name"].label =_("Choice Name")
        self.fields["name"].widget.attrs.update({"class":"form-control", "autofocus":""})
        self.fields["value"].label =_("Choice Value")
        self.fields["value"].widget.attrs.update({"class":"form-control"})


class ScalarTypeForm(forms.Form):
    scalar_setter = forms.CharField(label="prop_name", max_length=100,\
                                        widget=forms.TextInput(attrs={"class":"form-control"}))
    def __init__(self, property_obj, *args, **kwargs):
        super(ScalarTypeForm, self).__init__(*args, **kwargs)
        self.fields["scalar_setter"].label = property_obj.name
        self.fields["scalar_setter"].widget.attrs["id"] = "property-"+str(property_obj.name)

        if property_obj.property_type.access_mode == PropertyType.READONLY:
            self.fields["scalar_setter"].widget.attrs["readonly"] = True


class EnumTypeForm(forms.Form):
    enum_setter = forms.ChoiceField(label="prop_name",\
                                        widget=forms.RadioSelect(attrs={"class":"radio-setter"}))
    def __init__(self, property_obj, *args, **kwargs):
        super(EnumTypeForm, self).__init__(*args, **kwargs)
        self.fields["enum_setter"].label = property_obj.name
        self.fields["enum_setter"].widget.attrs["id"] = "property-"+str(property_obj.name)
        self.fields["enum_setter"].widget.attrs["onclick"] = "updateEnumProperty('"+str(property_obj.name)+"', this.value, '"+str(property_obj.related_device.id)+"'); blockPropertySetterInpts(true)"

        q = EnumValueType.objects.get(id=property_obj.property_type.value_type_id).choices.all()
        self.fields["enum_setter"].choices = []
        self.fields["enum_setter"].choices.extend([(c.name, c.name) for c in q])
        self.initial["enum_setter"] = EnumValueType.objects.get(id=property_obj.property_type.value_type_id).default_value.name