# Generated by Django 4.1.5 on 2023-01-04 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_password_given',
            field=models.BooleanField(default=False),
        ),
    ]
