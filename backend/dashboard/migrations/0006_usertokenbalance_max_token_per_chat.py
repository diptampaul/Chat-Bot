# Generated by Django 4.1.5 on 2023-01-06 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_tokenusage_remaining_tokens_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertokenbalance',
            name='max_token_per_chat',
            field=models.PositiveIntegerField(default=1000),
        ),
    ]