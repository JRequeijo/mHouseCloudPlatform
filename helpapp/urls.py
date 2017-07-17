
from django.conf.urls import url
from helpapp import views


urlpatterns = [
    url(r"^$", views.RenderView, 
                {"template_name":"./help.html"}, name="helpMain"),
    
    #Cloud Platform
    url(r"^cloudplatform/$",  views.RenderView, 
                        {"template_name":"./cloud_platform/main.html"}, name="cloudplatformMain"),
    
    #Home Server
    url(r"^homeserver/$",  views.RenderView, 
                        {"template_name":"./home_server/main.html"}, name="homeserverMain"),
    
    #Endpoints Network
    url(r"^endpoints/$",  views.RenderView, 
                        {"template_name":"./endpoints/main.html"}, name="endpointsMain"),
                        
    #api
    url(r"^api/$",  views.RenderView, 
                        {"template_name":"./api/main.html"}, name="apiMainHelp"),
    url(r"^api/cloud/$", views.RenderView, 
                        {"template_name":"./api/cloud/main.html"} ,name="cloudAPImain"),
    url(r"^api/hs/http/$", views.RenderView, 
                        {"template_name":"./api/hs_http/main.html"}, name="hsHTTPAPImain"),
    url(r"^api/hs/coap/$", views.RenderView, 
                        {"template_name":"./api/hs_coap/main.html"}, name="hsCOAPAPImain"),
    
    #cloud API URIs
    #configuration related URIs
    url(r"^api/cloud/configslist/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/configsList.html"}, name="configsList"),
    url(r"^api/cloud/devicetypeslist/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/deviceTypesList.html"}, name="deviceTypesList"),
    url(r"^api/cloud/devicetypesdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/deviceTypesDetail.html"}, name="deviceTypesDetail"),
    url(r"^api/cloud/propertytypeslist/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/propTypesList.html"}, name="propTypesList"),
    url(r"^api/cloud/propertytypesdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/propTypesDetail.html"}, name="propTypesDetail"),
    url(r"^api/cloud/scalarslist/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/scalarsList.html"}, name="scalarsList"),
    url(r"^api/cloud/scalarsdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/scalarsDetail.html"}, name="scalarsDetail"),
    url(r"^api/cloud/enumslist/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/enumsList.html"}, name="enumsList"),
    url(r"^api/cloud/enumsdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/enumsDetail.html"}, name="enumsDetail"),
    url(r"^api/cloud/choiceslist/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/choicesList.html"}, name="choicesList"),
    url(r"^api/cloud/choicesdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/configs/choicesDetail.html"}, name="choicesDetail"),
    
    #space related URIs
    url(r"^api/cloud/houseslist/$", views.RenderView, 
                {"template_name":"./api/cloud/spaces/housesList.html"}, name="housesList"),
    url(r"^api/cloud/housesdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/spaces/housesDetail.html"}, name="housesDetail"),
    url(r"^api/cloud/areaslist/$", views.RenderView, 
                {"template_name":"./api/cloud/spaces/areasList.html"}, name="areasList"),
    url(r"^api/cloud/areasdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/spaces/areasDetail.html"}, name="areasDetail"),
    url(r"^api/cloud/divisionslist/$", views.RenderView, 
                {"template_name":"./api/cloud/spaces/divisionsList.html"}, name="divisionsList"),
    url(r"^api/cloud/divisionsdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/spaces/divisionsDetail.html"}, name="divisionsDetail"),
    url(r"^api/cloud/divisiondevices/$", views.RenderView, 
                {"template_name":"./api/cloud/spaces/divisionDevices.html"}, name="divisionDevices"),
    
    #service related URIs
    url(r"^api/cloud/serviceslist/$", views.RenderView, 
                {"template_name":"./api/cloud/services/servicesList.html"}, name="servicesList"),
    url(r"^api/cloud/servicesdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/services/servicesDetail.html"}, name="servicesDetail"),
    url(r"^api/cloud/servicedevices/$", views.RenderView, 
                {"template_name":"./api/cloud/services/serviceDevices.html"}, name="serviceDevices"),
    
    #servers and devices related URIs
    url(r"^api/cloud/serverslist/$", views.RenderView, 
                {"template_name":"./api/cloud/servers/serversList.html"}, name="serversList"),
    url(r"^api/cloud/serversdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/servers/serversDetail.html"}, name="serversDetail"),
    url(r"^api/cloud/serverdevices/$", views.RenderView, 
                {"template_name":"./api/cloud/servers/serverDevices.html"}, name="serverDevices"),
    url(r"^api/cloud/serverstate/$", views.RenderView, 
                {"template_name":"./api/cloud/servers/serverState.html"}, name="serverState"),
    
    url(r"^api/cloud/deviceslist/$", views.RenderView, 
                {"template_name":"./api/cloud/devices/devicesList.html"}, name="devicesList"),
    url(r"^api/cloud/devicesdetail/$", views.RenderView, 
                {"template_name":"./api/cloud/devices/devicesDetail.html"}, name="devicesDetail"),
    url(r"^api/cloud/devicestate/$", views.RenderView, 
                {"template_name":"./api/cloud/devices/deviceState.html"}, name="deviceState"),
    url(r"^api/cloud/devicehistory/$", views.RenderView, 
                {"template_name":"./api/cloud/devices/deviceHistory.html"}, name="deviceHistory"),
    
    #actions history related URIs
    url(r"^api/cloud/actionshistory/$", views.RenderView, 
                {"template_name":"./api/cloud/actionsHistory.html"}, name="actionsHistory"),
                
]
