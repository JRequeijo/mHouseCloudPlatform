
from django.conf.urls import url
from helpapp import views


urlpatterns = [
    url(r"^$", views.RenderView, 
                {"template_name":"./help.html"}, name="helpMain"),
             
]
