from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('webhook/new', views.webhookProduct, name='webhookProductNew'), #/catalogo/webhook/new
    path('webhook/update', views.webhookProduct, name='webhookProductUpdate'), #/catalogo/webhook/update
]
