# Generated by Django 4.0.4 on 2022-07-25 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_remove_event_round_duration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='market_reset',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='roundinvestment',
            name='market_reset',
            field=models.BooleanField(default=False),
        ),
    ]
