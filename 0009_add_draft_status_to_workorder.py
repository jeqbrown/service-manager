from django.db import migrations, models

def forward_func(apps, schema_editor):
    WorkOrder = apps.get_model('service', 'WorkOrder')
    # Set any existing work orders without entitlements to draft status
    WorkOrder.objects.filter(entitlement__isnull=True).update(status='draft')

class Migration(migrations.Migration):

    dependencies = [
        ('service', 'previous_migration'),  # Replace with actual previous migration
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('open', 'Open'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed')
                ],
                default='draft',
                max_length=20
            ),
        ),
        migrations.RunPython(forward_func, migrations.RunPython.noop),
    ]