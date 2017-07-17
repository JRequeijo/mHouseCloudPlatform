
from django.conf.urls import url
from domositeapp import views
from domositeapp.cstm_views import houseviews as h_views
from domositeapp.cstm_views import areaviews as a_views
from domositeapp.cstm_views import divisionviews as d_views
from domositeapp.cstm_views import deviceviews as dev_views
from domositeapp.cstm_views import serverviews as server_views
from domositeapp.cstm_views import serviceviews as service_views
from domositeapp.cstm_views import configviews as conf_views

import thread 

urlpatterns = [
    url(r"^dashboard/$", views.Dashboard.as_view(), name="dashboard"),
    url(r"^history/$", views.MainHistory.as_view(), name="history"),
    url(r"^settings/$", views.MyAccountSettings.as_view(), name="settings"),
    url(r"^analytics/$", views.Analytics.as_view(), name="analytics"),

    url(r"^houses/$", h_views.ListHTMLView.as_view(), name="houses"),
    url(r"^houses/(?P<pk>[0-9]+)/$", h_views.DetailHTMLView.as_view(), name="houseDetail"),

    url(r"^areas/$", a_views.ListHTMLView.as_view(), name="areas"),
    url(r"^areas/(?P<pk>[0-9]+)/$", a_views.DetailHTMLView.as_view(), name="areaDetail"),

    url(r"^divisions/$", d_views.ListHTMLView.as_view(), name="divisions"),
    url(r"^divisions/(?P<pk>[0-9]+)/$", d_views.DetailHTMLView.as_view(), name="divisionDetail"),

    url(r"^servers/$", server_views.ListHTMLView.as_view(), name="servers"),
    url(r"^servers/(?P<pk>[0-9]+)/$", server_views.DetailHTMLView.as_view(), name="serverDetail"),

    url(r"^devices/$", dev_views.ListHTMLView.as_view(), name="devices"),
    url(r"^devices/(?P<pk>[0-9]+)/$", dev_views.DetailHTMLView.as_view(), name="deviceDetail"),

    url(r"^services/$", service_views.ListHTMLView.as_view(), name="services"),
    url(r"^services/(?P<pk>[0-9]+)/$", service_views.DetailHTMLView.as_view(), name="serviceDetail"),

    url(r"^configs/$", conf_views.ConfigsHTMLView.as_view(), name="configs"),

    url(r"^api/configs/$", conf_views.ConfigsJSONView.as_view(), name="configsAPI"),

    url(r"^api/configs/device_types/$", conf_views.DeviceTypesListView.as_view(),\
                                                                name="devicetypesAPI"),
    url(r"^api/configs/device_types/(?P<pk>[0-9]+)/$", conf_views.DeviceTypesDetailView.as_view(),\
                                                                name="devicetypesDetailAPI"),

    url(r"^api/configs/property_types/$", conf_views.PropertyTypesListView.as_view(),\
                                                                name="propertytypesAPI"),
    url(r"^api/configs/property_types/(?P<pk>[0-9]+)/$",\
                                          conf_views.PropertyTypesDetailView.as_view(),\
                                                                name="propertytypesDetailAPI"),

    url(r"^api/configs/scalars/$", conf_views.ScalarListView.as_view(),\
                                                                name="scalartypesAPI"),
    url(r"^api/configs/scalars/(?P<pk>[0-9]+)/$",\
                                          conf_views.ScalarDetailView.as_view(),\
                                                                name="scalartypesDetailAPI"),

    url(r"^api/configs/enums/$", conf_views.EnumListView.as_view(),\
                                                                name="enumtypesAPI"),
    url(r"^api/configs/enums/(?P<pk>[0-9]+)/$",\
                                          conf_views.EnumDetailView.as_view(),\
                                                                name="enumtypesDetailAPI"),

    url(r"^api/configs/choices/$", conf_views.ChoiceListView.as_view(),\
                                                                name="choicesAPI"),
    url(r"^api/configs/choices/(?P<pk>[0-9]+)/$",\
                                          conf_views.ChoiceDetailView.as_view(),\
                                                                name="choicesDetailAPI"),


    url(r"^api/houses/$", h_views.ListJSONView.as_view(), name="housesAPI"),
    url(r"^api/houses/(?P<pk>[0-9]+)/$", h_views.DetailJSONView.as_view(), name="houseDetailAPI"),

    url(r"^api/areas/$", a_views.ListJSONView.as_view(), name="areasAPI"),
    url(r"^api/areas/(?P<pk>[0-9]+)/$", a_views.DetailJSONView.as_view(), name="areaDetailAPI"),

    url(r"^api/divisions/$", d_views.ListJSONView.as_view(), name="divisionsAPI"),
    url(r"^api/divisions/(?P<pk>[0-9]+)/$", d_views.DetailJSONView.as_view(), name="divisionDetailAPI"),
    url(r"^api/divisions/(?P<pk>[0-9]+)/devices/$", d_views.DivisionDevicesJSONView.as_view(), name="divisionDevicesAPI"),


    url(r"^api/services/$", service_views.ListJSONView.as_view(), name="servicesAPI"),
    url(r"^api/services/(?P<pk>[0-9]+)/$", service_views.DetailJSONView.as_view(), name="serviceDetailAPI"),
    url(r"^api/services/(?P<pk>[0-9]+)/devices/$", service_views.ServiceDevicesJSONView.as_view(), name="serviceDevicesAPI"),


    url(r"^api/servers/$", server_views.ListJSONView.as_view(), name="serversAPI"),
    url(r"^api/servers/(?P<pk>[0-9]+)/$", server_views.DetailJSONView.as_view(), name="serverDetailAPI"),
    url(r"^api/servers/(?P<pk>[0-9]+)/state/$", server_views.StateJSONView.as_view(), name="serverStateAPI"),
    url(r"^api/servers/(?P<pk>[0-9]+)/devices/$", server_views.ServerDevicesJSONView.as_view(), name="serverDevicesAPI"),

    url(r"^api/devices/$", dev_views.ListJSONView.as_view(), name="devicesAPI"),
    url(r"^api/devices/(?P<pk>[0-9]+)/$", dev_views.DetailJSONView.as_view(), name="deviceDetailAPI"),
    url(r"^api/devices/(?P<pk>[0-9]+)/state/$", dev_views.StateJSONView.as_view(), name="deviceStateAPI"),
    url(r"^api/devices/(?P<pk>[0-9]+)/history/$", dev_views.ChangesHistoryJSONView.as_view(), name="deviceHistoryAPI"),

    url(r"^api/history/$", views.MainHistoryJSON.as_view(), name="historyAPI"),
]


thread.start_new_thread(server_views.periodic_state_check, ())
thread.start_new_thread(dev_views.periodic_state_check, ())
