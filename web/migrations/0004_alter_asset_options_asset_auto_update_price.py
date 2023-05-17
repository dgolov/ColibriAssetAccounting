# Generated by Django 4.1.7 on 2023-04-30 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_asset_is_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asset',
            options={'verbose_name': 'Актив', 'verbose_name_plural': 'Активы'},
        ),
        migrations.AddField(
            model_name='asset',
            name='auto_update_price',
            field=models.BooleanField(default=False, verbose_name='Автообновление стоимости'),
        ),
    ]