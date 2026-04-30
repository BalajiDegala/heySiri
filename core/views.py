from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import (
    ActivityLog,
    Finding,
    FindingComment,
    Topic,
    UserSession,
)

PASSWORD = "pipeline"  # change this


def current_user(request):
    return request.session.get('user') or "Guest"


def delete_finding_file(finding):
    if finding.file:
        finding.file.delete(save=False)


def resolve_topic_by_name(topic_name, user, fallback_topic=None):
    topic_name = (topic_name or "").strip()
    if topic_name:
        topic, _ = Topic.objects.get_or_create(
            name=topic_name,
            defaults={"created_by": user},
        )
        return topic
    return fallback_topic


def login_view(request):
    error = None

    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")

        if password == PASSWORD and name:
            session = UserSession.objects.create(name=name)

            request.session['user'] = name
            request.session['session_id'] = session.id

            ActivityLog.objects.create(
                user_name=name,
                action="Logged in"
            )

            return redirect('findings')
        else:
            error = "Invalid name or password"

    return render(request, 'login.html', {'error': error})

def logout_view(request):
    session_id = request.session.get('session_id')
    name = request.session.get('user')

    if session_id:
        session = UserSession.objects.get(id=session_id)
        session.logout_time = timezone.now()
        session.save()

    ActivityLog.objects.create(
        user_name=name,
        action="Logged out"
    )

    request.session.flush()
    return redirect('login')


def findings(request):
    user = current_user(request)
    all_topics = Topic.objects.annotate(finding_count=Count("findings")).filter(finding_count__gt=0).order_by("name")
    topic_query = request.GET.get("q", "").strip()
    topics = all_topics.filter(name__icontains=topic_query) if topic_query else all_topics
    selected_topic = None
    topic_id = request.GET.get("topic")
    show_all_topics = topic_id == "all"
    if topic_id and not show_all_topics:
        selected_topic = all_topics.filter(id=topic_id).first()
    if selected_topic is None and not show_all_topics:
        selected_topic = all_topics.first()

    edit_finding = None
    edit_comment = None

    edit_id = request.GET.get("edit")
    if edit_id:
        edit_finding = get_object_or_404(Finding, id=edit_id)
        selected_topic = edit_finding.topic or selected_topic

    edit_comment_id = request.GET.get("edit_comment")
    if edit_comment_id:
        edit_comment = get_object_or_404(FindingComment, id=edit_comment_id)
        selected_topic = edit_comment.finding.topic or selected_topic
        show_all_topics = False

    if show_all_topics:
        findings = Finding.objects.select_related("topic").prefetch_related("comments").order_by("-created_at")
    elif selected_topic:
        findings = Finding.objects.filter(topic=selected_topic).select_related("topic").prefetch_related("comments").order_by("-created_at")
    else:
        findings = Finding.objects.none()

    if request.method == "POST":
        action = request.POST.get("action")
        topic_query = request.POST.get("q", "").strip()
        query_suffix = f"&q={topic_query}" if topic_query else ""

        if action == "add_finding":
            topic_name = request.POST.get("topic_name", "").strip()
            content = request.POST.get("content", "")
            attachment_mode = request.POST.get("attachment_mode", "none")
            if attachment_mode not in {"none", "file", "code", "both"}:
                attachment_mode = "none"
            file = request.FILES.get("file") if attachment_mode in {"file", "both"} else None
            code_snippet = request.POST.get("code_snippet", "").strip() if attachment_mode in {"code", "both"} else ""
            code_language = request.POST.get("code_language", "").strip() if code_snippet else ""
            topic = resolve_topic_by_name(
                topic_name,
                user,
                fallback_topic=selected_topic,
            )

            if topic and content.strip():
                Finding.objects.create(
                    topic=topic,
                    title=topic.name,
                    content=content,
                    created_by=user,
                    file=file,
                    code_snippet=code_snippet,
                    code_language=code_language,
                )

                ActivityLog.objects.create(
                    user_name=user,
                    action="Added Finding",
                    details=topic.name
                )
                messages.success(request, f'Posted to "{topic.name}".')
                redirect_topic = "all" if show_all_topics else str(topic.id)
                return HttpResponseRedirect(f"{reverse('findings')}?topic={redirect_topic}{query_suffix}#topic-feed")

            messages.error(request, "Enter a topic name and content.")

        elif action == "update_finding":
            finding = get_object_or_404(Finding, id=request.POST.get("finding_id"))
            topic = resolve_topic_by_name(
                request.POST.get("topic_name"),
                user,
                fallback_topic=finding.topic,
            )
            finding.topic = topic
            finding.content = request.POST.get("content", finding.content)
            attachment_mode = request.POST.get("attachment_mode", "none")
            if attachment_mode not in {"none", "file", "code", "both"}:
                attachment_mode = "none"
            finding.code_snippet = request.POST.get("code_snippet", "").strip() if attachment_mode in {"code", "both"} else ""
            finding.code_language = request.POST.get("code_language", "").strip() if finding.code_snippet else ""
            if topic:
                finding.title = topic.name

            if request.POST.get("remove_file") == "on":
                delete_finding_file(finding)
                finding.file = None

            new_file = request.FILES.get("file") if attachment_mode in {"file", "both"} else None
            if new_file:
                delete_finding_file(finding)
                finding.file = new_file

            finding.save()

            ActivityLog.objects.create(
                user_name=user,
                action="Updated Finding",
                details=finding.topic.name if finding.topic else finding.title
            )
            messages.success(request, "Post updated.")
            redirect_topic = "all" if show_all_topics else str(finding.topic_id)
            return HttpResponseRedirect(f"{reverse('findings')}?topic={redirect_topic}{query_suffix}#topic-feed")

        elif action == "delete_finding":
            finding = get_object_or_404(Finding, id=request.POST.get("finding_id"))
            title = finding.topic.name if finding.topic else finding.title
            topic_id = finding.topic_id
            delete_finding_file(finding)
            finding.delete()

            ActivityLog.objects.create(
                user_name=user,
                action="Deleted Finding",
                details=title
            )
            messages.success(request, f'"{title}" deleted.')
            if topic_id:
                redirect_topic = "all" if show_all_topics else str(topic_id)
                return HttpResponseRedirect(f"{reverse('findings')}?topic={redirect_topic}{query_suffix}#topic-feed")

        elif action == "add_comment":
            finding = get_object_or_404(Finding, id=request.POST.get("finding_id"))
            content = request.POST.get("comment_content", "").strip()
            if content:
                FindingComment.objects.create(
                    finding=finding,
                    content=content,
                    created_by=user,
                )
                ActivityLog.objects.create(
                    user_name=user,
                    action="Added Comment",
                    details=finding.topic.name if finding.topic else finding.title,
                )
                messages.success(request, "Comment added.")
            else:
                messages.error(request, "Comment cannot be empty.")

            return HttpResponseRedirect(
                f"{reverse('findings')}?topic={'all' if show_all_topics else finding.topic_id}{query_suffix}#finding-{finding.id}"
            )

        elif action == "update_comment":
            comment = get_object_or_404(FindingComment, id=request.POST.get("comment_id"))
            content = request.POST.get("comment_content", "").strip()
            if content:
                comment.content = content
                comment.save()
                ActivityLog.objects.create(
                    user_name=user,
                    action="Updated Comment",
                    details=comment.finding.topic.name if comment.finding.topic else comment.finding.title,
                )
                messages.success(request, "Comment updated.")
            else:
                messages.error(request, "Comment cannot be empty.")

            return HttpResponseRedirect(
                f"{reverse('findings')}?topic={'all' if show_all_topics else comment.finding.topic_id}{query_suffix}#finding-{comment.finding_id}"
            )

        elif action == "delete_comment":
            comment = get_object_or_404(FindingComment, id=request.POST.get("comment_id"))
            finding_id = comment.finding_id
            topic_id = comment.finding.topic_id
            comment.delete()
            ActivityLog.objects.create(
                user_name=user,
                action="Deleted Comment",
                details=str(finding_id),
            )
            messages.success(request, "Comment deleted.")
            return HttpResponseRedirect(
                f"{reverse('findings')}?topic={'all' if show_all_topics else topic_id}{query_suffix}#finding-{finding_id}"
            )

        return redirect('findings')

    return render(
        request,
        'findings.html',
        {
            'findings': findings,
            'edit_finding': edit_finding,
            'edit_comment': edit_comment,
            'all_topics': all_topics,
            'topics': topics,
            'topic_query': topic_query,
            'selected_topic': selected_topic,
            'show_all_topics': show_all_topics,
        },
    )
