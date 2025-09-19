from django.urls import path
from . import views
urlpatterns = [
    path("ping/", views.ping, name="myapp_ping"),
    path("student/new/", views.new_query, name="student_new_query"),
    path("student/ai/analyze/", views.ai_analyze, name="student_ai_analyze"),
    path("tickets/create/", views.ticket_create, name="ticket_create"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
]

