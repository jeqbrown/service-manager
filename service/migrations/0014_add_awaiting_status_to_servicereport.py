from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('service', '0013_alter_entitlement_instrument_alter_entitlement_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicereport',
            name='approval_status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('in_progress', 'In Progress'),
                    ('awaiting', 'Awaiting Approval'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected')
                ],
                default='draft',
                max_length=20
            ),
        ),
    ]
