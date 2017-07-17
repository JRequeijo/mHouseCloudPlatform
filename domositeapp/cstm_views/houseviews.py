
from django.shortcuts import redirect
from django.db import IntegrityError
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import permissions, serializers, generics
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from domositeapp import permissions as custom_perm
from domositeapp.renderers import CustomHTMLRenderer
from domositeapp.models import House, LogAction
from domositeapp.serializers import HouseSerializer, HousePresentSerializer, AreaPresentSerializer
from domositeapp.forms import HouseCreationForm

class CustomHousesView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = HouseSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return House.objects.filter(user=user).annotate(area_count=Count("area__id"))

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["house with this name already exists."]})

        act = LogAction(action=LogAction.CREATE,\
                        description="Created new House with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.HOUSE,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"name":\
                                                ["house with this name already exists."]})

        act = LogAction(action=LogAction.UPDATE,\
                        description="Updated House with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.HOUSE,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_destroy(self, instance):
        id_str = str(instance.id)
        instance.delete()

        act = LogAction(action=LogAction.DELETE,\
                        description="Deleted House with ID "+id_str,\
                        instance_class=LogAction.HOUSE,\
                        instance_id=int(id_str),\
                        user=self.request.user)
        act.save()
#
### HTML VIEWS ###
class ListHTMLView(CustomHousesView, LoginRequiredMixin, generics.ListAPIView):

    renderer_classes = [CustomHTMLRenderer, ]
    template_name = "./houses/houses.html"
    serializer_class = HousePresentSerializer

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        form = HouseCreationForm(user=self.request.user)
        return Response({"form":form, "houses":resp.data}, status=resp.status_code)

class DetailHTMLView(CustomHousesView, LoginRequiredMixin, generics.RetrieveAPIView):
    renderer_classes = [CustomHTMLRenderer, ]
    template_name = "./houses/houseDetail.html"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        areas = AreaPresentSerializer(instance.area_set.all().annotate(division_count=Count("division__id")), many=True)

        form = HouseCreationForm(user=self.request.user, initial=serializer.data)
        return Response({"form": form, "ele":serializer.data, "areas":areas.data})

#
### API VIEWS ###
class ListJSONView(CustomHousesView, generics.ListCreateAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        return Response({"houses":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return redirect("housesAPI")
        except serializers.ValidationError as err:
            return Response(err.detail, status=err.status_code)

class DetailJSONView(CustomHousesView, generics.RetrieveUpdateDestroyAPIView):
    #all come from generics.RetrieveUpdateDestroyAPIView
    pass
