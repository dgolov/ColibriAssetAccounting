# Generated by Django 4.1.7 on 2023-04-30 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_alter_asset_options_asset_auto_update_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='phone',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Номер телефона'),
        ),
    ]