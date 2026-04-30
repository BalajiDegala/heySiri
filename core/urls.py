from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('findings/', views.findings, name='findings'),
    path('logout/', views.logout_view, name='logout'),
]
