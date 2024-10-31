from datetime import date
from django.shortcuts import render
from django.db.models import Sum
from apps.ventas.models import Venta, DetalleVenta
import plotly.express as px
import pandas as pd


def estadisticas_ventas(request):
    # --- Grafico de ventas totales por empleado  --- #
    datos_ventas_empleado = Venta.objects.values( # pylint: disable=no-member
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

    # Se convierte a HTML
    graph_empleado_html = fig_empleado.to_html(full_html=False)

    # --- Grafico de ventas totales por mes  --- #
    datos_ventas_mes = Venta.objects.values( # pylint: disable=no-member
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

    # Se convierte a HTML
    graph_mes_html = fig_mes.to_html(full_html=False)

    # --- Grafico de ventas agrupadas por categoria de productos y dia del mes  --- #
    
    # Se filtra las ventas del mes actual
    hoy = date.today()
    ventas_mes = DetalleVenta.objects.filter( # pylint: disable=no-member
        venta__fechaDeVenta__year=hoy.year,
        venta__fechaDeVenta__month=hoy.month
    ).values(
        'producto__categoria',
        'venta__fechaDeVenta__day'
    ).annotate(
        total_ventas=Sum('subTotal')
    )

    # Convierte los datos a un DataFrame de pandas
    df_ventas = pd.DataFrame(list(ventas_mes))
    df_ventas.rename(columns={
        'producto__categoria': 'Categoria',
        'venta__fechaDeVenta__day': 'Dia',
        'total_ventas': 'TotalVentas'
    }, inplace=True)

    # Unifica las categorias en una sola columna "Categoria_mixed"
    df_ventas['Categoria_mixed'] = df_ventas['Categoria'].replace({
        'panadería': 'panadería',
        'panaderia': 'panadería',
        'pastelería': 'pastelería',
        'pasteleria': 'pastelería',
    })
    
    # Se agrupa para evitar duplicados en el índice y columnas
    df_ventas = df_ventas.groupby(['Categoria_mixed', 'Dia'], as_index=False).sum()

    # Se crea el mapa de calor usando Plotly
    fig = px.imshow(
        df_ventas.pivot(index='Categoria_mixed', columns='Dia', values='TotalVentas'),
        color_continuous_scale='Viridis',
        labels=dict(x="Día del Mes", y="Categoría de Producto", color="Ventas Totales"),
        title="Ventas por Categoría y Día del Mes"
    )
    fig.update_layout(
        xaxis_title="Día del Mes",
        yaxis_title="Categoría de Producto"
    )

    # Se convierte a HTML
    graph_categorias_html = fig.to_html(full_html=False)

    return render(
        request,
        "estadisticas/estadisticas_ventas.html",
        {"graph_empleado_html": graph_empleado_html, "graph_mes_html": graph_mes_html, "graph_categorias_html": graph_categorias_html},
    )
