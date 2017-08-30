
from django.db.models import Count
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import permissions, serializers, generics
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from domositeapp import permissions as custom_perm
from domositeapp.renderers import CustomHTMLRenderer
from domositeapp.models import Division, LogAction
from domositeapp.serializers import DivisionSerializer, DivisionPresentSerializer, DevicePresentSerializer
from domositeapp.forms import DivisionCreationForm

class CustomDivisionsView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = DivisionSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Division.objects.filter(user=user).annotate(device_count=Count("device__id"))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        act = LogAction(action=LogAction.CREATE,\
                        description="Created new Division with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.DIVISION,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        act = LogAction(action=LogAction.UPDATE,\
                        description="Updated Division with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.DIVISION,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_destroy(self, instance):
        id_str = str(instance.id)
        instance.delete()

        act = LogAction(action=LogAction.DELETE,\
                        description="Deleted Division with ID "+id_str,\
                        instance_class=LogAction.DIVISION,\
                        instance_id=int(id_str),\
                        user=self.request.user)
        act.save()

#
### HTML VIEWS ###
class ListHTMLView(CustomDivisionsView, LoginRequiredMixin, generics.ListAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./divisions/divisions.html"
    serializer_class = DivisionPresentSerializer

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        form = DivisionCreationForm(user=self.request.user)
        return Response({"form": form, "divisions":resp.data}, status=resp.status_code)


class DetailHTMLView(CustomDivisionsView, LoginRequiredMixin, generics.RetrieveAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./divisions/divisionDetail.html"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        devices = DevicePresentSerializer(instance.device_set, many=True)

        form = DivisionCreationForm(user=self.request.user, initial=serializer.data)
        return Response({"form": form, "ele":serializer.data, "devices":devices.data})

#
### API VIEWS ####
class ListJSONView(CustomDivisionsView, generics.ListCreateAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        try:
            house_id = request.GET["house"]
            resp_q = Division.objects.filter(area__house=int(house_id))
            resp = DivisionPresentSerializer(resp_q, many=True)
            return Response({"divisions":resp.data})
        except:
            pass

        try:
            area_id = request.GET["area"]
            resp_q = Division.objects.filter(area=int(area_id))
            resp = DivisionPresentSerializer(resp_q, many=True)
            return Response({"divisions":resp.data})
        except:
            pass
        resp = self.list(request, *args, **kwargs)
        return Response({"divisions":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return redirect("divisionsAPI")
        except serializers.ValidationError as err:
            return Response(err.detail,status=err.status_code)

class DetailJSONView(CustomDivisionsView, generics.RetrieveUpdateDestroyAPIView):
    #all come from generics.RetrieveUpdateDestroyAPIView
    renderer_classes = [JSONRenderer,]
    pass

class DivisionDevicesJSONView(CustomDivisionsView, generics.GenericAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        division = self.get_object()
        resp = division.device_set.all()
        resp = DevicePresentSerializer(resp, many=True)
        for d in resp.data:
            d.pop("division")
            d.pop("state")
        data = {"devices":resp.data}
        return Response(data)