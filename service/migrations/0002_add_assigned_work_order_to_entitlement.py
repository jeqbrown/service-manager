from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),  # Now correctly pointing to the initial migration
    ]

    operations = [
        migrations.AddField(
            model_name='entitlement',
            name='assigned_work_order',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_entitlement',
                to='service.workorder'
            ),
        ),
    ]