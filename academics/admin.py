from django.contrib import admin

from .models import (
    AcademicYear,
    AttendanceRecord,
    ClassSession,
    Course,
    CourseOffering,
    Department,
    Enrollment,
    Faculty,
    Programme,
    Term,
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    search_fields = ("name",)
    ordering = ("-start_date",)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "start_date", "end_date", "is_current")
    list_filter = ("is_current", "academic_year")
    search_fields = ("name", "academic_year__name")
    ordering = ("-start_date",)
    autocomplete_fields = ("academic_year",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "department", "credit_units")
    list_filter = ("department__faculty", "department")
    search_fields = ("code", "title", "department__name", "department__code")
    ordering = ("code",)
    autocomplete_fields = ("department",)
    list_select_related = ("department",)


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ("course", "term", "coordinator")
    list_filter = ("term", "course")
    search_fields = (
        "course__code",
        "course__title",
        "term__name",
        "term__academic_year__name",
    )
    autocomplete_fields = ("course", "term", "coordinator")
    list_select_related = ("course", "term", "coordinator")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "faculty")
    list_filter = ("faculty",)
    search_fields = ("code", "name", "faculty__name", "faculty__code")
    ordering = ("faculty__name", "name")
    autocomplete_fields = ("faculty",)
    list_select_related = ("faculty",)


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "department", "duration_years")
    list_filter = ("department__faculty", "department")
    search_fields = (
        "code",
        "name",
        "department__name",
        "department__code",
        "department__faculty__name",
    )
    ordering = ("name",)
    autocomplete_fields = ("department",)
    list_select_related = ("department",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course_offering",
        "status",
        "registered_at",
    )
    list_filter = (
        "status",
        "course_offering__term",
        "course_offering__course__department",
    )
    search_fields = (
        "student__student_number",
        "student__user__first_name",
        "student__user__last_name",
        "student__user__email",
        "course_offering__course__code",
        "course_offering__course__title",
    )
    autocomplete_fields = ("student", "course_offering")
    list_select_related = ("student", "course_offering")
    ordering = ("-registered_at",)
    date_hierarchy = "registered_at"


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = (
        "course_offering",
        "date",
        "start_time",
        "end_time",
        "status",
        "venue",
        "topic",
    )
    list_filter = (
        "status",
        "date",
        "course_offering__term",
        "course_offering__course__department",
    )
    search_fields = (
        "course_offering__course__code",
        "course_offering__course__title",
        "venue",
        "topic",
    )
    autocomplete_fields = ("course_offering", "created_by")
    list_select_related = (
        "course_offering",
        "course_offering__course",
        "course_offering__term",
    )
    ordering = ("-date", "-start_time")
    date_hierarchy = "date"


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "enrollment",
        "status",
        "capture_method",
        "captured_by",
        "captured_at",
    )
    list_filter = (
        "status",
        "capture_method",
        "session__date",
        "session__course_offering__term",
    )
    search_fields = (
        "enrollment__student__student_number",
        "enrollment__student__user__first_name",
        "enrollment__student__user__last_name",
        "session__course_offering__course__code",
        "session__course_offering__course__title",
    )
    autocomplete_fields = ("session", "enrollment", "captured_by")
    list_select_related = (
        "session",
        "session__course_offering",
        "enrollment",
        "enrollment__student",
    )
    ordering = ("-captured_at",)
    date_hierarchy = "captured_at"
    readonly_fields = ("client_uuid",)
