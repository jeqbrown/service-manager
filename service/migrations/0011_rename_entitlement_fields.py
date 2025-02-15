from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('service', '0010_add_description_to_workorder'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entitlement',
            old_name='total_visits',
            new_name='total',
        ),
    ]
