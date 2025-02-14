# Generated by Django 5.1.5 on 2025-02-05 23:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('address', models.TextField()),
                ('website', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EntitlementType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='InstrumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('role', models.CharField(blank=True, max_length=100)),
                ('primary_contact', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='service.customer')),
            ],
            options={
                'ordering': ['-primary_contact', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=50, unique=True)),
                ('installation_date', models.DateField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instruments', to='service.customer')),
                ('instrument_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='service.instrumenttype')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('draft', 'Draft')], default='draft', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agreements', to='service.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Entitlement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_visits', models.PositiveIntegerField(default=0)),
                ('used_visits', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('entitlement_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='service.entitlementtype')),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.instrument')),
                ('agreement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entitlements', to='service.serviceagreement')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='open', max_length=20)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.customer')),
                ('entitlement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='service.entitlement')),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.instrument')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_date', models.DateField()),
                ('findings', models.TextField()),
                ('actions_taken', models.TextField()),
                ('approval_status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('approval_date', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_reports', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.customer')),
                ('technician', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('work_order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='service_report', to='service.workorder')),
            ],
        ),
    ]
