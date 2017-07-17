from django.conf.urls import url
from django.contrib.auth import views as auth_views
from rest_framework.urlpatterns import format_suffix_patterns

from webapp import views
from webapp.forms import LoginForm, PassRecverForm, NewPassSetForm


urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^help/$', views.HelpView.as_view(), name='help'),

    url(r'^register/$', views.Register.as_view(), name='register'),

    url(r'^login/$', auth_views.login,
        {"template_name":"login.html",
         "authentication_form":LoginForm,
         "redirect_authenticated_user":True},
        name='login'),

    url(r'^logout/$', auth_views.logout,
        {"template_name":"login.html"},
        name='logout'),

    url(r'^passrecv/$', auth_views.password_reset,\
        {"post_reset_redirect":"passrecv_emailsent",
         "template_name":"pass_recv/password_recover.html",
         "email_template_name":"pass_recv/password_reset_email.html",
         "html_email_template_name":"pass_recv/password_reset_email.html",
         "password_reset_form":PassRecverForm}, name="passrecv"),

    url(r'^passrecv/emailsent/$', auth_views.password_reset_done,
        {"template_name":"pass_recv/email_sent_status.html"}, name="passrecv_emailsent"),

    url(r'^passrecv/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$',\
        auth_views.password_reset_confirm,\
        {"template_name":"pass_recv/password_reset.html",
         "set_password_form": NewPassSetForm,
         "post_reset_redirect":"passrecv_success"}, name='passrecv_confirm'),

    url(r'^passrecv/success/$',\
        auth_views.password_reset_complete,\
        {"template_name":"pass_recv/password_reset_status.html"}, name='passrecv_success'),

]

urlpatterns = format_suffix_patterns(urlpatterns)