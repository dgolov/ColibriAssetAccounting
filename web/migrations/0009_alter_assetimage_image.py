# Generated by Django 4.1.7 on 2023-05-25 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_remove_history_location_remove_history_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetimage',
            name='image',
            field=models.ImageField(upload_to='images/assets', verbose_name='Изображенеие'),
        ),
    ]