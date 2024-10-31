from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name='estadisticas'

urlpatterns = [
    path('estadisticas/', views.estadisticas_ventas, name='estadisticas_ventas'),
]