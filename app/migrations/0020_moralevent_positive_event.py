# Generated by Django 4.0.4 on 2022-08-18 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_moralevent_moral_max_reset_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='moralevent',
            name='positive_event',
            field=models.BooleanField(default=False),
        ),
    ]
