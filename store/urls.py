from django.urls import path

from . import views

urlpatterns = [
    path('', views.StoreList.as_view(), name='store'),
    path('newitem', views.ItemCreate.as_view(), name='new_item'),
]