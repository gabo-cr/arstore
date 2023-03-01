from django.shortcuts import render

def compras(request):
    template = 'compras/compras.html'
    context = {}
    return render(request, template, context)

def orden(request, orden):
    template = 'compras/orden.html'
    context = {
        'orden': orden
    }
    return render(request, template, context)