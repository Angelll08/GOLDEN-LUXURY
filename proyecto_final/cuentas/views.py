from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistroForm


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        # Hay varios backends configurados, hay que indicar cuál usar
        login(request, usuario, backend='cuentas.backends.CorreoOUsuarioBackend')
        messages.success(request, '¡Bienvenido a Golden Luxury!')
        return redirect('inicio')
    return render(request, 'cuentas/registro.html', {'form': form})
