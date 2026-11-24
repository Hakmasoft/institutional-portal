"""Object-level authorization for portal views."""

from academics.models import CourseOffering, Enrollment


def can_view_offering(user, offering: CourseOffering):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if offering.coordinator_id == user.id:
        return True

    staff = getattr(user, "staff_profile", None)
    if staff is None:
        return False

    if user.is_hod and staff.department_id == offering.course.department_id:
        return True
    if user.is_dean and (staff.department.faculty_id == offering.course.department.faculty_id):
        return True
    return False


def can_view_enrollment(user, enrollment: Enrollment):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if enrollment.student.user_id == user.id:
        return True
    return can_view_offering(user, enrollment.course_offering)
