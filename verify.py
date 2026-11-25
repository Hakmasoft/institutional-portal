import json
from django.test import Client
from django.utils import timezone
from academics.models import AttendanceRecord, ClassSession, CourseOffering
from accounts.models import User

# Clean slate first: remove any existing data
AttendanceRecord.objects.all().delete()
ClassSession.objects.all().delete()

physio = CourseOffering.objects.get(course__code="PHYS101")
enrollments = list(physio.enrollments.filter(status="enrolled"))
print("Enrollment count:", len(enrollments))

# Clean slate: remove any existing today session + records
ClassSession.objects.filter(
    course_offering=physio, date=timezone.localdate()
).delete()
print("Pre-state sessions today:", ClassSession.objects.filter(
    course_offering=physio, date=timezone.localdate()).count())

# GET creates the session (as before)
c = Client()
c.login(username="lecturer1", password="demo1234!")
r = c.get(f"/lecturer/offerings/{physio.pk}/attendance/today/")
print("GET take_attendance:", r.status_code)

session = ClassSession.objects.get(
    course_offering=physio, date=timezone.localdate())
print("Session status before save:", session.status)
print("Records before save:", AttendanceRecord.objects.filter(session=session).count())

# --- Save 1: all present ---
payload = {"records": [
    {"enrollment_id": e.pk, "status": "present"} for e in enrollments
]}
r = c.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data=json.dumps(payload),
    content_type="application/json",
)
data = r.json()
print("Save 1 status:", r.status_code)
print("Save 1 ok:", data.get("ok"))
print("Save 1 saved:", data.get("saved"))
print("Save 1 redirect_url:", data.get("redirect_url"))

session.refresh_from_db()
print("Session status after save 1:", session.status)
print("Records after save 1:",
      AttendanceRecord.objects.filter(session=session).count())
print("All present:",
      AttendanceRecord.objects.filter(session=session, status="present").count())

# Flash was set — verify by following the redirect with a GET
r = c.get(data["redirect_url"])
body = r.content.decode()
print("Redirect page has flash:",
      "Attendance saved for 10 students." in body)

# --- Save 2: two absent (upsert) ---
payload["records"][0]["status"] = "absent"
payload["records"][1]["status"] = "absent"
r = c.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data=json.dumps(payload),
    content_type="application/json",
)
data = r.json()
print("Save 2 status:", r.status_code)
print("Save 2 saved:", data.get("saved"))
print("Records after save 2:",
      AttendanceRecord.objects.filter(session=session).count())
print("Absent count after save 2:",
      AttendanceRecord.objects.filter(session=session, status="absent").count())

# --- Reject invalid status ---
payload_bad = {"records": [
    {"enrollment_id": enrollments[0].pk, "status": "foo"}
]}
r = c.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data=json.dumps(payload_bad),
    content_type="application/json",
)
print("Invalid status:", r.status_code, r.json().get("error"))

# --- Reject invalid enrollment_id ---
payload_bad = {"records": [
    {"enrollment_id": 999999, "status": "present"}
]}
r = c.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data=json.dumps(payload_bad),
    content_type="application/json",
)
print("Invalid enrollment:", r.status_code, r.json().get("error"))

# --- Reject empty records ---
r = c.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data=json.dumps({"records": []}),
    content_type="application/json",
)
print("Empty records:", r.status_code)

# --- Reject malformed JSON ---
r = c.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data="not json",
    content_type="application/json",
)
print("Malformed JSON:", r.status_code)

# --- GET on save URL returns 405 ---
r = c.get(f"/lecturer/offerings/{physio.pk}/attendance/today/save/")
print("GET save endpoint:", r.status_code)

# --- Student cannot save ---
c2 = Client()
c2.login(username="2023_mb_001", password="demo1234!")
r = c2.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data=json.dumps(payload),
    content_type="application/json",
)
print("Student POST:", r.status_code)

# --- HOD of other department cannot save ---
c3 = Client()
c3.login(username="hod_anat", password="demo1234!")
r = c3.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data=json.dumps(payload),
    content_type="application/json",
)
print("HOD other dept POST:", r.status_code)

# --- CANCELLED session rejects save ---
session.status = ClassSession.Status.CANCELLED
session.save()
r = c.post(
    f"/lecturer/offerings/{physio.pk}/attendance/today/save/",
    data=json.dumps(payload),
    content_type="application/json",
)
print("Cancelled session save:", r.status_code)

# Restore HELD (leave in place for manual testing)
session.refresh_from_db()
session.status = ClassSession.Status.HELD
session.save()
print("cleanup: session restored to HELD, records in place for manual testing")