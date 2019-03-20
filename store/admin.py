from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Store

# Register your models here.

#admin.site.register(Store)

@admin.register(Store)
class StoreAdmin(ImportExportModelAdmin):
    pass