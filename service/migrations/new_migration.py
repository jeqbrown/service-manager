from django.db import migrations, models

def set_primary_contacts(apps, schema_editor):
    Contact = apps.get_model('service', 'Contact')
    Customer = apps.get_model('service', 'Customer')
    
    for customer in Customer.objects.all():
        first_contact = customer.contacts.first()
        if first_contact:
            first_contact.is_primary = True
            first_contact.save()

def reverse_primary_contacts(apps, schema_editor):
    Contact = apps.get_model('service', 'Contact')
    Contact.objects.all().update(is_primary=False)

class Migration(migrations.Migration):
    dependencies = [
        ('service', '0018_merge_20250226_0222'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='is_primary',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            set_primary_contacts,
            reverse_primary_contacts
        ),
    ]
