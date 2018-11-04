from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('show', views.show, name='show'),
    path('services', views.services, name='services'),
    path('net_view/<str:view>', views.network_views, name='net_view'),
    path('check_view/<str:check>', views.checks_view, name='check_view'),
]