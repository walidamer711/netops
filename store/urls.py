from django.urls import path

from . import views


urlpatterns = [
    path('<str:item_type>', views.StoreList.as_view(), name='store'),
    path('<str:item_type>/newitem', views.ItemCreate.as_view(), name='new_item'),
    path('<str:item_type>/<int:item_id>', views.ItemUpdate.as_view(), name='item_update'),
]