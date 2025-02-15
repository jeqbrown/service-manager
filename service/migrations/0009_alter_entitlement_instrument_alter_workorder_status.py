# Generated by Django 5.1.6 on 2025-02-14 20:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0008_alter_workorder_instrument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entitlement',
            name='instrument',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.instrument'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('open', 'Open'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='draft', max_length=20),
        ),
    ]
