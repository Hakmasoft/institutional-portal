from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Staff, Student, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    fieldsets = BaseUserAdmin.fieldsets + (("Institutional", {"fields": ("role", "phone_number")}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Institutional", {"fields": ("role", "phone_number")}),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_number",
        "user",
        "programme",
        "year_of_study",
        "status",
    )
    list_filter = (
        "status",
        "programme__department__faculty",
        "programme",
        "year_of_study",
    )
    search_fields = (
        "student_number",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    autocomplete_fields = ("user", "programme")
    list_select_related = ("user", "programme")
    ordering = ("student_number",)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        "staff_number",
        "user",
        "department",
        "employment_type",
        "status",
    )
    list_filter = (
        "status",
        "employment_type",
        "department__faculty",
        "department",
    )
    search_fields = (
        "staff_number",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    autocomplete_fields = ("user", "department")
    list_select_related = ("user", "department")
    ordering = ("staff_number",)
