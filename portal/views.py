from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from academics.models import CourseOffering
from accounts.decorators import role_required

from .permissions import can_view_offering


def home_view(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    user = request.user
    if user.is_superuser:
        return redirect("/admin/")
    if user.is_lecturer:
        return redirect("portal:lecturer_home")
    if user.is_student:
        return redirect("portal:student_home")
    return render(request, "portal/home.html")


@role_required("student")
def student_home(request):
    student = request.user.student_profile
    enrollments = (
        student.enrollments.filter(status="enrolled")
        .select_related("course_offering__course", "course_offering__term")
        .order_by("course_offering__course__code")
    )
    return render(
        request,
        "portal/student_home.html",
        {"student": student, "enrollments": enrollments},
    )


@role_required("lecturer", "hod", "dean")
def lecturer_home(request):
    offerings = request.user.coordinated_offerings.select_related("course", "term").order_by(
        "course__code"
    )
    return render(
        request,
        "portal/lecturer_home.html",
        {"offerings": offerings},
    )


@role_required("lecturer", "hod", "dean")
def offering_detail(request, pk):
    offering = get_object_or_404(
        CourseOffering.objects.select_related(
            "course__department__faculty",
            "term",
            "coordinator",
        ).prefetch_related(
            "enrollments__student__user",
            "enrollments__student__programme",
        ),
        pk=pk,
    )
    if not can_view_offering(request.user, offering):
        raise PermissionDenied

    enrollments = (
        offering.enrollments.filter(status="enrolled")
        .select_related("student__user", "student__programme")
        .order_by("student__student_number")
    )
    recent_sessions = offering.sessions.all()[:5]

    return render(
        request,
        "portal/offering_detail.html",
        {
            "offering": offering,
            "enrollments": enrollments,
            "recent_sessions": recent_sessions,
        },
    )


@role_required("lecturer", "hod", "dean")
def take_attendance_placeholder(request, pk):
    offering = get_object_or_404(
        CourseOffering.objects.select_related("course", "term"),
        pk=pk,
    )
    if not can_view_offering(request.user, offering):
        raise PermissionDenied
    return render(
        request,
        "portal/attendance_placeholder.html",
        {"offering": offering},
    )
