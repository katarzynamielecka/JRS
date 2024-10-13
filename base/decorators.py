from django.http import HttpResponseForbidden
from functools import wraps
from .models import Employee

def employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Nie masz uprawnień, aby wyświetlić tę stronę.")
        try:
            employee = Employee.objects.get(user=request.user)
            if not employee.is_admin:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Nie masz uprawnień, aby wyświetlić tę stronę.")
        except Employee.DoesNotExist:
            return HttpResponseForbidden("Nie masz uprawnień, aby wyświetlić tę stronę.")
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            employee = Employee.objects.get(user=request.user)
            if employee.is_admin:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Nie masz uprawnień, aby wyświetlić tę stronę.")
        except Employee.DoesNotExist:
            return HttpResponseForbidden("Nie masz uprawnień, aby wyświetlić tę stronę.")
    return _wrapped_view


def admin_or_employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Nie masz uprawnień, aby wyświetlić tę stronę.")
        try:
            employee = Employee.objects.get(user=request.user)
            if employee.is_admin or not employee.is_admin:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Nie masz uprawnień, aby wyświetlić tę stronę.")
        except Employee.DoesNotExist:
            return HttpResponseForbidden("Nie masz uprawnień, aby wyświetlić tę stronę.")
    return _wrapped_view