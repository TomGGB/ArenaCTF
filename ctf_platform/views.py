"""
Custom error handlers for CTF platform.
"""
from django.shortcuts import render
import uuid


def custom_400(request, exception=None):
    """Handler para error 400 - Bad Request"""
    context = {
        'request_id': str(uuid.uuid4())[:8].upper(),
    }
    return render(request, '400.html', context, status=400)


def custom_403(request, exception=None):
    """Handler para error 403 - Forbidden"""
    context = {
        'request_id': str(uuid.uuid4())[:8].upper(),
    }
    return render(request, '403.html', context, status=403)


def custom_404(request, exception=None):
    """Handler para error 404 - Not Found"""
    context = {
        'request_id': str(uuid.uuid4())[:8].upper(),
    }
    return render(request, '404.html', context, status=404)


def custom_500(request):
    """Handler para error 500 - Internal Server Error"""
    context = {
        'request_id': str(uuid.uuid4())[:8].upper(),
    }
    return render(request, '500.html', context, status=500)
