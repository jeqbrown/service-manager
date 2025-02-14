from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('service', 'PREVIOUS_MIGRATION'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicereport',
            name='work_order',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='service_reports',
                to='service.workorder'
            ),
        ),
    ]