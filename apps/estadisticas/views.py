from django.shortcuts import render, redirect
from django.db.models import Sum
from apps.estadisticas.models import Chat
from apps.estadisticas.forms import SeleccionarFechaForm
from apps.ventas.models import Venta, DetalleVenta
from apps.estadisticas import utils
from datetime import date, datetime
from django.apps import apps
from django.conf import settings
import plotly.express as px
import pandas as pd
import json
import os
import openai

from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv(".messages")
openai.api_key = os.getenv("OPENAI_API_KEY")

# IMPROTS LANGCHAIN
from langchain_community.utilities import SQLDatabase # conexion a la Base de Datos
from langchain_openai import ChatOpenAI # crear el Modelo de Lenguaje
from langchain.chains import create_sql_query_chain # Cadena de Consultas SQL
from langchain_core.output_parsers import StrOutputParser # Manejo de Errores y Validación de Consultas
from langchain_core.prompts import ChatPromptTemplate # Manejo de Errores y Validación de Consultas

# IMPORTS PARA PDF
from apps.productos import views # generarPDF()

def response_llm(message, query, response):
    print('\n--------- response_llm ---------\n')
    system_message = f"""
        <contexto>
        consutla del usuario: 
        {message}
        query del usuario:
        {query}
        </contexto>
        Responde amablemente en lenguaje natural estos datos resultantes, traduciendolos a lenguaje natural: 
        {response}
        
        - Recuerda usar siempre el simbolo $ para referirte a dinero
        - Si la respuesta incluye un dato en singular, asegúrate de responder en forma singular y gramaticalmente correcta.
        - Evita los campos ID a menos que la "consulta del usuario" lo requiera
        - Una vez respondida la consulta, te quedarás disponible para cualquier otra pregunta sobre los servicios.
        """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message},
        ]
    )
    print('\n--------- response_llm response ---------\n')
    print(response.choices[0].message.content)
    # Procesa la respuesta del modelo y devuelve la etiqueta
    return response.choices[0].message.content

def detect_intention(message):
    """
    Usa OpenAI para detectar si el mensaje del usuario es una consulta SQL o una pregunta general.
    """
    print('\n--------- detect_intention ---------\n')
    schema = obtener_schema()
    # Define un prompt que le pide al modelo clasificar la intención
    system_message = f"""
    Actúa como un clasificador de consultas de usuario. 
    Responde solo con una de las siguientes etiquetas: 
    - "SQL" si el usuario está preguntando por datos específicos o haciendo una consulta de base de datos.
    - "Conversación" si el usuario está haciendo una pregunta general o saludando.
    Interpreta si es sobre SQL guiandote del siguiente schema de base de datos:
    <schema>{schema}</schema>
    No expliques nada adicional. Solo responde con "SQL" o "Conversación".
    """
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message},
        ]
    )
    print('\n--------- detect_intention response ---------\n')
    print(response.choices[0].message.content)
    # Procesa la respuesta del modelo y devuelve la etiqueta
    return response.choices[0].message.content

def generate_general_response(message):
    print('\n--------- generate_general_response ---------\n')
    # Genera una respuesta conversacional usando OpenAI
    # Obtener la fecha y hora actuales
    fecha_hoy = datetime.now()

    # Formatear en ISO 8601 con hora
    fecha_iso_hora = fecha_hoy.strftime('%Y-%m-%dT%H:%M:%S')
    
    system_message = f"""
    Eres un asistente amigable para la Panadería Maná. Estás aquí para ayudar a los clientes con cualquier consulta relacionada con sus servicios y operaciones.
    Trata de ser conciso y claro en tus respuestas, proporcionando la información necesaria sin extenderte demasiado. 
    Pueden pedirte información sobre los siguientes temas:
    -Proveedores
    -Pedidos
    -Detalles de pedido
    -Recepción de pedido
    -Detalle de la recepción del pedido
    -Productos
    -Insumos
    -Empleados
    -Clientes mayoristas
    -Ventas y detalles de ventas
    -Generación de PDF con lista de productos
    Si necesitan información sobre alguno de estos temas, no dudes en preguntar.
    Por otro lado, si te preguntan algo fuera de estos temas, limitate obligatoriamente sobre temas de la panaderia, pero intentarás ofrecer una respuesta amable.
    Una vez respondida la consulta, te quedarás disponible para cualquier otra pregunta sobre los servicios.
    Fecha actual:{fecha_iso_hora}
    """
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ]
    )
    print('\n--------- generate_general_response response ---------\n')
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def generate_sql_response(message):
    print('\n--------- generate_sql_response ---------\n')
    # Conecta a la base de datos
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    sqlite_db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    db = SQLDatabase.from_uri(f'sqlite:///{sqlite_db_path}')
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    chain = create_sql_query_chain(llm, db)
    dialect = db.dialect
    
    # Genera la consulta y verifica que no modifique datos
    query = chain.invoke({"question": message})
    print('\n--------- generate_sql_response query ---------\n')
    print(query)
    
    print('\n--------- generate_sql_response VERIFICACION ---------\n')
    if "SELECT" not in query:
        raise ValueError("No se permiten consultas que modifiquen datos.")
    
    system =""" user's question: {message}
            Double check the user's {dialect} query for common mistakes, including:
            - Using NOT IN with NULL values
            - Using UNION when UNION ALL should have been used
            - Using BETWEEN for exclusive ranges
            - Data type mismatch in predicates
            - Properly quoting identifiers
            - Using the correct number of arguments for functions
            - Casting to the correct data type
            - Using the proper columns for joins
            - do not use LIMIT unless the user requests it

            If there are any of the above mistakes, rewrite the query.
            If there are no mistakes, just reproduce the original query with no further commentary.

            When generating the query, make sure to:
            - Concatenate the 'nombre' and 'apellido' fields directly from 'usuarios_empleado' without using an alias.
            - Use the correct field names as specified without modifying or shortening them.
            - Use descriptions (e.g., 'nombre') instead of foreign key IDs in the query.
            - Before processing any query, ensure that it does not include SQL commands such as DELETE, UPDATE, TRUNCATE, or any instruction that alters data.
            
            Return only the SQL query, without any alias or additional commentary.
            """ # Output the final SQL query only.
        
    prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{query}")]
    ).partial(dialect=db.dialect, message=message)
        
    print('\n--------- prompt ---------\n')
    #print(prompt)
        
    # Combinando la generación y validación
    validation_chain = prompt | llm | StrOutputParser()
    full_chain = {"query": chain} | validation_chain
    
    # Ejecutar la consulta y validar
    query = full_chain.invoke({
        "question": f'{message}'
    })
    print('\n--------- query verficada ---------\n')
    print(query)
    
    results = db.run(query)
    response = response_llm(message, query, results)
    return response

def chatbot(request):
    if request.method == "POST":
        print('\n--------- INICIO DE POST en chatbot_view ---------\n')
        message = request.POST.get("message")
        print(f'\n--------- Mensaje de usuario: {message}  ---------\n')
        try:
            # Detecta si el mensaje es una consulta SQL o una conversación general
            intention = detect_intention(message)
            if intention == "SQL":
                response = generate_sql_response(message)
            else:
                response = generate_general_response(message)
        except ValueError as e:
            response = f"hubo un error: {str(e)}"

        # Guarda el mensaje y la respuesta en la base de datos
        Chat.objects.create(user=request.user, message=message, response=response)
        
        return redirect('estadisticas:chatbot')

    # Cargar el historial de chat
    historial_chat = Chat.objects.filter(user=request.user).order_by("-created_at")[:5]
    historial_chat = historial_chat[::-1]
    return render(request, "chatbot/chat.html", {"historial_chat": historial_chat})


def estadisticas_ventas(request):
    
    
    hoy = date.today()
    mes = hoy.month
    anio = hoy.year
    # --- --- --- Grafico de ventas agrupadas por categoria de productos y dia del mes --- --- --- #

    #print("\n", obtener_schema(), "\n")
    
    # --- NUEVO CODIGO  --- #
    if request.method == "POST":
        form = SeleccionarFechaForm(request.POST)
        if form.is_valid():
            mes = int(form.cleaned_data['mes'])
            anio = int(form.cleaned_data['anio'])
    else:
        form = SeleccionarFechaForm()
    #chatbot(request)
    # Filtrar ventas según el mes y año seleccionado
    ventas_mes = DetalleVenta.objects.filter(
        venta__fechaDeVenta__year=anio,
        venta__fechaDeVenta__month=mes
    ).values(
        'producto__categoria',  
        'venta__fechaDeVenta__day'
    ).annotate(
        total_ventas=Sum('subTotal')
    )

    if not ventas_mes.exists():
        return render(request, 'estadisticas/estadisticas_ventas.html', {
            'mensaje': 'No hay datos de ventas disponibles.',
            'form': form
        })
    
    # Convertir los datos a un DataFrame de pandas
    df_ventas = pd.DataFrame(list(ventas_mes))
    df_ventas.rename(columns={
        'producto__categoria': 'Categoria',
        'venta__fechaDeVenta__day': 'Dia',
        'total_ventas': 'TotalVentas'
    }, inplace=True)

    # Unificar las categorías en "Categoria_mixed"
    df_ventas['Categoria_mixed'] = df_ventas['Categoria'].replace({
        'panadería': 'panadería',
        'panaderia': 'panadería',
        'pastelería': 'pastelería',
        'pasteleria': 'pastelería',
    })
    
    #print("\n", df_ventas, "\n")

    # Agrupar para evitar duplicados
    df_ventas = df_ventas.groupby(['Categoria_mixed', 'Dia'], as_index=False).sum()

    # Crear el mapa de calor usando Plotly
    fig = px.imshow(
        df_ventas.pivot(index='Categoria_mixed', columns='Dia', values='TotalVentas'),
        color_continuous_scale='Viridis',
        labels=dict(x="Día del Mes", y="Categoría de Producto", color="Ventas Totales"),
        # title="Ventas por Categoría y Día del Mes"
    )
    fig.update_layout(
        xaxis_title="Día del Mes",
        yaxis_title="Categoría de Producto"
    )
    
    # Se convierte a HTML
    graph_categorias_html = fig.to_html(full_html=False)
    
    # --- /NUEVO CODIGO  --- #
    
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
        xaxis_title="Empleados",
        yaxis_title="Total de Ventas en $",
        xaxis=dict(tickvals=[]),
    )

    # Se convierte a HTML
    graph_empleado_html = fig_empleado.to_html(full_html=False)

    # --- --- --- Grafico de ventas totales por mes --- ---  --- #
    datos_ventas_mes = Venta.objects.values( # pylint: disable=no-member
        "fechaDeVenta__year", "fechaDeVenta__month", "fechaDeVenta__day"
    ).annotate(total_ventas=Sum("total"))
    #print("\n", datos_ventas_mes, "\n")
    df_mes = pd.DataFrame(list(datos_ventas_mes))
    df_mes["fecha"] = pd.to_datetime(
        df_mes["fechaDeVenta__year"].astype(str)
        + "-"
        + df_mes["fechaDeVenta__month"].astype(str)
        + "-01"
    )
    df_mes = df_mes.sort_values("fecha")
    
    #print("\n", df_mes, "\n")
    
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

    return render(
        request,
        "estadisticas/estadisticas_ventas.html",
        {"graph_empleado_html": graph_empleado_html, "graph_mes_html": graph_mes_html, "graph_categorias_html": graph_categorias_html, "form": form},
    )


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