from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    STUDENT = "student", "Student"
    LECTURER = "lecturer", "Lecturer"
    HOD = "hod", "Head of Department"
    DEAN = "dean", "Dean"
    REGISTRAR = "registrar", "Registrar"
    FINANCE = "finance", "Finance / Bursar"
    PARENT = "parent", "Parent / Sponsor"
    ADMIN = "admin", "Institution Admin"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        blank=True,
        default="",
        help_text=(
            "Primary role for this account. Superusers operate above role "
            "gating and may leave this blank."
        ),
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="International format, e.g. +256700000000. Used for SMS notifications.",
    )

    @property
    def is_student(self):
        return self.role == Role.STUDENT

    @property
    def is_lecturer(self):
        return self.role in {Role.LECTURER, Role.HOD, Role.DEAN}

    @property
    def is_hod(self):
        return self.role == Role.HOD

    @property
    def is_dean(self):
        return self.role == Role.DEAN

    @property
    def is_registrar(self):
        return self.role == Role.REGISTRAR

    @property
    def is_finance(self):
        return self.role == Role.FINANCE

    def __str__(self):
        return self.get_full_name() or self.username


class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        GRADUATED = "graduated", "Graduated"
        SUSPENDED = "suspended", "Suspended"
        WITHDRAWN = "withdrawn", "Withdrawn"

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    student_number = models.CharField(
        max_length=30,
        unique=True,
        help_text='Institutional student number, e.g. "2023/CS/001".',
    )
    programme = models.ForeignKey(
        "academics.Programme",
        on_delete=models.PROTECT,
        related_name="students",
    )
    year_of_study = models.PositiveSmallIntegerField(default=1)
    date_enrolled = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student_number"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.student_number} — {self.user}"


class Staff(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full time"
        PART_TIME = "part_time", "Part time"
        CONTRACT = "contract", "Contract"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On leave"
        RETIRED = "retired", "Retired"
        TERMINATED = "terminated", "Terminated"

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    staff_number = models.CharField(
        max_length=30,
        unique=True,
        help_text='Institutional staff number, e.g. "STF/2019/042".',
    )
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.PROTECT,
        related_name="staff",
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    date_hired = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["staff_number"]
        verbose_name = "Staff"
        verbose_name_plural = "Staff"

    def __str__(self):
        return f"{self.staff_number} — {self.user}"
