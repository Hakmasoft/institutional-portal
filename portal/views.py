from django.shortcuts import redirect, render

from accounts.decorators import role_required


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
