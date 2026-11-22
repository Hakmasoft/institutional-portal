from django.db import connection
from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})


def db_health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
        return JsonResponse({"status": "ok", "result": row})
    except Exception as exc:
        return JsonResponse(
            {
                "status": "error",
                "type": type(exc).__name__,
                "error": str(exc),
            },
            status=500,
        )