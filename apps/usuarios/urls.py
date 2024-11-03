from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path
from . import views

app_name = 'usuarios'

def admin_required(user):
    return user.is_superuser  # Solo permite acceso a superusuarios


urlpatterns = [
    path('', user_passes_test(admin_required)(login_required(views.empleados)), name='empleados'),
    path('buscarEmpleado/',user_passes_test(admin_required)(login_required(views.buscarEmpleado)), name='buscarEmpleado'),
    path('eliminarEmpleado/<empleado_id>',user_passes_test(admin_required)(login_required(views.eliminarEmpleado)), name='eliminarEmpleado'),
    path('editarEmpleado/<empleado_id>',user_passes_test(admin_required)(login_required(views.editarEmpleado)),name='editarEmpleado'),
    path('edicionEmpleado/',user_passes_test(admin_required)(login_required(views.edicionEmpleado)),name='edicionEmpleado'),
    path('agregarEmpleado',user_passes_test(admin_required)(login_required(views.agregarEmpleado)),name='agregarEmpleado'),
    path('crear_usuario/', user_passes_test(admin_required)(login_required(views.crear_usuario)), name='crear_usuario'),
    path('generarPDF/', user_passes_test(admin_required)(login_required(views.generarPDF)), name='generarPDF'),
]