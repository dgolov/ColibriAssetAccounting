# Generated by Django 4.1.7 on 2023-05-21 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_alter_asset_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='location',
            name='city',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Город'),
        ),
    ]