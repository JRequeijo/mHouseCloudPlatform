from django.contrib.auth import authenticate, login, forms
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.decorators import renderer_classes, api_view
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from webapp.forms import RegisterUserForm
from webapp.models import User, AccountSettings


@api_view(["GET"])
@renderer_classes((TemplateHTMLRenderer,))
def homepage(request, format=None):
    return render(request,'home.html')

class HelpView(APIView):
    renderer_classes = [TemplateHTMLRenderer,]
    def get(self, request, format=None):
        return render(request, "help.html")


class AboutView(APIView):
    renderer_classes = [TemplateHTMLRenderer,]
    def get(self, request, format=None):
        return render(request, "about.html")

class Register(APIView):

    renderer_classes = [TemplateHTMLRenderer,]

    def get(self, request, format=None):
        form = RegisterUserForm()
        return render(request, 'register.html', {"form":form})

    def post(self, request, format=None):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            email = request.POST["email"]
            password = request.POST["password1"]

            setts = AccountSettings()
            setts.save()
            user = User.objects.create_user(email, password, account_settings=setts)

            login(request, user)

            return redirect('dashboard')
        else:
            return render(request, 'register.html', {"form":form})

