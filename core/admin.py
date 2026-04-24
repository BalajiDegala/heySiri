from django.contrib import admin

from .models import ActivityLog, Finding, FindingComment, Topic, UserSession


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
    search_fields = ("name", "created_by")


class FindingCommentInline(admin.TabularInline):
    model = FindingComment
    extra = 0
    fields = ("created_by", "content", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "created_by", "created_at", "has_file", "has_code")
    list_filter = ("topic", "created_by", "created_at")
    search_fields = ("title", "content", "created_by", "topic__name", "code_snippet")
    readonly_fields = ("created_at",)
    inlines = (FindingCommentInline,)

    @admin.display(boolean=True, description="File")
    def has_file(self, obj):
        return bool(obj.file)

    @admin.display(boolean=True, description="Code")
    def has_code(self, obj):
        return bool(obj.code_snippet)


@admin.register(FindingComment)
class FindingCommentAdmin(admin.ModelAdmin):
    list_display = ("finding", "created_by", "created_at")
    list_filter = ("created_by", "created_at")
    search_fields = ("content", "created_by", "finding__title", "finding__topic__name")
    readonly_fields = ("created_at",)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user_name", "action", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("user_name", "action", "details")
    readonly_fields = ("timestamp",)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "login_time", "logout_time")
    search_fields = ("name",)
