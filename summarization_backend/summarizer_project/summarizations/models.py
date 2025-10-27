from django.db import models

class Summary(models.Model):
    user_id = models.IntegerField(null=True, blank=True) # ✅ Auth Service user ID
    title = models.CharField(max_length=255)
    original_text = models.TextField()
    summary_text = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
