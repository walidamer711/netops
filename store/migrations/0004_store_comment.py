# Generated by Django 2.1.1 on 2019-03-20 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20190320_0841'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='comment',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]