# Generated by Django 4.1.5 on 2023-01-07 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_usertokenbalance_max_token_per_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertokenbalance',
            name='image_size',
            field=models.PositiveIntegerField(default=256),
        ),
        migrations.AddField(
            model_name='usertokenbalance',
            name='number_of_image',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
