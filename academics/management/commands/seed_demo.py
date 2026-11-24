from datetime import time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from academics.models import (
    AcademicYear,
    AttendanceCaptureConfig,
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
from accounts.models import Staff, Student

DEMO_PASSWORD = "demo1234!"


class Command(BaseCommand):
    help = "Seed the local database with medical-school demo data. Refuses to run when DEBUG=False."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "seed_demo is a local-development tool. Set DEBUG=True or use "
                "a management command appropriate for production."
            )

        with transaction.atomic():
            self._seed()
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))

    def _seed(self):
        faculties, departments = self._seed_academic_structure()
        term = self._seed_term()
        courses = self._seed_courses(departments)
        offerings = self._seed_offerings(courses, term)
        self._seed_capture_config()
        users = self._seed_users(departments, offerings, term)
        self._seed_students(users, offerings)
        self._seed_sessions(offerings, users[0])

    def _seed_capture_config(self):
        existing = AttendanceCaptureConfig.objects.filter(offering__isnull=True).first()
        if existing is None:
            AttendanceCaptureConfig.objects.create(
                offering=None,
                method=AttendanceCaptureConfig.Method.MANUAL,
                conflict_policy=AttendanceCaptureConfig.ConflictPolicy.FLAG,
            )

    def _seed_academic_structure(self):
        med = Faculty.objects.get_or_create(
            code="MED",
            defaults={"name": "Faculty of Medicine"},
        )[0]
        nur = Faculty.objects.get_or_create(
            code="NUR",
            defaults={"name": "Faculty of Nursing"},
        )[0]

        departments = {}
        departments["anat"] = Department.objects.get_or_create(
            faculty=med,
            code="ANAT",
            defaults={"name": "Anatomy"},
        )[0]
        departments["physio"] = Department.objects.get_or_create(
            faculty=med,
            code="PHYSIO",
            defaults={"name": "Physiology"},
        )[0]
        departments["ime"] = Department.objects.get_or_create(
            faculty=med,
            code="IME",
            defaults={"name": "Internal Medicine"},
        )[0]
        departments["nurs"] = Department.objects.get_or_create(
            faculty=nur,
            code="NURS",
            defaults={"name": "Nursing Science"},
        )[0]

        Programme.objects.get_or_create(
            code="MBCHB",
            defaults={
                "department": departments["ime"],
                "name": "Bachelor of Medicine and Bachelor of Surgery",
                "duration_years": 5,
            },
        )
        Programme.objects.get_or_create(
            code="BSN",
            defaults={
                "department": departments["nurs"],
                "name": "Bachelor of Science in Nursing",
                "duration_years": 4,
            },
        )

        return (med, nur), departments

    def _seed_term(self):
        ay = AcademicYear.objects.get_or_create(
            name="2025/2026",
            defaults={"start_date": "2025-08-01", "end_date": "2026-06-30"},
        )[0]

        existing_current = Term.objects.filter(is_current=True).first()
        term = Term.objects.filter(
            academic_year=ay,
            name="Semester 1",
        ).first()

        if term is None:
            term, _ = Term.objects.get_or_create(
                academic_year=ay,
                name="Semester 1",
                defaults={
                    "start_date": "2025-08-15",
                    "end_date": "2025-12-15",
                    "is_current": existing_current is None,
                },
            )

        if existing_current and not term.is_current:
            self.stdout.write(
                self.style.WARNING(
                    f"Warning: term '{existing_current}' is already current. "
                    f"Seed term '{term}' was created but not marked current."
                )
            )

        return term

    def _seed_courses(self, departments):
        courses_data = [
            ("ANAT101", "Human Anatomy I", departments["anat"], 4),
            ("PHYS101", "Medical Physiology I", departments["physio"], 4),
            ("MED101", "Introduction to Clinical Medicine", departments["ime"], 3),
            ("NURS101", "Fundamentals of Nursing Practice", departments["nurs"], 4),
        ]
        courses = []
        for code, title, department, credit_units in courses_data:
            course = Course.objects.get_or_create(
                code=code,
                defaults={
                    "title": title,
                    "department": department,
                    "credit_units": credit_units,
                },
            )[0]
            courses.append(course)
        return courses

    def _seed_offerings(self, courses, term):
        offerings = {}
        for course in courses:
            offering = CourseOffering.objects.get_or_create(
                course=course,
                term=term,
                defaults={"coordinator": None},
            )[0]
            offerings[course.code] = offering
        return offerings

    def _seed_users(self, departments, offerings, term):
        User = get_user_model()

        lecturer_user, created = User.objects.get_or_create(
            username="lecturer1",
            defaults={
                "role": "lecturer",
                "first_name": "Sarah",
                "last_name": "Namubiru",
                "email": "s.namubiru@demo.local",
                "is_staff": True,
                "is_active": True,
            },
        )
        if created:
            lecturer_user.set_password(DEMO_PASSWORD)
            lecturer_user.save()

        hod_user, created = User.objects.get_or_create(
            username="hod_anat",
            defaults={
                "role": "hod",
                "first_name": "Joseph",
                "last_name": "Kizito",
                "email": "j.kizito@demo.local",
                "is_staff": True,
                "is_active": True,
            },
        )
        if created:
            hod_user.set_password(DEMO_PASSWORD)
            hod_user.save()

        Staff.objects.get_or_create(
            staff_number="STF/2018/001",
            defaults={
                "user": lecturer_user,
                "department": departments["physio"],
                "employment_type": "full_time",
                "date_hired": "2018-09-01",
                "status": "active",
            },
        )
        Staff.objects.get_or_create(
            staff_number="STF/2015/007",
            defaults={
                "user": hod_user,
                "department": departments["anat"],
                "employment_type": "full_time",
                "date_hired": "2015-01-15",
                "status": "active",
            },
        )

        phys101_offering = CourseOffering.objects.get(
            course__code="PHYS101",
            term=term,
        )
        if phys101_offering.coordinator_id != lecturer_user.id:
            phys101_offering.coordinator = lecturer_user
            phys101_offering.save()

        return lecturer_user, hod_user

    def _seed_students(self, users, offerings):
        User = get_user_model()
        mbchb = Programme.objects.get(code="MBCHB")
        bsn = Programme.objects.get(code="BSN")

        students_data = [
            ("2023/MB/001", "Alice", "Nakato", mbchb, 2),
            ("2023/MB/002", "Bob", "Okello", mbchb, 2),
            ("2023/MB/003", "Carol", "Achieng", mbchb, 2),
            ("2023/MB/004", "David", "Ssemakula", mbchb, 2),
            ("2024/MB/001", "Eve", "Namono", mbchb, 1),
            ("2024/MB/002", "Frank", "Mugisha", mbchb, 1),
            ("2023/BN/001", "Grace", "Atim", bsn, 2),
            ("2023/BN/002", "Henry", "Byaruhanga", bsn, 2),
            ("2024/BN/001", "Irene", "Akello", bsn, 1),
            ("2024/BN/002", "James", "Otim", bsn, 1),
        ]

        students = {}
        for student_number, first_name, last_name, programme, year in students_data:
            username = student_number.lower().replace("/", "_")
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "role": "student",
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": f"{username}@demo.local",
                    "is_staff": False,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()

            cohort = student_number[:4]
            student = Student.objects.get_or_create(
                student_number=student_number,
                defaults={
                    "user": user,
                    "programme": programme,
                    "year_of_study": year,
                    "date_enrolled": f"{cohort}-08-15",
                    "status": "active",
                },
            )[0]
            students[student_number] = student

        for student_number, student in students.items():
            if "/MB/" in student_number:
                offering_codes = ("ANAT101", "PHYS101", "MED101")
            else:
                offering_codes = ("ANAT101", "PHYS101", "NURS101")
            for code in offering_codes:
                Enrollment.objects.get_or_create(
                    student=student,
                    course_offering=offerings[code],
                    defaults={"status": "enrolled"},
                )

    def _seed_sessions(self, offerings, lecturer_user):
        yesterday = timezone.localdate() - timedelta(days=1)
        for code, offering in offerings.items():
            session, _ = ClassSession.objects.get_or_create(
                course_offering=offering,
                date=yesterday,
                start_time=time(9, 0),
                defaults={
                    "end_time": time(11, 0),
                    "venue": "Main Hall",
                    "topic": f"Introductory {code}",
                    "status": ClassSession.Status.HELD,
                    "created_by": lecturer_user,
                },
            )
            enrollments = offering.enrollments.filter(status="enrolled")
            enrollment_count = enrollments.count()
            for idx, enrollment in enumerate(enrollments):
                status = (
                    AttendanceRecord.Status.PRESENT
                    if idx < int(enrollment_count * 0.8)
                    else AttendanceRecord.Status.ABSENT
                )
                AttendanceRecord.objects.get_or_create(
                    session=session,
                    enrollment=enrollment,
                    defaults={
                        "status": status,
                        "capture_method": AttendanceRecord.CaptureMethod.MANUAL,
                        "captured_by": lecturer_user,
                    },
                )
