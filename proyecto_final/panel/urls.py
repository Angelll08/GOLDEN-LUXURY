from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='panel'),
    path('productos/', views.productos, name='panel_productos'),
    path('productos/nuevo/', views.producto_editar, name='panel_producto_nuevo'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='panel_producto_editar'),
    path('productos/<int:pk>/borrar/', views.producto_borrar, name='panel_producto_borrar'),
    path('pedidos/', views.pedidos, name='panel_pedidos'),
    path('accesos/', views.accesos, name='panel_accesos'),
    path('ubicaciones/', views.ubicaciones, name='panel_ubicaciones'),
]
