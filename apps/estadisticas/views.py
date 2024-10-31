from django.shortcuts import render
from django.db.models import Sum
from apps.ventas.models import Venta
import plotly.express as px
import pandas as pd


def estadisticas_ventas(request):
    # Gráfico de ventas totales por empleado
    datos_ventas_empleado = Venta.objects.values(
        "empleado__nombre", "empleado__apellido"
    ).annotate(total_ventas=Sum("total"))
    df_empleado = pd.DataFrame(list(datos_ventas_empleado))
    df_empleado["empleados"] = (
        df_empleado["empleado__nombre"] + " " + df_empleado["empleado__apellido"]
    )
    fig_empleado = px.bar(
        df_empleado,
        x="empleados",
        y="total_ventas",
        # title="Ventas Totales por Empleado",
        color="empleados",
    )
    fig_empleado.update_layout(
        xaxis_title="Empleados", yaxis_title="Total de Ventas en $"
    )

    # Convertir a HTML
    graph_empleado_html = fig_empleado.to_html(full_html=False)

    # Gráfico de ventas totales por mes
    datos_ventas_mes = Venta.objects.values(
        "fechaDeVenta__year", "fechaDeVenta__month", "fechaDeVenta__day"
    ).annotate(total_ventas=Sum("total"))
    print("\n", datos_ventas_mes, "\n")
    df_mes = pd.DataFrame(list(datos_ventas_mes))
    df_mes["fecha"] = pd.to_datetime(
        df_mes["fechaDeVenta__year"].astype(str)
        + "-"
        + df_mes["fechaDeVenta__month"].astype(str)
        + "-01"
    )
    df_mes = df_mes.sort_values("fecha")
    print("\n", df_mes, "\n")
    fig_mes = px.line(
        df_mes,
        x="fechaDeVenta__day",
        y="total_ventas",
        # title="Ventas Totales por Mes",
    )
    fig_mes.update_layout(
        xaxis_title="Dias",
        yaxis_title="Total de Ventas en $",
        # plot_bgcolor="lightgray",
        # paper_bgcolor="white",
    )

    # Convertir a HTMLSS
    graph_mes_html = fig_mes.to_html(full_html=False)

    return render(
        request,
        "estadisticas/estadisticas_ventas.html",
        {"graph_empleado_html": graph_empleado_html, "graph_mes_html": graph_mes_html},
    )
