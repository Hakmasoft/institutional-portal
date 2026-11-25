import json
from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from academics.models import AttendanceRecord, ClassSession, CourseOffering
from accounts.decorators import role_required

from .permissions import can_view_offering


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


@role_required("lecturer", "hod", "dean")
def offering_detail(request, pk):
    offering = get_object_or_404(
        CourseOffering.objects.select_related(
            "course__department__faculty",
            "term",
            "coordinator",
        ).prefetch_related(
            "enrollments__student__user",
            "enrollments__student__programme",
        ),
        pk=pk,
    )
    if not can_view_offering(request.user, offering):
        raise PermissionDenied

    enrollments = (
        offering.enrollments.filter(status="enrolled")
        .select_related("student__user", "student__programme")
        .order_by("student__student_number")
    )
    recent_sessions = offering.sessions.all()[:5]

    return render(
        request,
        "portal/offering_detail.html",
        {
            "offering": offering,
            "enrollments": enrollments,
            "recent_sessions": recent_sessions,
        },
    )


@role_required("lecturer", "hod", "dean")
def take_attendance(request, pk):
    offering = get_object_or_404(
        CourseOffering.objects.select_related("course__department__faculty", "term"),
        pk=pk,
    )
    if not can_view_offering(request.user, offering):
        raise PermissionDenied

    session = _resolve_today_session(offering, request.user)

    enrollments = (
        offering.enrollments.filter(status="enrolled")
        .select_related("student__user", "student__programme")
        .order_by("student__student_number")
    )

    existing_records = {
        record.enrollment_id: record.status
        for record in AttendanceRecord.objects.filter(session=session)
    }

    roster = [
        {
            "enrollment": enrollment,
            "status": existing_records.get(enrollment.pk, AttendanceRecord.Status.PRESENT),
        }
        for enrollment in enrollments
    ]

    statuses = [
        {
            "value": AttendanceRecord.Status.PRESENT,
            "short": "P",
            "full": "Present",
        },
        {
            "value": AttendanceRecord.Status.ABSENT,
            "short": "A",
            "full": "Absent",
        },
        {
            "value": AttendanceRecord.Status.LATE,
            "short": "L",
            "full": "Late",
        },
        {
            "value": AttendanceRecord.Status.EXCUSED,
            "short": "E",
            "full": "Excused",
        },
    ]

    return render(
        request,
        "portal/take_attendance.html",
        {
            "offering": offering,
            "session": session,
            "roster": roster,
            "statuses": statuses,
        },
    )


@role_required("lecturer", "hod", "dean")
@require_POST
def save_attendance(request, pk):
    """Persist attendance for today's session of the offering.

    Accepts JSON: {"records": [{"enrollment_id": int, "status": str}, ...]}

    - Validates each enrollment belongs to the offering and has status
      "enrolled"
    - Validates each status is one of AttendanceRecord.Status values
    - Upserts via update_or_create per record (auto timestamps fire)
    - Flips session status SCHEDULED -> HELD
    - Emits a Django messages.success flash for the redirect target
    - Returns {"ok": true, "saved": N, "redirect_url": "..."}
    """
    offering = get_object_or_404(
        CourseOffering.objects.select_related("course", "term"),
        pk=pk,
    )
    if not can_view_offering(request.user, offering):
        raise PermissionDenied

    # Parse JSON body
    try:
        payload = json.loads(request.body.decode("utf-8"))
        records_payload = payload.get("records")
        if not isinstance(records_payload, list) or not records_payload:
            raise ValueError("Payload must include a non-empty 'records' list.")
    except (json.JSONDecodeError, ValueError) as exc:
        return JsonResponse({"ok": False, "error": f"Invalid payload: {exc}"}, status=400)

    session = _resolve_today_session(offering, request.user)

    if session.status == ClassSession.Status.CANCELLED:
        return JsonResponse(
            {"ok": False, "error": "Cannot save attendance for a cancelled session."},
            status=400,
        )

    # Build valid sets for validation
    valid_enrollment_ids = set(
        offering.enrollments.filter(status="enrolled").values_list("id", flat=True)
    )
    valid_statuses = {choice[0] for choice in AttendanceRecord.Status.choices}

    # Validate every record up-front so the save is all-or-nothing
    for r in records_payload:
        if not isinstance(r, dict):
            return JsonResponse(
                {"ok": False, "error": "Each record must be an object."}, status=400
            )
        eid = r.get("enrollment_id")
        status = r.get("status")
        if eid not in valid_enrollment_ids:
            return JsonResponse({"ok": False, "error": f"Invalid enrollment_id: {eid}"}, status=400)
        if status not in valid_statuses:
            return JsonResponse({"ok": False, "error": f"Invalid status: {status}"}, status=400)

    # Upsert records
    saved_count = 0
    with transaction.atomic():
        for r in records_payload:
            AttendanceRecord.objects.update_or_create(
                session=session,
                enrollment_id=r["enrollment_id"],
                defaults={
                    "status": r["status"],
                    "capture_method": AttendanceRecord.CaptureMethod.MANUAL,
                    "captured_by": request.user,
                    "captured_at": timezone.now(),
                },
            )
            saved_count += 1

    # Flip session to HELD if it was SCHEDULED
    if session.status == ClassSession.Status.SCHEDULED:
        session.status = ClassSession.Status.HELD
        session.save()

    # Flash for the redirect target
    messages.success(
        request,
        f"Attendance saved for {saved_count} student{'s' if saved_count != 1 else ''}.",
    )

    redirect_url = reverse("portal:offering_detail", args=[offering.pk])
    return JsonResponse({"ok": True, "saved": saved_count, "redirect_url": redirect_url})


def _resolve_today_session(offering, user):
    now = timezone.localtime()
    today = now.date()

    lookback = (now - timedelta(hours=4)).time()

    existing = (
        ClassSession.objects.filter(
            course_offering=offering,
            date=today,
            start_time__gte=lookback,
        )
        .order_by("-start_time")
        .first()
    )
    if existing is not None:
        return existing

    rounded_minute = (now.minute // 15) * 15
    rounded_start_dt = now.replace(minute=rounded_minute, second=0, microsecond=0)
    rounded_start = rounded_start_dt.time()
    rounded_end = (rounded_start_dt + timedelta(hours=2)).time()

    session, _ = ClassSession.objects.get_or_create(
        course_offering=offering,
        date=today,
        start_time=rounded_start,
        defaults={
            "end_time": rounded_end,
            "status": ClassSession.Status.SCHEDULED,
            "created_by": user,
        },
    )
    return session
