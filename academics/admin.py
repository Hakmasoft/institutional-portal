from django.contrib import admin

from .models import AcademicYear, Course, CourseOffering, Term


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
    list_filter = ("department",)
    search_fields = ("code", "title", "department")
    ordering = ("code",)


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
