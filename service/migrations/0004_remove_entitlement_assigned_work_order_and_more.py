# Generated by Django 5.1.5 on 2025-02-14 03:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_alter_workorder_entitlement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entitlement',
            name='assigned_work_order',
        ),
        migrations.RemoveField(
            model_name='entitlement',
            name='used_visits',
        ),
    ]
