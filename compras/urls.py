from django.urls import path
from . import views

urlpatterns = [
    path('', views.compras, name='compras'),
    path('<str:orden>/', views.orden, name='orden'),
]
