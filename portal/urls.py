from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("student/", views.student_home, name="student_home"),
    path("lecturer/", views.lecturer_home, name="lecturer_home"),
]
