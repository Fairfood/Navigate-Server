# Generated by Django 4.0.4 on 2024-05-17 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_theme_badge_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intervention',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='intervention_images'),
        ),
    ]
