from django.db import models


class UserSession(models.Model):
    name = models.CharField(max_length=100)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Sprint(models.Model):
    name = models.CharField(max_length=100)
    goal = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SprintItem(models.Model):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

    STATUS_CHOICES = [
        (TODO, "Todo"),
        (IN_PROGRESS, "In Progress"),
        (REVIEW, "Review"),
        (DONE, "Done"),
    ]

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    PRIORITY_CHOICES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
        (CRITICAL, "Critical"),
    ]

    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assignee = models.CharField(max_length=100, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=MEDIUM)
    story_points = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TODO)
    blocked = models.BooleanField(default=False)
    blocker_reason = models.TextField(blank=True)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "-blocked", "-priority", "-created_at"]

    def __str__(self):
        return self.title


class StandupUpdate(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name="standups")
    user_name = models.CharField(max_length=100)
    yesterday = models.TextField(blank=True)
    today = models.TextField(blank=True)
    blockers = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_name} standup"


class Blocker(models.Model):
    OPEN = "open"
    WATCHING = "watching"
    RESOLVED = "resolved"

    STATUS_CHOICES = [
        (OPEN, "Open"),
        (WATCHING, "Watching"),
        (RESOLVED, "Resolved"),
    ]

    sprint_item = models.ForeignKey(SprintItem, on_delete=models.CASCADE, related_name="blockers")
    owner = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "-created_at"]

    def __str__(self):
        return f"{self.sprint_item.title} - {self.get_status_display()}"


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    week = models.CharField(max_length=20)

    def __str__(self):
        return self.title


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
    linked_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
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
