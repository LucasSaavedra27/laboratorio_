document.addEventListener("DOMContentLoaded", function () {
    // deshabilitar fechas posteriores a la actual
    function deshabilitarFechasPasadas() {
        const fechaActual = new Date().toISOString().split("T")[0];
        const camposFecha = document.querySelectorAll('input[type="date"]');
        
        camposFecha.forEach(campo => {
            campo.setAttribute("max", fechaActual);
        });
    }
    
    window.onload = deshabilitarFechasPasadas;
    
});