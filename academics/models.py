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
    captured_by_device = models.ForeignKey(
        "AttendanceDevice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="captured_attendance",
        help_text=(
            "Set when the record was created by a device event (biometric/QR). "
            "NULL for manual marking."
        ),
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


class AttendanceCaptureConfig(models.Model):
    class Method(models.TextChoices):
        MANUAL = "manual", "Manual only"
        BIOMETRIC = "biometric", "Biometric only"
        HYBRID = "hybrid", "Hybrid (biometric preferred, manual allowed)"

    class ConflictPolicy(models.TextChoices):
        FLAG = "flag", "Flag for review"
        BIOMETRIC_WINS = "biometric_wins", "Biometric wins"
        MANUAL_WINS = "manual_wins", "Manual wins"

    offering = models.OneToOneField(
        CourseOffering,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="capture_config",
        help_text=(
            "Leave blank for the institution-wide default. Set to override "
            "the capture method for a specific course offering."
        ),
    )
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.MANUAL,
    )
    grace_minutes_before = models.PositiveSmallIntegerField(
        default=15,
        help_text=(
            "Minutes before the session start within which a device event "
            "is still considered part of this session."
        ),
    )
    grace_minutes_after = models.PositiveSmallIntegerField(
        default=15,
        help_text=(
            "Minutes after the session end within which a device event is "
            "still considered part of this session."
        ),
    )
    conflict_policy = models.CharField(
        max_length=20,
        choices=ConflictPolicy.choices,
        default=ConflictPolicy.FLAG,
        help_text=(
            "How to resolve disagreements between a manual mark and a "
            "biometric observation for the same session."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["offering"]
        constraints = [
            UniqueConstraint(
                fields=["offering"],
                condition=Q(offering__isnull=False),
                name="unique_capture_config_per_offering",
            ),
            UniqueConstraint(
                fields=["offering"],
                condition=Q(offering__isnull=True),
                name="only_one_global_capture_config",
            ),
        ]
        verbose_name = "Attendance capture config"
        verbose_name_plural = "Attendance capture configs"

    def __str__(self):
        scope = self.offering or "Institution default"
        return f"{scope} — {self.get_method_display()}"


class AttendanceDevice(models.Model):
    class DeviceType(models.TextChoices):
        FINGERPRINT = "fingerprint", "Fingerprint scanner"
        QR_TERMINAL = "qr_terminal", "QR / card terminal"

    name = models.CharField(max_length=100)
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text='Physical location, e.g. "Physiology Lab — Room 2".',
    )
    offerings = models.ManyToManyField(
        CourseOffering,
        blank=True,
        related_name="attendance_devices",
        help_text=(
            "Course offerings this device reports events for. Empty means "
            "the device is provisioned but not yet assigned."
        ),
    )
    api_key_hash = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text=(
            "Hash of the device's API key. Empty until provisioning. Never "
            "store the plaintext key here. Provisoning UI: TODO."
        ),
    )
    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Updated by the device on each successful event POST. TODO.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Deactivated devices are rejected by the event ingest endpoint "
            "even if their API key is valid."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Attendance device"
        verbose_name_plural = "Attendance devices"

    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()})"


class BiometricEnrollment(models.Model):
    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.CASCADE,
        related_name="biometric_enrollments",
    )
    device_type = models.CharField(
        max_length=20,
        choices=AttendanceDevice.DeviceType.choices,
        help_text=(
            "Fingerprint template formats are vendor/protocol specific. A "
            "student may be enrolled on multiple device families."
        ),
    )
    template_ref = models.CharField(
        max_length=200,
        help_text=(
            "Opaque reference assigned by the scanner for this student's "
            "biometric template. NOT the template itself — the biometric "
            "data stays on the device."
        ),
    )
    enrolled_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student", "device_type"]
        constraints = [
            UniqueConstraint(
                fields=["device_type", "template_ref"],
                name="unique_template_ref_per_device_type",
            ),
            UniqueConstraint(
                fields=["student", "device_type"],
                condition=Q(is_active=True),
                name="unique_active_biometric_per_student_per_device_type",
            ),
        ]
        verbose_name = "Biometric enrollment"
        verbose_name_plural = "Biometric enrollments"

    def __str__(self):
        return f"{self.student} → {self.device_type}:{self.template_ref}"


class AttendanceEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        MATCHED = "matched", "Matched"
        DUPLICATE = "duplicate", "Duplicate"
        UNMATCHED_SUBJECT = "unmatched_subject", "Unmatched subject"
        UNMATCHED_SESSION = "unmatched_session", "No session in window"
        AMBIGUOUS = "ambiguous", "Ambiguous — multiple candidate sessions"
        CONFLICT = "conflict", "Manual/biometric conflict"
        REJECTED = "rejected", "Rejected after review"

    device = models.ForeignKey(
        AttendanceDevice,
        on_delete=models.PROTECT,
        related_name="events",
    )
    external_id = models.CharField(
        max_length=100,
        help_text="Event ID assigned by the device. Unique per device.",
    )
    subject_ref = models.CharField(
        max_length=200,
        help_text=(
            "Raw subject identifier from the device — usually a template_ref "
            "or a student card number."
        ),
    )
    observed_at = models.DateTimeField(
        help_text="Time from the device clock, not the server clock.",
    )
    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Original event body for debugging and replay.",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )
    resolved_record = models.ForeignKey(
        AttendanceRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_events",
        help_text=(
            "Populated when a PENDING event is reconciled into an "
            "AttendanceRecord by the (future) reconciliation worker."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-observed_at"]
        constraints = [
            UniqueConstraint(
                fields=["device", "external_id"],
                name="unique_event_external_id_per_device",
            ),
        ]
        verbose_name = "Attendance event"
        verbose_name_plural = "Attendance events"

    def __str__(self):
        return f"{self.device.name} · {self.external_id} · {self.get_status_display()}"
