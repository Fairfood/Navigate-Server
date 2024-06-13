# Generated by Django 4.0.4 on 2024-06-13 06:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0005_alter_farmer_supply_chains'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='supply_chain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batches', to='supply_chains.supplychain'),
        ),
        migrations.AlterField(
            model_name='company',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
