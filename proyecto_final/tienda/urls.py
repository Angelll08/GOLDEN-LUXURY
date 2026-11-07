from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.detalle, name='detalle'),
    path('carrito/', views.carrito_ver, name='carrito'),
    path('carrito/agregar/', views.carrito_agregar, name='carrito_agregar'),
    path('carrito/quitar/<str:clave>/', views.carrito_quitar, name='carrito_quitar'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido/<int:pk>/gracias/', views.pedido_ok, name='pedido_ok'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('rastreo/', views.rastreo, name='rastreo'),
    path('rastreo/<int:pk>/', views.rastreo_detalle, name='rastreo_detalle'),
    path('pedido/<int:pk>/encuesta/', views.encuesta, name='encuesta'),
    path('chat/', views.chat_sala, name='chat'),
    path('chat/mensajes/', views.chat_mensajes, name='chat_mensajes'),
    path('chat/enviar/', views.chat_enviar, name='chat_enviar'),
]
