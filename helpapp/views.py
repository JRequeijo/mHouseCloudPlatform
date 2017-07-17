from django.shortcuts import render

def RenderView(request, template_name):
    return render(request, template_name)

