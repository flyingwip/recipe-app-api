# Generated by Django 2.1.15 on 2020-05-16 12:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_recipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='time',
            new_name='time_minutes',
        ),
    ]