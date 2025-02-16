# Generated by Django 5.1.6 on 2025-02-15 19:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0014_add_awaiting_status_to_servicereport'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicereport',
            name='technician',
        ),
        migrations.AddField(
            model_name='servicereport',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='created_service_reports', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
