from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=200)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=50)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.name} - {self.customer}"