# Generated by Django 4.1.7 on 2023-09-30 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0018_asset_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='ozon_slug',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Ссылка на ozon'),
        ),
    ]