import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = 'netops.settings'
django.setup()
from store.models import Store

for obj in Store.objects.all():
    print(obj.item_model)