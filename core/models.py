from django.db import models

class UserSession(models.Model):
    name = models.CharField(max_length=100)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    week = models.CharField(max_length=20)

    def __str__(self):
        return self.title
class Finding(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    linked_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return self.title


class ActivityLog(models.Model):
    user_name = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.action}"