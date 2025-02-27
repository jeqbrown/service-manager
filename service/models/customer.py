from django.db import models
from .base import TrackingModel

class Customer(TrackingModel):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

class Contact(TrackingModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.role}) - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            Contact.objects.filter(
                customer=self.customer,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        elif not self.pk and not Contact.objects.filter(customer=self.customer).exists():
            self.is_primary = True
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-is_primary', 'name']
