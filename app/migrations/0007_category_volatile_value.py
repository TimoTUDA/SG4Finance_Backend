# Generated by Django 4.0.4 on 2022-06-30 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_roundinvestment_asset_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='volatile_value',
            field=models.IntegerField(default=1),
        ),
    ]
