from django.urls import path
from . import views

urlpatterns = [
    path('', views.compras, name='compras'),
    path('<str:idOrden>/', views.orden, name='orden'),
    path('webhook/new', views.webhookOrderPaid, name='webhookOrderPaid'), #/compras/webhook/new
]
