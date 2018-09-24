from django.urls import path

from . import views

urlpatterns = [
    path('list', views.ProjectList.as_view(), name='projects'),
    path('newproject', views.ProjectCreate.as_view(), name='new_project'),
    path('project/<int:project_id>', views.TaskList.as_view(), name='project'),
    path('project/<int:project_id>/newtask', views.TaskCreate.as_view(), name='new_task'),
    path('project/<int:project_id>/task/<int:task_id>', views.TaskUpdate.as_view(), name='task_update'),
    path('project/<int:project_id>/task/<int:task_id>/delete', views.TaskDelete.as_view(), name='task_delete'),
]