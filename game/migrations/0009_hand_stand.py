# Generated by Django 4.2 on 2023-04-17 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_hand_current_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='hand',
            name='stand',
            field=models.BooleanField(default=False),
        ),
    ]
