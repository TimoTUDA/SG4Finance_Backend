# Generated by Django 4.0.4 on 2022-09-08 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_game_won_game_won_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='morals',
            name='freetime_max',
            field=models.IntegerField(default=200),
        ),
        migrations.AlterField(
            model_name='morals',
            name='health_max',
            field=models.IntegerField(default=300),
        ),
        migrations.AlterField(
            model_name='morals',
            name='housing_max',
            field=models.IntegerField(default=900),
        ),
    ]