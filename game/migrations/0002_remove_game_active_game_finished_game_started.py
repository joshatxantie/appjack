# Generated by Django 4.2 on 2023-04-17 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='active',
        ),
        migrations.AddField(
            model_name='game',
            name='finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='started',
            field=models.BooleanField(default=False),
        ),
    ]
