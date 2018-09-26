from django.urls import path

from . import views

app_name = 'stores'
urlpatterns = [
    path('<str:item_type>', views.StoreList.as_view(), name='store'),
    path('<str:item_type>/newitem', views.ItemCreate.as_view(), name='new_item'),
]