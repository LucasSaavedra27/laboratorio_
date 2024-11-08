from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required, user_passes_test

app_name='estadisticas'

def admin_required(user):
    return user.is_superuser  # Solo permite acceso a superusuarios

urlpatterns = [
<<<<<<< HEAD
    path('chatbot/', login_required(views.chatbot), name='chatbot'),
    path('estadisticas/', login_required(views.estadisticas_ventas), name='estadisticas_ventas'),
=======
    path('chatbot/', user_passes_test(admin_required)(login_required(views.chatbot)), name='chatbot'),
    path('estadisticas/', user_passes_test(admin_required)(login_required(views.estadisticas_ventas)), name='estadisticas_ventas'),
>>>>>>> origin/chatbot
]