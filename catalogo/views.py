from django.shortcuts import render

def catalogo(request):
    template = 'catalogo/catalogo.html'
    context = {}
    return render(request, template, context)