from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.urls import reverse
from apps.estadisticas.models import Chat
from apps.estadisticas.forms import SeleccionarFechaForm
from apps.ventas.models import Venta, DetalleVenta
from apps.estadisticas import utils
from datetime import date, datetime
from django.db.models.functions import ExtractMonth, ExtractYear
from django.apps import apps
from django.conf import settings
from calendar import monthrange
import plotly.express as px
import pandas as pd
import json
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# IMPROTS LANGCHAIN
from langchain_community.utilities import SQLDatabase  # conexion a la Base de Datos
from langchain_openai import ChatOpenAI  # crear el Modelo de Lenguaje
from langchain.chains import create_sql_query_chain  # Cadena de Consultas SQL
from langchain_core.output_parsers import (
    StrOutputParser,
)  # Manejo de Errores y Validación de Consultas
from langchain_core.prompts import (
    ChatPromptTemplate,
)  # Manejo de Errores y Validación de Consultas

# IMPORTS PARA PDF
from apps.productos.views import crearpdf  # generarPDF()


def response_llm(message, query, response):
    try:
        system_message = utils.response_llm_message.format(
            message=message,
            query=query,
            response=response,
        )
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message},
            ],
        )
        # Procesa la respuesta del modelo y devuelve la etiqueta
        return response.choices[0].message.content
    except openai.AuthenticationError:
        return "Error: Clave API inválida"

    except Exception as e:
        return f"Hubo un error: {str(e)}"

def detect_intention(message):
    """
    Usa OpenAI para detectar si el mensaje del usuario es una consulta SQL o una pregunta general.
    """
    try:
        schema = obtener_schema()
        # Define un prompt que le pide al modelo clasificar la intención
        system_message = utils.detect_intention_message.format(
            schema=schema,
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message},
            ],
        )
        # Procesa la respuesta del modelo y devuelve la etiqueta
        return response.choices[0].message.content
    except openai.AuthenticationError:
        return "Error: Clave API inválida"

    except Exception as e:
        return f"Hubo un error: {str(e)}"


def generate_general_response(message):
    # Genera una respuesta conversacional usando OpenAI
    # Obtener la fecha y hora actuales
    fecha_hoy = datetime.now()

    # Formatear en ISO 8601 con hora
    fecha_iso_hora = fecha_hoy.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        system_message = utils.generate_general_response_message.format(
            fecha_iso_hora=fecha_iso_hora,
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message},
            ],
        )
        results = response.choices[0].message.content
        # Analiza el resultado para ver si se menciona PDF de Producto o Insumo
        if "PDF" in results:
            if "PRODUCTO" in results:
                return "redirect_producto_pdf"
            elif "INSUMO" in results:
                return "redirect_insumo_pdf"

        return results
    except openai.AuthenticationError:
        return "Error: Clave API inválida"

    except Exception as e:
        return f"Hubo un error: {str(e)}"


def generate_sql_response(message):
    # Conecta a la base de datos
    try: 
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        sqlite_db_path = os.path.join(settings.BASE_DIR, "db.sqlite3")
        db = SQLDatabase.from_uri(f"sqlite:///{sqlite_db_path}")

        llm = ChatOpenAI(model="gpt-3.5-turbo")
        chain = create_sql_query_chain(llm, db)
        dialect = db.dialect

        # Genera la consulta y verifica que no modifique datos
        query = chain.invoke({"question": message})

        if "SELECT" not in query:
            raise ValueError("No se permiten consultas que modifiquen datos.")

        system_message = utils.generate_sql_response_message

        prompt = ChatPromptTemplate.from_messages(
            [("system", system_message), ("human", "{query}")]
        ).partial(dialect=db.dialect, message=message)

        # Combinando la generación y validación
        validation_chain = prompt | llm | StrOutputParser()
        full_chain = {"query": chain} | validation_chain

        # Ejecutar la consulta y validar
        query = full_chain.invoke({"question": f"{message}"})
        results = db.run(query)
        response = response_llm(message, query, results)
        return response
    except Exception as e:
        return f"Hubo un error al procesar la consulta: {str(e)}"

def chatbot(request):
    if request.method == "POST":
        message = request.POST.get("message")
        try:
            # Detecta si el mensaje es una consulta SQL o una conversación general
            intention = detect_intention(message)
            if intention == "SQL":
                response = generate_sql_response(message)
            else:
                response = generate_general_response(message)

                # Revisa si generate_general_response devuelve una indicación de generación de PDF
                if response == "redirect_producto_pdf":
                    pdf = crearpdf()  # Genera el PDF utilizando la función `crearpdf`
                    # Prepara la respuesta con el PDF generado
                    response = HttpResponse(
                        pdf.output(dest="S").encode("latin1"),
                        content_type="application/pdf",
                    )
                    response["Content-Disposition"] = (
                        'attachment; filename="reporteProductos.pdf"'
                    )
                    response["Refresh"] = "0; url=/estadisticas/chatbot/"
                    return response
                elif response == "redirect_insumo_pdf":
                    pdf = (
                        crearpdf()
                    )  # Aquí también podrías utilizar otra función si deseas generar un PDF distinto
                    response = HttpResponse(
                        pdf.output(dest="S").encode("latin1"),
                        content_type="application/pdf",
                    )
                    response["Content-Disposition"] = (
                        'attachment; filename="reporteInsumosFaltantes.pdf"'
                    )
                    response["Refresh"] = "0; url=/estadisticas/chatbot/"
                    return response

        except ValueError as e:
            response = f"Hubo un error: {str(e)}"

        # Guarda el mensaje y la respuesta en la base de datos
        Chat.objects.create(user=request.user, message=message, response=response)

        return redirect("estadisticas:chatbot")

    # Cargar el historial de chat
    historial_chat = Chat.objects.filter(user=request.user).order_by("-created_at")[:3]
    historial_chat = historial_chat[::-1]
    return render(request, "chatbot/chat.html", {"historial_chat": historial_chat})


def obtener_schema():
    # Almacenar el esquema en un diccionario
    schema = {}

    # Iterar a través de todas las aplicaciones registradas
    for app in apps.get_app_configs():
        app_schema = {"nombre": app.name, "modelos": []}

        for model in app.get_models():
            model_schema = {"nombre": model.__name__, "campos": []}

            for field in model._meta.get_fields():
                model_schema["campos"].append(
                    {"nombre": field.name, "tipo": field.get_internal_type()}
                )

            app_schema["modelos"].append(model_schema)

        schema[app.name] = app_schema

    # Convertir el esquema a JSON
    return json.dumps(schema)


# Función para procesar formulario de selección de fecha
def obtener_fecha_seleccionada(request):
    hoy = date.today()
    mes = hoy.month
    anio = hoy.year
    if request.method == "POST":
        form = SeleccionarFechaForm(request.POST)
        if form.is_valid():
            mes = int(form.cleaned_data["mes"])
            anio = int(form.cleaned_data["anio"])
    else:
        form = SeleccionarFechaForm()
    return mes, anio, form


# Gráfico de ventas por categoría y productos en formato Sunburst
def grafico_ventas_por_categoria_y_dia(mes, anio):
    # Filtrar ventas por mes y año, obteniendo la categoría y el nombre del producto
    ventas_mes = (
        DetalleVenta.objects.filter(
            venta__fechaDeVenta__year=anio, venta__fechaDeVenta__month=mes
        )
        .values("producto__categoria", "producto__nombre")
        .annotate(total_ventas=Sum("subTotal"))
    )

    # Verificar si existen datos para evitar errores
    if not ventas_mes.exists():
        return None

    # Convertir los datos a un DataFrame de pandas
    df_ventas = pd.DataFrame(list(ventas_mes))
    df_ventas.rename(
        columns={
            "producto__categoria": "Categoria",
            "producto__nombre": "Producto",
            "total_ventas": "TotalVentas",
        },
        inplace=True,
    )

    # Estandarizar los nombres de categorías
    df_ventas["Categoria"] = df_ventas["Categoria"].replace(
        {
            "panadería": "Panadería",
            "panaderia": "Panadería",
            "pastelería": "Pastelería",
            "pasteleria": "Pastelería",
        }
    )

    # Crear el gráfico sunburst
    fig = px.sunburst(
        df_ventas,
        path=["Categoria", "Producto"],
        values="TotalVentas",
        branchvalues="total",
    )
    fig.update_layout(
        title="Ventas Totales por Categoría y Producto",
    )

    # Convertir el gráfico a HTML
    return fig.to_html(full_html=False)


# Gráfico de ventas totales por empleado
def grafico_ventas_por_empleado():
    datos_ventas_empleado = Venta.objects.values(
        "empleado__nombre", "empleado__apellido"
    ).annotate(total_ventas=Sum("total"))

    df_empleado = pd.DataFrame(list(datos_ventas_empleado))
    df_empleado["empleados"] = (
        df_empleado["empleado__nombre"] + " " + df_empleado["empleado__apellido"]
    )
    fig = px.bar(
        df_empleado,
        x="empleados",
        y="total_ventas",
        color="empleados",
    )
    fig.update_layout(
        xaxis_title="Empleados",
        yaxis_title="Total de Ventas en $",
        xaxis=dict(tickvals=[]),
    )
    return fig.to_html(full_html=False)


# Gráfico de ventas totales por mes
def grafico_ventas_totales_por_mes(mes, anio):
    # Filtrar ventas según el mes y año seleccionados
    datos_ventas_mes = (
        Venta.objects.filter(fechaDeVenta__year=anio, fechaDeVenta__month=mes)
        .values("fechaDeVenta__day")
        .annotate(total_ventas=Sum("total"))
    )

    # Convertir a DataFrame
    df_mes = pd.DataFrame(list(datos_ventas_mes))

    # Obtener el último día del mes para definir el rango de fechas
    ultimo_dia = monthrange(anio, mes)[1]

    # Generar una columna de fecha completa para ordenar correctamente los datos
    df_mes["fecha"] = pd.to_datetime(
        f"{anio}-{mes:02d}-" + df_mes["fechaDeVenta__day"].astype(str)
    )

    # Crear un rango de días para el mes completo usando el último día obtenido
    dias_del_mes = pd.date_range(
        start=f"{anio}-{mes:02d}-01", end=f"{anio}-{mes:02d}-{ultimo_dia}"
    )

    # Asegurar que se tienen todas las fechas y llenar valores faltantes
    df_mes = (
        df_mes.set_index("fecha")
        .reindex(dias_del_mes)
        .fillna(method="ffill")
        .reset_index()
    )
    df_mes.rename(columns={"index": "fecha"}, inplace=True)

    # Crear gráfico
    fig = px.line(
        df_mes,
        x="fecha",
        y="total_ventas",
    )
    fig.update_layout(
        xaxis_title="Días",
        yaxis_title="Total de Ventas en $",
    )

    # Convertir el gráfico a HTML
    return fig.to_html(full_html=False)


# Vista principal de estadísticas de ventas
def estadisticas_ventas(request):
    mes, anio, form = obtener_fecha_seleccionada(request)

    graph_categorias_html = grafico_ventas_por_categoria_y_dia(mes, anio)
    if not graph_categorias_html:
        return render(
            request,
            "estadisticas/estadisticas_ventas.html",
            {"mensaje": "No hay datos de ventas disponibles.", "form": form},
        )

    graph_empleado_html = grafico_ventas_por_empleado()
    graph_mes_html = grafico_ventas_totales_por_mes(mes, anio)

    # AGREGADO POR LUCAS
    # Obtener el empleado con más ventas en el mes y año actual
    empleado = (
        Venta.objects.annotate(
            month=ExtractMonth("fechaDeVenta"), year=ExtractYear("fechaDeVenta")
        )
        .filter(month=date.today().month, year=date.today().year)
        .values("empleado__nombre")
        .annotate(total_ventas=Count("id"))  # Contar las ventas
        .order_by("-total_ventas")  # Ordenar descendentemente
        .first()  # Obtener el empleado con más ventas
    )

    # Ventas del día actual
    ventas_diarias = Venta.objects.filter(fechaDeVenta=date.today()).aggregate(
        total_diario=Sum("total")
    )
    total_diario = (
        ventas_diarias["total_diario"] if ventas_diarias["total_diario"] else 0
    )

    # Ventas del mes actual
    ventas_mensuales = Venta.objects.filter(
        fechaDeVenta__year=date.today().year, fechaDeVenta__month=date.today().month
    ).aggregate(total_mensual=Sum("total"))
    total_mensual = (
        ventas_mensuales["total_mensual"] if ventas_mensuales["total_mensual"] else 0
    )

    # Producto más vendido en el mes y año actual
    producto_mas_vendido = (
        DetalleVenta.objects.annotate(
            month=ExtractMonth("venta__fechaDeVenta"),
            year=ExtractYear("venta__fechaDeVenta"),
        )
        .filter(month=date.today().month, year=date.today().year)
        .values("producto__nombre")
        .annotate(total_vendido=Sum("cantidad"))
        .order_by("-total_vendido")
        .first()  # Obtener el primer resultado, que será el producto más vendido
    )

    context = {
        "graph_categorias_html": graph_categorias_html,
        "graph_empleado_html": graph_empleado_html,
        "graph_mes_html": graph_mes_html,
        "empleado": empleado,
        "total_diario": total_diario,
        "total_mensual": total_mensual,
        "producto_mas_vendido": producto_mas_vendido,
        "form": form,
    }
    return render(request, "estadisticas/estadisticas_ventas.html", context)
