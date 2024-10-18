from django.urls import path
from . import views

app_name='productos'

urlpatterns = [
    path('',views.productos,name='productos'),
    path('editarProducto/<producto_id>',views.editarProducto,name='editarProducto'),
    path('eliminarProducto/<producto_id>',views.eliminarProducto,name='eliminarProducto'),
    path('edicionProducto/',views.edicionProducto,name='edicionProducto'),
    path('buscarProducto/', views.buscarProducto, name='buscarProducto'),
]