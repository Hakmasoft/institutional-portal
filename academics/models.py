from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint


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
