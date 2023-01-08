# Generated by Django 4.1.5 on 2023-01-09 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_stablediffusionimagegeneration_image_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='LanguageTranslation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('message_id', models.CharField(max_length=100)),
                ('source_text', models.TextField(blank=True)),
                ('source_language', models.CharField(max_length=2)),
                ('destination_text', models.TextField(blank=True)),
                ('destination_language', models.CharField(max_length=2)),
                ('confidence', models.DecimalField(decimal_places=2, max_digits=2)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]