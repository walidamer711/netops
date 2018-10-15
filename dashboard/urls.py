from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('show', views.show, name='show'),
    path('services', views.services, name='services'),
]