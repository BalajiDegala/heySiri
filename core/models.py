from django.db import models


class UserSession(models.Model):
    name = models.CharField(max_length=100)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    overview = models.TextField(blank=True)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Finding(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="findings", null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    code_snippet = models.TextField(blank=True)
    code_language = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.title


class FindingComment(models.Model):
    finding = models.ForeignKey(Finding, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.created_by} comment"


class ActivityLog(models.Model):
    user_name = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.action}"
