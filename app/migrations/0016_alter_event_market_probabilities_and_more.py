# Generated by Django 4.0.4 on 2022-07-25 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_alter_event_market_reset_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='market_probabilities',
            field=models.CharField(default='0/30/10/60/0', max_length=20),
        ),
        migrations.AlterField(
            model_name='roundinvestment',
            name='market_probabilities',
            field=models.CharField(default='0/30/10/60/0', max_length=20),
        ),
    ]
