# Generated by Django 4.0.4 on 2022-08-31 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_alter_game_current_round_alter_round_round_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='won',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='won_description',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]