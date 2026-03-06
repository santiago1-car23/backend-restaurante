from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def dashboard(request):
    context = {'active': 'dashboard'}
    return render(request, 'core/inicio.html', context)


def service_worker(request):
    """Service Worker para PWA (scope raíz)."""
    response = render(request, 'core/service-worker.js', content_type='application/javascript')
    # Evitar cache agresivo en desarrollo
    response['Cache-Control'] = 'no-cache'
    return response

