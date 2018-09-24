from django.contrib import admin

# Register your models here.
from .models import Projects, Tasks

admin.site.register(Projects)
admin.site.register(Tasks)