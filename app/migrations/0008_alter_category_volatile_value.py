# Generated by Django 4.0.4 on 2022-06-30 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_category_volatile_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='volatile_value',
            field=models.FloatField(default=0.1),
        ),
    ]
