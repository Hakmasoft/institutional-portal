import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils import timezone


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

    def __str__(self):
        return self.name


class Term(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="terms")
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(
        default=False,
        help_text=(
            "Only one term can be current at a time. To switch, first uncheck the "
            "current term, save, then check the new one."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            UniqueConstraint(
                fields=["academic_year", "name"],
                name="unique_term_name_per_year",
            ),
            UniqueConstraint(
                fields=["is_current"],
                condition=Q(is_current=True),
                name="only_one_current_term_globally",
            ),
        ]
        verbose_name = "Term"
        verbose_name_plural = "Terms"

    def __str__(self):
        return f"{self.academic_year} · {self.name}"


class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Faculties"

    def __str__(self):
        return f"{self.code} — {self.name}"


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="departments")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["faculty__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["faculty", "name"],
                name="unique_department_name_per_faculty",
            ),
            models.UniqueConstraint(
                fields=["faculty", "code"],
                name="unique_department_code_per_faculty",
            ),
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Programme(models.Model):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="programmes")
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    duration_years = models.PositiveSmallIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Programmes"

    def __str__(self):
        return f"{self.code} — {self.name}"


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="courses")
    credit_units = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.title}"


class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="offerings")
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="offerings")
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coordinated_offerings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["term", "course__code"]
        constraints = [
            UniqueConstraint(
                fields=["course", "term"],
                name="unique_offering_per_course_per_term",
            ),
        ]

    def __str__(self):
        return f"{self.course.code} ({self.term})"

    def active_enrollments(self):
        """Enrollments with status='enrolled'. The base queryset for
        attendance rosters, grade entry lists, and other per-offering
        student listings.
        """
        # The literal "enrolled" matches Enrollment.Status.ENROLLED.
        # Using the literal avoids a forward reference to a class defined
        # later in this module; the enum value is stable so drift is not a
        # realistic concern.
        return self.enrollments.filter(status="enrolled")


class ClassSession(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        HELD = "held", "Held"
        CANCELLED = "cancelled", "Cancelled"

    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100, blank=True, default="")
    topic = models.CharField(max_length=200, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-start_time"]
        constraints = [
            UniqueConstraint(
                fields=["course_offering", "date", "start_time"],
                name="unique_session_per_offering_per_date_per_start",
            ),
        ]
        verbose_name = "Class session"
        verbose_name_plural = "Class sessions"

    def __str__(self):
        return f"{self.course_offering} · {self.date} {self.start_time:%H:%M}"

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be later than start time."})


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        DROPPED = "dropped", "Dropped"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course_offering", "student__student_number"]
        constraints = [
            UniqueConstraint(
                fields=["student", "course_offering"],
                name="unique_enrollment_per_student_per_offering",
            ),
        ]
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student} in {self.course_offering}"


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    class CaptureMethod(models.TextChoices):
        MANUAL = "manual", "Lecturer (manual)"
        BIOMETRIC = "biometric", "Fingerprint scanner"
        QR = "qr", "QR / self check-in"
        IMPORT = "import", "CSV import"
        OVERRIDE = "override", "Manual override"

    session = models.ForeignKey(
        ClassSession,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
    )
    capture_method = models.CharField(
        max_length=20,
        choices=CaptureMethod.choices,
        default=CaptureMethod.MANUAL,
    )
    captured_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="captured_attendance",
    )
    captured_at = models.DateTimeField(default=timezone.now)
    client_uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text=(
            "Idempotency key for offline/batch sync. Client generates UUIDv4 "
            "on the device; server stores it to de-duplicate re-posts."
        ),
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Reason for override, or other free-text annotation.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["session", "enrollment__student__student_number"]
        constraints = [
            UniqueConstraint(
                fields=["session", "enrollment"],
                name="unique_attendance_per_session_per_enrollment",
            ),
        ]
        verbose_name = "Attendance record"
        verbose_name_plural = "Attendance records"

    def __str__(self):
        return (
            f"{self.enrollment.student.student_number} · "
            f"{self.session} · {self.get_status_display()}"
        )
