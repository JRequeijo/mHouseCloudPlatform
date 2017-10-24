
from django.db.models import Count
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import permissions, serializers, generics
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from domositeapp import permissions as custom_perm
from domositeapp.renderers import CustomHTMLRenderer
from domositeapp.models import Area, LogAction
from domositeapp.serializers import AreaSerializer, AreaPresentSerializer, DivisionPresentSerializer
from domositeapp.forms import AreaCreationForm

class CustomAreasView():
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    serializer_class = AreaSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Area.objects.filter(user=user).annotate(division_count=Count("division__id"))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        act = LogAction(action=LogAction.CREATE,\
                        description="Created new Area with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.AREA,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

        act = LogAction(action=LogAction.UPDATE,\
                        description="Updated Area with ID "+str(serializer.data["id"]),\
                        instance_class=LogAction.AREA,\
                        instance_id=int(serializer.data["id"]),\
                        user=self.request.user)
        act.save()
    
    def perform_destroy(self, instance):
        id_str = str(instance.id)
        instance.delete()

        act = LogAction(action=LogAction.DELETE,\
                        description="Deleted Area with ID "+id_str,\
                        instance_class=LogAction.AREA,\
                        instance_id=int(id_str),\
                        user=self.request.user)
        act.save()

#
#### HTML VIEWS ####
class ListHTMLView(CustomAreasView, LoginRequiredMixin, generics.ListAPIView):
    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./areas/areas.html"
    serializer_class = AreaPresentSerializer

    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        form = AreaCreationForm(user=self.request.user)
        return Response({"form": form, "areas":resp.data}, status=resp.status_code)

class DetailHTMLView(CustomAreasView, LoginRequiredMixin, generics.RetrieveAPIView):
    renderer_classes = [CustomHTMLRenderer, ]
    template_name = "./areas/areaDetail.html"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        divisions = DivisionPresentSerializer(instance.division_set.all().annotate(device_count=Count("device__id")), many=True)

        form = AreaCreationForm(user=self.request.user, initial=serializer.data)
        return Response({"form": form, "ele":serializer.data, "divisions":divisions.data})
#
### API VIEWS ####
class ListJSONView(CustomAreasView, generics.ListCreateAPIView):
    renderer_classes = [JSONRenderer,]

    def get(self, request, *args, **kwargs):
        try:
            house_id = request.GET["house"]
            resp_q = Area.objects.filter(house=int(house_id))
            resp = AreaPresentSerializer(resp_q, many=True)
            return Response({"areas":resp.data})
        except:
            pass

        resp = self.list(request, *args, **kwargs)
        return Response({"areas":resp.data}, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return redirect("areasAPI")
        except serializers.ValidationError as err:
            return Response(err.detail,status=err.status_code)

class DetailJSONView(CustomAreasView, generics.RetrieveUpdateDestroyAPIView):
    #all come from generics.RetrieveUpdateDestroyAPIView
    renderer_classes = [JSONRenderer,]
    pass