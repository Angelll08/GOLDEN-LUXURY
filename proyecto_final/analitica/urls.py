from django.urls import path
from . import views

urlpatterns = [
    path('api/evento/', views.evento, name='evento'),
]
