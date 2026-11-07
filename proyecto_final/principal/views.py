from django.http import HttpResponse

def hola_mundo(request):
    return HttpResponse("¡Hola, papu! Esta es mi primera página creada con Django 🚀")