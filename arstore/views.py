from django.shortcuts import render

def index(request):
    template = 'dashboard.html'
    context = {}
    return render(request, template, context)