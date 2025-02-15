from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('service', '0009_alter_entitlement_instrument_alter_workorder_status'),  # Replace this with your actual previous migration name
    ]

    operations = [
        migrations.AddField(
            model_name='workorder',
            name='description',
            field=models.TextField(blank=True, help_text='Description of the work to be performed'),
        ),
    ]
