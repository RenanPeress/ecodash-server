import secrets
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CollectorToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='collector_token')
    token = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token de {self.user.username}"


class Analise(models.Model):
    GRADES = [('AAA', 'AAA'), ('AA', 'AA'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analises')
    software_name = models.CharField(max_length=255)
    sci_score = models.FloatField()
    grade = models.CharField(max_length=3, choices=GRADES)
    energy_kwh = models.FloatField()
    region = models.CharField(max_length=10)
    hardware_type = models.CharField(max_length=20)
    payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.software_name} [{self.grade}] — {self.user.username}"
