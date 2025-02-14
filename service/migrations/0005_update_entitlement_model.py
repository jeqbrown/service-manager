from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_remove_entitlement_assigned_work_order_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entitlement',
            name='instrument',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entitlements', to='service.instrument'),
        ),
    ]