from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("student/", views.student_home, name="student_home"),
    path("lecturer/", views.lecturer_home, name="lecturer_home"),
    path(
        "lecturer/offerings/<int:pk>/",
        views.offering_detail,
        name="offering_detail",
    ),
    path(
        "lecturer/offerings/<int:pk>/attendance/today/",
        views.take_attendance,
        name="take_attendance",
    ),
]
