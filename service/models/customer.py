from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField()
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=100, blank=True)
    primary_contact = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.customer.name}"

    class Meta:
        ordering = ['-primary_contact', 'name']
