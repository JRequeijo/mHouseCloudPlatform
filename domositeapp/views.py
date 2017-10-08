from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.contrib.auth.mixins import LoginRequiredMixin

from domositeapp.models import *
from rest_framework.response import Response
from domositeapp.serializers import *
from rest_framework import generics, mixins
from domositeapp.forms import HouseCreationForm, AreaCreationForm
from rest_framework import status
from rest_framework import serializers
from rest_framework import permissions
from rest_framework import exceptions
from domositeapp import permissions as custom_perm
import json
from django.core.exceptions import ValidationError

from domositeapp import permissions as custom_perm

from domositeapp.renderers import CustomHTMLRenderer
from webapp.models import AccountSettings
from webapp.serializers import AccountSettingsSerializer

from datetime import datetime
##DASH MAIN VIEW####
class Dashboard(LoginRequiredMixin, APIView):

    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./overview.html"

    def get(self, request, format=None):
        setts = AccountSettings.objects.get(user=request.user)

        data = {}
        if setts.present_history_on_dash:
            log = LogAction.objects.filter(user=request.user).order_by("-timestamp")
            serializer = LogActionSerializer(log, many=True)
            data["log"] = serializer.data[:20]

        if setts.present_analytics_on_dash:
            data["analytics"] = True
            n_actions_per_time = []

            n_actions_per_time.append(LogAction.objects.filter(user=self.request.user,\
                                                                timestamp__range=(datetime.now()-timedelta(minutes=120), datetime.now()-timedelta(minutes=115))).count())
            i = 110
            while i != 0:
                n_actions_per_time.append(LogAction.objects.filter(user=self.request.user,\
                                                                    timestamp__range=(datetime.now()-timedelta(minutes=i+5), datetime.now()-timedelta(minutes=i-5))).count())
                i-=10
            
            n_actions_per_time.append(LogAction.objects.filter(user=self.request.user,\
                                                                    timestamp__range=(datetime.now()-timedelta(minutes=5), datetime.now())).count())
            data["n_actions_per_time"] = n_actions_per_time

        return Response(data)

class MainHistory(LoginRequiredMixin, APIView):

    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./history.html"

    def get(self, request, format=None):
        log = LogAction.objects.filter(user=request.user).order_by("-timestamp")
        serializer = LogActionSerializer(log, many=True)
        return Response({"log":serializer.data})

class MainHistoryJSON(APIView):
    permission_classes = (permissions.IsAuthenticated, custom_perm.IsOwner,)
    renderer_classes = [JSONRenderer,]

    def get_history_records(self, start=None, end=None,\
                            action_id=None, action=None, instance_class=None,\
                            instance_id=None, nb_results=20):

        if start is None:
            start = timezone.now()-timedelta(days=730000)

        if end is None:
            end = timezone.now()
        
        if action_id is None:
            if action is None:
                if instance_class is None:
                    if instance_id is None:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    else:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            instance_id=instance_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    
                else:
                    if instance_id is None:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            instance_class=instance_class,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    else:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            instance_class=instance_class,\
                                            instance_id=instance_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
            else:
                if instance_class is None:
                    if instance_id is None:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            action=action,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    else:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            action=action,\
                                            instance_id=instance_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    
                else:
                    if instance_id is None:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            action=action,\
                                            instance_class=instance_class,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    else:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            action=action,\
                                            instance_class=instance_class,\
                                            instance_id=instance_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
        else:
            if action is None:
                if instance_class is None:
                    if instance_id is None:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            id=action_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    else:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            id=action_id,\
                                            instance_id=instance_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    
                else:
                    if instance_id is None:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            id=action_id,\
                                            instance_class=instance_class,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    else:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            id=action_id,\
                                            instance_class=instance_class,\
                                            instance_id=instance_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
            else:
                if instance_class is None:
                    if instance_id is None:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            id=action_id,\
                                            action=action,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    else:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            id=action_id,\
                                            action=action,\
                                            instance_id=instance_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    
                else:
                    if instance_id is None:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            id=action_id,\
                                            action=action,\
                                            instance_class=instance_class,\
                                            timestamp__range=(start, end)).order_by("-timestamp")
                    else:
                        log = LogAction.objects.filter(user=self.request.user,\
                                            id=action_id,\
                                            action=action,\
                                            instance_class=instance_class,\
                                            instance_id=instance_id,\
                                            timestamp__range=(start, end)).order_by("-timestamp")

        if nb_results:
            serializer = LogActionSerializer(log[:nb_results], many=True)
        else:
            serializer = LogActionSerializer(log, many=True)
        
        return serializer.data

    def get(self, request, format=None):
        try:
            start = request.GET["start"]
        except:
            start = None

        try:
            end = request.GET["end"]
        except:
            end = None

        try:
            action_id = request.GET["id"]
            action_id = int(action_id)
        except:
            action_id = None

        try:
            action = request.GET["action"]
        except:
            action = None

        try:
            instance_class = request.GET["instance_class"]
        except:
            instance_class = None
        
        try:
            instance_id = request.GET["instance_id"]
        except:
            instance_id = None

        try:
            limit = request.GET["limit"]
            limit = int(limit)
        except:
            limit = None

        try:
            hist_data = self.get_history_records(start=start, end=end,\
                                                action_id=action_id, action=action,\
                                                instance_class=instance_class,\
                                                instance_id=instance_id, nb_results=limit)
            return Response(hist_data)
        except ValidationError as err:
            return Response({"detail":err.message}, status=status.HTTP_400_BAD_REQUEST)

class MyAccountSettings(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):

    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./settings.html"
    serializer_class = AccountSettingsSerializer

    def get_object(self):
        return AccountSettings.objects.get(user=self.request.user)

    def get(self, request, *args, **kwargs):
        resp = self.retrieve(request, *args, **kwargs)
        return Response({"settings":resp.data}, status=resp.status_code)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"info":"Account Successfully Deleted"}, status=status.HTTP_200_OK)

class Analytics(LoginRequiredMixin, APIView):

    renderer_classes = [CustomHTMLRenderer,]
    template_name = "./analytics.html"

    def get(self, request, *args, **kwargs):
        n_actions_per_time = []

        n_actions_per_time.append(LogAction.objects.filter(user=self.request.user,\
                                                            timestamp__range=(datetime.now()-timedelta(minutes=120), datetime.now()-timedelta(minutes=115))).count())
        i = 110
        while i != 0:
            n_actions_per_time.append(LogAction.objects.filter(user=self.request.user,\
                                                                timestamp__range=(datetime.now()-timedelta(minutes=i+5), datetime.now()-timedelta(minutes=i-5))).count())
            i-=10
        
        n_actions_per_time.append(LogAction.objects.filter(user=self.request.user,\
                                                                timestamp__range=(datetime.now()-timedelta(minutes=5), datetime.now())).count())

        n_devices = LogAction.objects.filter(user=self.request.user, instance_class=LogAction.DEVICE).count()
        n_servers = LogAction.objects.filter(user=self.request.user, instance_class=LogAction.SERVER).count()
        n_houses = LogAction.objects.filter(user=self.request.user, instance_class=LogAction.HOUSE).count()
        n_areas = LogAction.objects.filter(user=self.request.user, instance_class=LogAction.AREA).count()
        n_divisions = LogAction.objects.filter(user=self.request.user, instance_class=LogAction.DIVISION).count()
        n_services = LogAction.objects.filter(user=self.request.user, instance_class=LogAction.SERVICE).count()

        n_create = LogAction.objects.filter(user=self.request.user, action=LogAction.CREATE).count()
        n_read = LogAction.objects.filter(user=self.request.user, action=LogAction.READ).count()
        n_update = LogAction.objects.filter(user=self.request.user, action=LogAction.UPDATE).count()
        n_delete = LogAction.objects.filter(user=self.request.user, action=LogAction.DELETE).count()
        n_error = LogAction.objects.filter(user=self.request.user, action=LogAction.ERROR).count()
        n_down = LogAction.objects.filter(user=self.request.user, action=LogAction.STAT_DOWN).count()
        n_up = LogAction.objects.filter(user=self.request.user, action=LogAction.STAT_UP).count()

        return Response({"n_actions_per_time":n_actions_per_time,\
                         "n_devices":n_devices,\
                         "n_server":n_servers,\
                         "n_houses":n_houses,
                         "n_areas":n_areas,
                         "n_divisions":n_divisions,\
                         "n_services":n_services,\
                         "n_create":n_create,\
                         "n_read":n_read,\
                         "n_update":n_update,
                         "n_delete":n_delete,
                         "n_error":n_error,
                         "n_down":n_down,
                         "n_up":n_up})
       