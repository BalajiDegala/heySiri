from django.shortcuts import render, redirect
from .models import UserSession, ActivityLog, Task, Finding
from django.utils import timezone

PASSWORD = "pipeline"  # change this


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

            return redirect('dashboard')
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

    from .models import Task

def agenda(request):
    user = request.session.get('user')
    tasks = Task.objects.all().order_by('-created_at')

    if request.method == "POST":
        title = request.POST.get("title")
        Task.objects.create(
            title=title,
            created_by=user,
            week="Week 1"
        )

        ActivityLog.objects.create(
            user_name=user,
            action="Added Task",
            details=title
        )

        return redirect('agenda')

    return render(request, 'agenda.html', {'tasks': tasks})

from .models import Finding

def findings(request):
    user = request.session.get('user')
    findings = Finding.objects.all().order_by('-created_at')

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        file = request.FILES.get("file")

        Finding.objects.create(
            title=title,
            content=content,
            created_by=user,
            file=file
        )

        ActivityLog.objects.create(
            user_name=user,
            action="Added Finding",
            details=title
        )

        return redirect('findings')

    return render(request, 'findings.html', {'findings': findings})


def activity(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'activity.html', {'logs': logs})


def dashboard(request):
    total = Task.objects.count()
    completed = Task.objects.filter(completed=True).count()

    percent = 0
    if total > 0:
        percent = int((completed / total) * 100)

    return render(request, 'dashboard.html', {'percent': percent})

