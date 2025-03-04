# Generated by Django 5.1.6 on 2025-02-16 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0016_instrument_assigned_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceagreement',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='serviceagreement',
            name='po_number',
            field=models.CharField(blank=True, help_text='Purchase Order or Credit Card Number', max_length=50, verbose_name='PO/CC Number'),
        ),
        migrations.AlterField(
            model_name='serviceagreement',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='draft', max_length=20),
        ),
    ]
