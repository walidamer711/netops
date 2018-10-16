# Generated by Django 2.0.8 on 2018-09-25 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='item_status',
            field=models.CharField(choices=[('PJ', 'Project'), ('ST', 'Stock')], default='ST', max_length=1000),
        ),
    ]