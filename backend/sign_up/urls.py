from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('add_email/', views.add_email, name='add_email'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('add_password/', views.add_password, name='add_password'),
]