from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ticket(models.Model):
    TYPE_CHOICES = [('technical','Technical'), ('non-technical','Non-Technical')]
    STATUS_CHOICES = [('open','Open'), ('in_progress','In Progress'), ('closed','Closed')]

    student       = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    type          = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text          = models.TextField()
    ai_category   = models.CharField(max_length=50, blank=True)
    ai_is_technical = models.BooleanField(default=False)
    ai_record_id  = models.CharField(max_length=64, blank=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.pk} {self.type} ({self.status})"
