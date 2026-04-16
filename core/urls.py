from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('agenda/', views.agenda, name='agenda'),
    path('findings/', views.findings, name='findings'),
    path('activity/', views.activity, name='activity'),
    path('logout/', views.logout_view, name='logout'),
]