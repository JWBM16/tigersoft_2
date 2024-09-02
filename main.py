import base64
import hashlib
import io
import os
import sqlite3
import time
from datetime import datetime
from io import BytesIO

import extra_streamlit_components as stx
import pandas as pd
import PIL as pl
import streamlit as st
from streamlit.components.v1 import html
# import streamlit_antd_components as sac
# import streamlit_shadcn_ui as ui
import streamlit_space
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
# from reportlab.pdfgen import canvas
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode
from streamlit_option_menu import option_menu
from streamlit_space import space
from streamlit_vizzu import VizzuChart, Config, Data
from ipyvizzu import Chart, Data, Config, Style, DisplayTarget
from ipyvizzustory import Story, Slide, Step
import agstyler
from agstyler import PINLEFT, PRECISION_TWO, draw_grid

# Configuracion de la pagina
st.set_page_config(layout="wide")

# Ubicacion de la image dentro del directorio libreria OS
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path_taller_img = os.path.join(current_dir, "assets", "auto_2.png")
secuencia_img_path = os.path.join(current_dir, "assets", "secuencia.png")
portada_img_path = os.path.join(current_dir, "assets", "tiger_soft.jpeg")
tiger_peq_path = os.path.join(current_dir, "assets", "tiger_soft_sin_fondo_peq.png")

# Modificacion y ajuste de la imagen
taller_img = Image.open(image_path_taller_img)
secuencia_img = Image.open(secuencia_img_path)
portada_img = Image.open(portada_img_path)
tiger_peq_img = Image.open(tiger_peq_path)

# Obtener las dimensiones originales
ancho_original, alto_original = portada_img.size

# Calcular las nuevas dimensiones (disminuir en 15%)
nuevo_ancho = int(ancho_original * 0.60)
nuevo_alto = int(alto_original * 0.55)

portada_reducida = portada_img.resize((nuevo_ancho, nuevo_alto))

resized_im = taller_img.resize(
    (round(taller_img.size[0] * 0.40), round(taller_img.size[1] * 0.40))
)

# Encode the image to base64
buffered1 = io.BytesIO()
taller_img.save(buffered1, format="PNG")
img_str = base64.b64encode(buffered1.getvalue()).decode()

buffered2 = io.BytesIO()
img_str_car_filled = base64.b64encode(buffered2.getvalue()).decode()

buffered3 = io.BytesIO()
secuencia_img.save(buffered3, format="PNG")
secuencia_img_def = base64.b64encode(buffered3.getvalue()).decode()

buffered4 = io.BytesIO()
portada_reducida.save(buffered4, format="PNG")
portada_img_def = base64.b64encode(buffered4.getvalue()).decode()

buffered4 = io.BytesIO()
tiger_peq_img.save(buffered4, format="PNG")
tiger_peq_img = base64.b64encode(buffered4.getvalue()).decode()

# Oculta el menu por Default de Streamlit
hide_st_text = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_text, unsafe_allow_html=True)
st.write(
    "<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True
)
padding = 0


# TODO: INICIO DEL 1ER INJERTO DEL ARCHIVO mecanica_test.py
if "data" not in st.session_state:
    st.session_state.data = []

# Inicializar el estado del diálogo en la sesión
if "dialog_visible" not in st.session_state:
    st.session_state.dialog_visible = False

# BUDGET: Inicializar st.session_state.df_modal si no existe
if "df_modal" not in st.session_state:
    st.session_state.df_modal = pd.DataFrame()


# FIXME: INCLUSION DE FUNCION QUE GUARDA VALORES EN TABLAS DEL PRESUPUESTO
def generar_siguiente_id_presupuesto():
    # Conectar a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()

    # Ejecutar la consulta para obtener el último IdPresupuesto
    cursor.execute("SELECT MAX(IdPresupuesto) FROM Presupuesto")
    last_id = cursor.fetchone()[0]

    # Cerrar la conexión
    # conn.close()

    if last_id is None:
        # Si no hay ningún ID, comenzar con 'P-0001'
        return "P-0001"
    else:
        # Extraer el número del último ID y sumar 1
        last_number = int(last_id.split("-")[1])
        new_number = last_number + 1
        return f"P-{new_number:04d}"


def presptosql(
    propietario_select,
    fecha_formateada,
    vehiculos_select,
    total_column_ventas,
    total_column_costos,
    ganancia,
    elemento_telefono,
    elemento_email,
    elemento_cliente_id,
    elemento_vehiculo_id,
    elemento_observaciones_veh,
):
    usuario = propietario_select
    fecha = fecha_formateada
    vehiculo = vehiculos_select
    ventas = total_column_ventas
    costos = total_column_costos
    profit = ganancia
    telefono = elemento_telefono
    email = elemento_email
    df_presup = st.session_state.df_detalle.copy()
    cliente_id = int(elemento_cliente_id)  # Convertir a entero
    veh_id = int(elemento_vehiculo_id)  # Convertir a entero
    observaciones = elemento_observaciones_veh

    # Función para generar el siguiente IdPresupuesto
    def generar_id_presupuesto():
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(IdPresupuesto) FROM Presupuesto")
        last_id = cursor.fetchone()[0]
        if last_id is None:
            return "P-0001"
        else:
            last_number = int(last_id.split("-")[1])
            new_number = last_number + 1
            return f"P-{new_number:04d}"

    # Ejemplo de inserción de un nuevo presupuesto y detalles
    nuevo_id_presupuesto = generar_id_presupuesto()
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO Presupuesto (IdPresupuesto, vehiculo_id, Cliente_id, NombreCliente, Telefono, email, DatosVehiculos, Fecha, TotalCosto, TotalVenta, Ganancia, Observaciones, Estatus)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            nuevo_id_presupuesto,
            veh_id,
            cliente_id,
            usuario,
            telefono,
            email,
            vehiculo,
            fecha,
            costos,
            ventas,
            ganancia,
            observaciones,
            "Creado",
        ),
    )

    # Insertar detalles del presupuesto desde el dataframe
    for index, row in df_presup.iterrows():
        cursor.execute(
            """
        INSERT INTO DetallePresupuesto (IdPresupuesto, Descripcion, Costo, PrecioVenta)
        VALUES (?, ?, ?, ?)
        """,
            (
                nuevo_id_presupuesto,
                row["Repuesto / Mano de Obra"],
                row["Costo en USD"],
                row["Precio Venta en USD"],
            ),
        )

    # Guardar los cambios y cerrar la conexión
    conn.commit()
    # conn.close()
    st.rerun()


# BUDGET: FIN DE BLOQUE NUEVO 2024-08-06


# Convertir la lista en un DataFrame
def get_dataframe(data):
    df_detalle = pd.DataFrame(
        data,
        columns=[
            "ID",
            "Repuesto / Mano de Obra",
            "Costo en USD",
            "Precio Venta en USD",
        ],
    )
    df_detalle = df_detalle.drop(columns=["ID"])

    return df_detalle


# Inicializar el DataFrame en el estado de sesión si no existe
if "df_detalle" not in st.session_state:
    st.session_state.df_detalle = get_dataframe(st.session_state.data)
if "selected_index" not in st.session_state:
    st.session_state.selected_index = (
        len(st.session_state.df_detalle) - 1
        if len(st.session_state.df_detalle) > 0
        else 0
    )

if "next_id" not in st.session_state:
    st.session_state.next_id = 1


def agregar_repuesto(data, selectrep, costorep, preciorep):
    # BUDGET: CAMBIO CODIGO 2024-08-6
    nuevo_repuesto = [
        st.session_state.next_id,
        selectrep,
        costorep,
        preciorep,
    ]
    data.append(nuevo_repuesto)
    st.session_state.next_id += 1
    return data


# Funciones para subir y bajar filas
def subir_fila(df_detalle, index):
    if index > 0:
        df_detalle.iloc[index], df_detalle.iloc[index - 1] = (
            df_detalle.iloc[index - 1].copy(),
            df_detalle.iloc[index].copy(),
        )
        st.session_state.selected_index -= 1
    return df_detalle


def bajar_fila(df_detalle, index):
    if index < len(df_detalle) - 1:
        df_detalle.iloc[index], df_detalle.iloc[index + 1] = (
            df_detalle.iloc[index + 1].copy(),
            df_detalle.iloc[index].copy(),
        )
        st.session_state.selected_index += 1
    return df_detalle


# Función para eliminar la última fila del DataFrame
def eliminar_ultima_fila(df_detalle):
    if len(df_detalle) > 0:
        df_detalle = df_detalle.drop(df_detalle.index[-1]).reset_index(drop=True)
        if st.session_state.selected_index >= len(df_detalle):
            st.session_state.selected_index = (
                len(df_detalle) - 1 if len(df_detalle) > 0 else 0
            )
            
    return df_detalle


# BUDGET: 2 LINEAS INCLUIDAS 2024-0806

# Carga de datos a una lista desde la base de datos jhotem.db
# Conectar a la base de datos
conn = sqlite3.connect("jhotem.db")
cursor = conn.cursor()

# BUDGET: query cambiado 2024-08-06
# Definir la consulta SQL en Vehiculos
query = """
    SELECT 
        v.vehiculos_id, 
        c.id AS cliente_id,
        c.nombre, 
        c.apellido, 
        c.telefono, 
        c.correo_electronico,
        c.cedula,
        v.marca, 
        v.modelo, 
        v.year, 
        v.placa, 
        v.fecha_entrada, 
        v.observaciones
    FROM 
        vehiculos v
    JOIN 
        clientes c ON v.cliente_id = c.id
"""

# Ejecutar la consulta y cargar los resultados en un DataFrame
df = pd.read_sql_query(query, conn)
# print(df.head(10))

# Crear una nueva columna 'nombre_completo' que combine 'nombre' y 'apellido' con un espacio
df = df.assign(nombre_completo=df["nombre"] + " " + df["apellido"])

# Eliminar las columnas 'nombre' y 'apellido' si no las necesitas
df = df.drop(columns=["nombre", "apellido"])

# Crear una nueva columna 'vehiculo_completo' que combine 'marca', 'modelo', 'year' con un espacio
df = df.assign(
    vehiculo_completo=df["marca"]
    + " "
    + df["modelo"]
    + " "
    + df["year"].astype(str)
    + " PLACA: "
    + df["placa"]
)

# FIXME: QUERY DE TABLA REPORTES
# Eliminar las columnas 'marca', 'modelo' y 'year' si no las necesitas
df = df.drop(columns=["marca", "modelo", "year"])

df_filtered = pd.DataFrame()


propietario_select_cambio = False

opciones_propietario = df["nombre_completo"].unique()
opciones_propietario = pd.Series(opciones_propietario)
opciones_propietario = opciones_propietario.sort_values()

# ---- QUERY Y DATAFRAME EN TABLA REPUESTOS ---#
# Conectar a la base de datos
conn = sqlite3.connect("jhotem.db")
cursor = conn.cursor()

query_rep = """ SELECT * FROM repuestos """

# Ejecutar la consulta y cargar los resultados en un DataFrame
df_repuestos = pd.read_sql_query(query_rep, conn)

opciones_repuestos = df_repuestos["Descripcion"].unique()
opciones_repuestos = pd.Series(opciones_repuestos)
opciones_repuestos = opciones_repuestos.sort_values()

df_filtered_repuestos = pd.DataFrame()
repuesto_select_cambio = False
# --- FIN DE QUERY Y DATAFRAME EN TABLA REPUESTOS ---#


# ---- TEST PANDAS SQL ----#
# Consulta para obtener los datos de la tabla vehiculos junto con el nombre del cliente
cursor.execute(
    """
    SELECT v.vehiculos_id, c.nombre, c.apellido, v.marca, v.modelo, v.year, v.placa, v.fecha_entrada, v.observaciones
    FROM vehiculos v
    JOIN clientes c ON v.cliente_id = c.id
"""
)
filas = cursor.fetchall()  # En filas no se obtiene el cliente Id
# conn.close()


# Nueva lista para almacenar los nombres y apellidos unidos
lista_1 = [f"{item[1]} {item[2]}" for item in filas]
# ---- FIN TEST PANDAS SQL ----#

# Obtener la fecha actual
fecha_actual = datetime.now()

# Formatear la fecha en el formato DD/MM/YYYY
fecha_formateada = fecha_actual.strftime("%Y-%m-%d")

# BUDGET: Inclusion de todo un bloque de funciones y variable 2024-08-06

# Conectar con la tabla 'Presupuestos'
conn = sqlite3.connect("jhotem.db")

# FIXME: Consulta SQL para obtener todos los datos de la tabla Presupuesto
query = "SELECT * FROM Presupuesto"

# Ejecutar la consulta y cargar los resultados en un DataFrame
df_presupuestos = pd.read_sql_query(query, conn)

# Filtrar el DataFrame para obtener los registros con Estatus 'Aprobado'
df_aprobados = df_presupuestos[df_presupuestos["Estatus"] == "Aprobado"]

# Filtrar el DataFrame para obtener los registros con Estatus 'Creado'
df_creados = df_presupuestos[df_presupuestos["Estatus"] == "Creado"]

# APROBADOS - Obtener los totales de las columnas 'Costo' y 'PrecioVenta' Presupuestos aprobados
# Datos para las Metric Cards
valor_total_costo = df_aprobados["TotalCosto"].sum()
valor_total_precio_venta = df_aprobados["TotalVenta"].sum()
valor_total_ganancia = valor_total_precio_venta - valor_total_costo

calculo_porcentaje_ganancia = valor_total_ganancia / valor_total_costo

formatted_valor_total_precio_venta = f"${valor_total_precio_venta:,.2f}"
formatted_valor_total_costo = f"${valor_total_costo:,.2f}"
formatted_valor_total_ganancia = f"${valor_total_ganancia:,.2f}"
formatted_margen_ganancia = f"{calculo_porcentaje_ganancia:.2%}"

# SIN APROBAR -Obtener los totales de las columnas 'Costo' y 'PrecioVenta'
# Datos para las Metric Cards
valor_total_precio_venta_creados = df_creados["TotalVenta"].sum()
valor_total_costo_creados = df_creados["TotalCosto"].sum()
valor_total_ganancia_creados = valor_total_precio_venta_creados - valor_total_costo_creados

# print (valor_total_precio_venta_creados)
# print(valor_total_costo_creados)
# print(valor_total_ganancia_creados)


calculo_porcentaje_ganancia_creados = (
    valor_total_ganancia_creados / valor_total_costo_creados
)

formatted_valor_total_precio_venta_creados = f"${valor_total_precio_venta_creados:,.2f}"
formatted_valor_total_costo_creados = f"${valor_total_costo_creados:,.2f}"
formatted_valor_total_ganancia_creados = f"${valor_total_ganancia_creados:,.2f}"
formatted_margen_ganancia_creados = f"{calculo_porcentaje_ganancia_creados:.2%}"

# formatted_valor_margen_ganancia
# Incluir los estilos CSS directamente en el archivo Python
st.markdown(
    """
<style>
.green-header {
    background-color: green !important;
    color: white !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Configurar las opciones del grid
formatter = {
    "IdPresupuesto": ("Presupuesto Id", {"width": 100, "pinned": "left"}),
    "vehiculo_id": ("Veh Id", {"width": 40}),
    "Cliente_id": ("Cliente", {"width": 80}),
    "NombreCliente": ("Propietario", {"width": 150}),
    "Telefono": ("Telf", {"width": 80}),
    "email": ("Email", {"width": 80}),
    "DatosVehiculos": ("Datos Vehiculo", {"width": 150}),
    "Fecha": ("Fecha", {"width": 100}),
    "TotalCosto": (
        "Total Costo    ",
        {
            "type": ["numericColumn"],
            "precision": 2,
            "filterable": True,
            "width": 100,
            "headerClass": "green-header",
        },
    ),
    "TotalVenta": (
        "Total Presupuesto",
        {"type": ["numericColumn"], "precision": 2, "filterable": True, "width": 100},
    ),
    
    "Ganancia": (
        "Ganancia",
        {"type": ["numericColumn"], "precision": 2, "filterable": True, "width": 100},
    ),
    "Observaciones": ("Observaciones", {"width": 200}),
    "Estatus": ("Estatus", {"width": 80}),
}


def borrar_presupuesto(id_presupuesto):
    # Conectar a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()

    try:
        # Eliminar registros asociados en DetallePresupuesto
        cursor.execute(
            """
        DELETE FROM DetallePresupuesto
        WHERE IdPresupuesto = ?
        """,
            (id_presupuesto,),
        )

        # Eliminar el registro en Presupuesto
        cursor.execute(
            """
        DELETE FROM Presupuesto
        WHERE IdPresupuesto = ?
        """,
            (id_presupuesto,),
        )

        # Confirmar los cambios
        conn.commit()
        print(
            f"Presupuesto con IdPresupuesto {id_presupuesto} y sus detalles han sido eliminados."
        )

    except sqlite3.Error as e:
        print(f"Error al eliminar el presupuesto: {e}")
        conn.rollback()

    finally:
        # Cerrar la conexión a la base de datos
        # conn.close()
        st.rerun()


def aprobar_presupuesto(id_presupuesto):
    # Conectar a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()

    try:
        # Actualizar el campo "Estatus" a "Aprobado" para el IdPresupuesto dado
        cursor.execute(
            """
        UPDATE Presupuesto
        SET Estatus = 'Aprobado'
        WHERE IdPresupuesto = ?
        """,
            (id_presupuesto,),
        )

        # Confirmar los cambios
        conn.commit()
        print(f"Presupuesto con IdPresupuesto {id_presupuesto} ha sido aprobado.")

    except sqlite3.Error as e:
        print(f"Error al aprobar el presupuesto: {e}")
        conn.rollback()

    finally:
        # Cerrar la conexión a la base de datos
        # conn.close()
        st.rerun()


@st.dialog(" ", width="large")
def advertencia(presupuesto_id):
    budget_id = presupuesto_id
    with st.container(height=80, border=False):
        st.markdown(
            """
        <div style="text-align: center; font-size: 34px; color: red; font-weight: bold;">
            <h2 style="font-size: 34px; color: red; font-weight: bold;">
                <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" fill="currentColor" class="bi bi-exclamation-octagon" viewBox="0 0 16 16">
                    <path d="M4.54.146A.5.5 0 0 1 4.893 0h6.214a.5.5 0 0 1 .353.146l4.394 4.394a.5.5 0 0 1 .146.353v6.214a.5.5 0 0 1-.146.353l-4.394 4.394a.5.5 0 0 1-.353.146H4.893a.5.5 0 0 1-.353-.146L.146 11.46A.5.5 0 0 1 0 11.107V4.893a.5.5 0 0 1 .146-.353zM5.1 1 1 5.1v5.8L5.1 15h5.8l4.1-4.1V5.1L10.9 1z"/>
                    <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/>
                </svg> ADVERTENCIA 
                <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" fill="currentColor" class="bi bi-exclamation-octagon" viewBox="0 0 16 16">
                    <path d="M4.54.146A.5.5 0 0 1 4.893 0h6.214a.5.5 0 0 1 .353.146l4.394 4.394a.5.5 0 0 1 .146.353v6.214a.5.5 0 0 1-.146.353l-4.394 4.394a.5.5 0 0 1-.353.146H4.893a.5.5 0 0 1-.353-.146L.146 11.46A.5.5 0 0 1 0 11.107V4.893a.5.5 0 0 1 .146-.353zM5.1 1 1 5.1v5.8L5.1 15h5.8l4.1-4.1V5.1L10.9 1z"/>
                    <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/>
                </svg>
            </h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with st.container(height=200, border=True):
        streamlit_space.space(container=None, lines=3)
        st.markdown(
            f"""
        <p style="font-size: 16px; color: red; font-weight: bold; text-align: center;">
            Esta a punto de borrar el registro N° {budget_id}, esta seguro?
        </p>
        """,
            unsafe_allow_html=True,
        )

    with st.container(height=80, border=False):
        (
            adv_izq,
            adv_cent,
            adv_der,
            adv_uno,
        ) = st.columns(
            [
                1,
                2,
                2,
                1,
            ]
        )
        with adv_cent:
            if st.button(" Si, Borrar ✅", key="adv_button_delete"):
                with st.spinner("Borrando registro..."):
                    time.sleep(5)
                st.write("Borrando Presupuesto")
                time.sleep(5)
                borrar_presupuesto(budget_id)
            else:
                with adv_der:
                    st.markdown(
                        """
                                    <p style="color:blue; font-size:14px; font-weight:bold; text-align:center;">
                                        Para cerrar oprima 'Esc' o marque arriba la 'X'
                                    </p>
                                    """,
                        unsafe_allow_html=True,
                    )


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None


# Columnas principales del Layout
col1, col2 = st.columns([1, 5])

selected = []


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login(username, password):
    if username in users_db and users_db[username] == hash_password(password):
        # st.session_state.logged_in = True
        st.session_state.username = username
        return True
    return False


def logout():
    st.toast("Cerrando sesión!")
    time.sleep(1)
    st.toast("Desconectando de la Base de Datos!")
    time.sleep(1)
    st.toast("Hasta luego!", icon="👋")
    time.sleep(1)
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.page = "log_in"
    st.rerun()

# Conectar a la base de datos SQLite
conn = sqlite3.connect('jhotem.db')
cursor = conn.cursor()

# Consultar los usuarios activos
cursor.execute("SELECT usuario, clave FROM usuarios WHERE estatus = 'activo'")
usuarios_activos = cursor.fetchall()

# Crear la base de datos de usuarios simulada
users_db = {}
for usuario, clave in usuarios_activos:
    users_db[usuario] = hash_password(clave)

# Base de datos de usuarios simulada
# users_db = {
#     "usuario1": hash_password("prueba123"),
#     "usuario2": hash_password("prueba123"),
# }


def login_incorrect():
    st.toast("Usuario o contraseña incorrectos", icon="❌")
    time.sleep(0.5)
    st.toast("Por favor corrija la informacion ingresada")


def login_correct():
    st.toast("Login exitoso!", icon="🎉")
    time.sleep(0.5)

# Abrimos un placeholder
placeholder = st.empty()

def novedades():
    with placeholder.container():
        nov_1, nov_2, nov_3 = st.columns([2, 3, 2])
        with nov_2:
            with st.container(height=580, border=False):
                with st.container(height=570, border=True):
                    streamlit_space.space(container=None, lines=3)
                    
                    st.markdown(
    f"""
    <div style='display: flex; align-items: center; justify-content: center; flex-direction: column; width: 100%;'>
        <div style='display: flex; align-items: center; justify-content: center; width: 80%; margin: 0 10%;'>
            <div style='margin-right: 20px;'>
                <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Impact:400,800&display=swap">
                <div style='font-size: 30px; font-weight: 900; color: blue; font-family: "Arial", sans-serif; text-align: center; position: relative;'>
                    Ti<span style='color: #ea882a;'>i</span>gerSoft<span style='font-size: 30px;'></span><sup>&copy;</sup>
                </div>
            </div>
            <div style='margin-right: 20px;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="blue" class="bi bi-arrow-right" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8"/>
                </svg>
            </div>
            <div>
                <div style='display: flex; align-items: center; color: blue; font-size: 12px; font-weight: bold;'>
                    <img src="data:image/png;base64,{img_str}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; border: 2px solid black;">
                    Auto Diagnostico J.M.R.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
                    # Nota esto agrega un subrayado en el penultimo div de arriba:
                    # <hr style='width: 80%; border: 2px solid blue; margin: 20px 10% 0 10%;'>
                    
                    streamlit_space.space(container=None, lines=2)

                    st.markdown(
                        """
                        <p style='text-align: center; color: grey; font-size: 16px;'>
                            Modulos activos: <span style='font-weight: bold; color: blue;'>4</span>
                        </p>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        """
                        <p style='text-align: center; color: gray; font-size: 16px;'>
                            Secuencia de carga de datos: <span style='font-weight: bold; color: blue;'></span>
                        </p>
                        """,
                        unsafe_allow_html=True,
                    )
                    streamlit_space.space(container=None, lines=2)
                    

                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: center;">
                            <img src="data:image/png;base64,{secuencia_img_def}" />
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    streamlit_space.space(container=None, lines=3)
                    
                    st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <img src="data:image/png;base64,{tiger_peq_img}" style="width: 87px; height: 103px; margin-right: 20px;" />
                        <div style="display: flex; flex-direction: column; align-items: center;">
                            <p style='text-align: center; color: grey; font-size: 24px;'>
                                Version: <span style='font-weight: bold; color: blue;'>1.0</span>
                            </p>
                            <p style='text-align: center; color: grey; font-size: 12px;'>
                                Powered by <span style='font-weight: bold; color: blue;'>White Labs Technologies</span>
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
)

                    streamlit_space.space(container=None, lines=3)

                    st.session_state.logged_in = True

                    time.sleep(5)
                    st.rerun()


# Páginas de la aplicación
def login_page():
    with placeholder.container():
        trip_1, trip_2 = st.columns([2, 2])
        with trip_2:
            # with col2:
            with st.container(height=700, border=False):

                # with log_2:
                with st.container(height=600, border=False):
                    log_1, log_2, log_3 = st.columns([1, 5, 1])
                    with log_1:
                        streamlit_space.space(container=None, lines=1)
                        
                        # st.markdown(
                        #     """
                        #     <div style="width: 3px; height: 540px; background-color: blue; margin: 0 auto;"></div>
                        #     """,
                        #     unsafe_allow_html=True,
                        # )
                    with log_2:
                        streamlit_space.space(container=None, lines=1)
                        st.markdown(
    """
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Impact:400,800&display=swap">
    <div style='font-size: 42px; font-weight: 900; color: blue; font-family: "Arial", sans-serif; text-align: center; width: 100%;'>
        <div style='display: inline-block; border-bottom: 3px solid black; padding-bottom: 1px; margin-bottom: -2px;'>
            Ti<span style='color: #ea882a;'>i</span>gerSoft<span style='font-size: 52px;'></span><sup>&copy;</sup>
            <span style='font-size: 10px; color: black; margin-left: 5px; vertical-align: baseline;'>v 1.0</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
                        streamlit_space.space(container=None, lines=1)

                        st.markdown(
                            """
                                <p style='text-align: center; color: grey; font-size: 12px;'>
                                    Licencia <span style='font-weight: bold; color: blue;'>Premium</span> a nombre de Auto Diagnóstico J.M.R.
                                </p>
                                """,
                            unsafe_allow_html=True,
                        )
                        st.header("Log in")
                        username = st.text_input(
                            "Usuario", on_change=None, key="prueba_usuario"
                        )

                        password = st.text_input(
                            "Contraseña",
                            on_change=None,
                            key="prueba_clave",
                            type="password",
                        )
                        boton_estilo = """
                                <style>
                                .stButton {
                                display: flex;
                                justify-content: center;
                                }
                                .stButton button {
                                background-color: blue !important;
                                color: white !important;
                                width: 250px !important;
                                height: 50px !important;
                                font-size: 24px !important;
                                }
                                </style>
                                """
                        # Aplicar el estilo CSS
                        st.markdown(boton_estilo, unsafe_allow_html=True)

                        if st.button("Iniciar sesión"):
                            if login(username, password) is True:
                                login_correct()
                                # st.session_state.logged_in = False
                                st.session_state.page = "Novedades"
                                st.rerun()

                            else:
                                with log_2:
                                    login_incorrect()
                        # with log_2:
                        streamlit_space.space(container=None, lines=2)

                        st.markdown(
                            """
                                        <p style='text-align: center; color: grey; font-size: 14px;'>
                                            Copyright © 2024 <span style='font-weight: bold; color: blue;'>White Labs Technologies LLC</span>. All rights reserved
                                        </p>
                                        """,
                            unsafe_allow_html=True,
                        )
        with trip_1:
            with st.container(height=700, border=False):
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; justify-content: flex-end; height: 100%;">
                        <div style="width: 5px; height: 100%; background-color: lightgray; margin-left: 10px;"></div>
                        <img src="data:image/png;base64,{portada_img_def}" style="margin-left: 10px; border: 3px solid #ea882a; border-radius: 10px;" />
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# Abrimos un placeholder
placeholder = st.empty()


if st.session_state.logged_in:
    # Columna del Menu y seteo de sus botones
    with col1:
        with st.container(height=635, border=True):
            st.markdown(
                """
                <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Impact:400,800&display=swap">
                <div style='font-size: 28px; font-weight: 900; color: blue; font-family: "Arial", sans-serif; text-align: center; position: relative;'>
                    Ti<span style='color: #ea882a;'>i</span>gerSoft<span style='font-size: 36px;'></span><sup>&copy;</sup>
                    <span style='font-size: 10px; color: black; margin-left: 5px;'></span>
                    <hr style='position: absolute; bottom: -5px; left: -5px; right: -4px; border: 1px solid black; margin: 0;'>
                </div>
                """,
                unsafe_allow_html=True,
            )
            streamlit_space.space(container=None, lines=3)
            selected = option_menu(
                menu_title=None,
                options=[
                    "Presupuestos",
                    "Repuestos",
                    "Vehiculos",
                    "Clientes",
                    "Ajustes",
                    "Log-out",
                ],  # Text you like to see
                icons=[
                    "cash-coin",
                    "wrench-adjustable",
                    "car-front-fill",
                    "person-vcard",
                    "gear-wide-connected",
                    "box-arrow-right",
                ],  # bootstrap icon you like to use from https://icons.getbootstrap.com/
                default_index=0,
                styles={
                    "container": {
                        "padding": "0!important",
                        "background-color": "#fafafa",
                    },
                    "icon": {"color": "white", "font-size": "18px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#eee",
                    },
                    "nav-link-selected": {
                        "background-color": "#0000FF",
                        "color": "white",
                    },
                    "nav-link-selected-icon": {
                        "color": "black",
                    },
                },
            )
            streamlit_space.space(container=None, lines=12)
            
            
            st.markdown(
                        """
                        <p style='text-align: center; color: grey; font-size: 11px;'>
                            Powered by <span style='font-weight: bold; color: blue;'>White Labs Technologies</span>
                        </p>
                        """,
                        unsafe_allow_html=True,
                    )


# Uso del session state para el manejo de paginas (distribuidas en funciones)
if selected and selected != []:
    st.session_state.page = selected

# Inicializamos el estado de sesión para la página si no existe
if "page" not in st.session_state:
    st.session_state.page = "log_in"
# elif st.session_state.page:
#     st.session_state.page = "Novedades"
#     time.sleep(10)
#     st.rerun()


# Pagina Presupuestos
def presupuestos():
    
    def toast():
        st.toast("Optimizando")
        time.sleep(0.5)
        st.toast("Haciendo los cambios en la Base de Datos")
        time.sleep(0.5)
        st.toast("Listo", icon="🎉")
    
    with placeholder.container():
        with col2:
            with st.container(height=70, border=True):
                left_co, cent_co, last_co = st.columns(3)
                with left_co:
                    st.markdown(
                        f"""
                        <div style='display: flex; align-items: center; color: blue; font-size: 20px; font-weight: bold;'>
                            <img src="data:image/png;base64,{img_str}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; border: 2px solid black;">
                            Auto Diagnóstico J.M.R.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with last_co:
                    st.markdown(
                        f"""
    <div style="display: flex; align-items: center; justify-content: flex-end;">
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
            <span style="color: blue; font-size: 16px; font-weight: bold;">Modulo: Presupuestos</span>
            <span style="color: black; font-size: 14px; font-weight: bold;">Fecha: {fecha_formateada}</span>
        </div>
        <span style="margin-left: 10px;"></span>
        <svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="blue" class="bi bi-cash-coin" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M11 15a4 4 0 1 0 0-8 4 4 0 0 0 0 8m5-4a5 5 0 1 1-10 0 5 5 0 0 1 10 0"/>
            <path d="M9.438 11.944c.047.596.518 1.06 1.363 1.116v.44h.375v-.443c.875-.061 1.386-.529 1.386-1.207 0-.618-.39-.936-1.09-1.1l-.296-.07v-1.2c.376.043.614.248.671.532h.658c-.047-.575-.54-1.024-1.329-1.073V8.5h-.375v.45c-.747.073-1.255.522-1.255 1.158 0 .562.378.92 1.007 1.066l.248.061v1.272c-.384-.058-.639-.27-.696-.563h-.668zm1.36-1.354c-.369-.085-.569-.26-.569-.522 0-.294.216-.514.572-.578v1.1zm.432.746c.449.104.655.272.655.569 0 .339-.257.571-.709.614v-1.195z"/>
            <path d="M1 0a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h4.083q.088-.517.258-1H3a2 2 0 0 0-2-2V3a2 2 0 0 0 2-2h10a2 2 0 0 0 2 2v3.528c.38.34.717.728 1 1.154V1a1 1 0 0 0-1-1z"/>
            <path d="M9.998 5.083 10 5a2 2 0 1 0-3.132 1.65 6 6 0 0 1 3.13-1.567"/>
        </svg>
    </div>
    """,
                        unsafe_allow_html=True,
                    )
            with st.container(height=550, border=True):
                tab1, tab2, tab3 = st.tabs(
                    [
                        "Nuevo Presupuesto",
                        "Gestión / Reportes de Presupuestos",
                        "Analísis de Desempeño"
                    ]
                )

                with tab1:
                    cont_1, cont_2, cont_3, cont_4, cont_5 = st.columns([2, 2, 1, 1, 1])
                    with cont_1:
                        propietario_select = st.selectbox(
                            "Seleccione un propietario",
                            opciones_propietario,
                            key="seleccion_propietarios_unique",
                        )
                        if propietario_select:
                            # propietario_select_cambio = True
                            df_filtered = df[
                                df["nombre_completo"].isin([propietario_select])
                            ]

                            opciones_vehiculo = df_filtered[
                                "vehiculo_completo"
                            ].unique()
                            # FIXME: CAMBIO 21-07
                            # opciones_vehiculo = pd.Series(opciones_vehiculo)

                            # TODO: VARIABLES PARA LA TABLA SQULITE PRESUPUESTOS Y PDF
                            opciones_cliente_id = df_filtered["cliente_id"].unique()
                            # opciones_cliente_id = pd.Series(opciones_cliente_id)
                            elemento_cliente_id = opciones_cliente_id[0]

                            opciones_telefono = df_filtered["telefono"].unique()
                            opciones_telefono = pd.Series(opciones_telefono)
                            elemento_telefono = opciones_telefono[0]

                            opciones_email = df_filtered["correo_electronico"].unique()
                            opciones_email = pd.Series(opciones_email)
                            elemento_email = opciones_email[0]

                            opciones_vehiculo_id = df_filtered["vehiculos_id"].unique()
                            opciones_vehiculo_id = pd.Series(opciones_vehiculo_id)
                            elemento_vehiculo_id = opciones_vehiculo_id[0]

                            opciones_observaciones_veh = df_filtered[
                                "observaciones"
                            ].unique()
                            opciones_observaciones_veh = pd.Series(
                                opciones_observaciones_veh
                            )
                            elemento_observaciones_veh = opciones_observaciones_veh[0]

                            # print(opciones_cliente_id)
                            # print(opciones_telefono)
                            # print(opciones_email)
                            # print(elemento_vehiculo_id)
                            # print(elemento_observaciones_veh)

                            vehiculos_select = st.selectbox(
                                "Seleccione un vehículo",
                                opciones_vehiculo,
                                key="seleccion_vehiculos_unique",
                            )
                            st.markdown(
                            """
                            <div style="display: flex; justify-content: center; align-items: center; font-size: 12px; font-weight: bold; color: blue;">
                                <div style="border-bottom: 1px solid blue; border-left: 1px solid blue; width: 12px; height: 12px;"></div>
                                <div style="margin: 0 0px;"><strong>__________ Propietario + Vehículo ________</strong></div>
                                <div style="border-bottom: 1px solid blue; border-right: 1px solid blue; width: 12px; height: 12px;"></div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        else:
                            df_filtered = pd.DataFrame()

                        total_column_ventas = st.session_state.df_detalle[
                            "Precio Venta en USD"
                        ].sum()
                        total_column_costos = st.session_state.df_detalle[
                            "Costo en USD"
                        ].sum()

                    with cont_2:
                        
                        repuesto_select = st.selectbox(
                            "Seleccione una pieza o repuesto",
                            opciones_repuestos,
                            on_change=None,
                            key="repuesto_unique",
                        )

                        mano_obra = st.text_input(
                            "Concepto libre (ej.: mano de obra, asesoría, etc.)",
                            on_change=None,
                            key="desc_mano_obra_unique",
                        )
                        st.markdown(
                            """
                            <div style="display: flex; justify-content: center; align-items: center; font-size: 12px; font-weight: bold; color: blue;">
                                <div style="border-bottom: 1px solid blue; border-left: 1px solid blue; width: 12px; height: 12px;"></div>
                                <div style="margin: 0 0px;"><strong>__ Componentes o Partidas del Presupuesto __</strong></div>
                                <div style="border-bottom: 1px solid blue; border-right: 1px solid blue; width: 12px; height: 12px;"></div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with cont_3:
                        if repuesto_select:
                            repuesto_select_cambio = True
                            df_filtered_repuestos = df_repuestos[
                                df_repuestos["Descripcion"].isin([repuesto_select])
                            ]
                            opciones_costo = df_filtered_repuestos["Costo"].unique()
                            opciones_costo = pd.Series(opciones_costo)

                            costo_rep = st.number_input(
                                "Costo en USD",
                                on_change=None,
                                value=float(opciones_costo.iloc[0]),
                                key="costo_repuestos_unique",
                            )
                            with cont_4:
                                opciones_precio_de_venta = df_filtered_repuestos[
                                    "Precio_de_Venta"
                                ].unique()
                                opciones_precio_de_venta = pd.Series(
                                    opciones_precio_de_venta
                                )

                                precio_rep = st.number_input(
                                    "Precio Venta en USD",
                                    on_change=None,
                                    value=float(opciones_precio_de_venta.iloc[0]),
                                    key="precio_venta_repuestos_unique",
                                )
                    with cont_3:
                        costo_mano_obra = st.number_input(
                            "Costo en USD", on_change=None, key="costo_mano_obra_unique"
                        )
                    with cont_4:
                        precio_mano_obra = st.number_input(
                            "Precio Venta en USD",
                            on_change=None,
                            key="precio_venta_mano_obra_unique",
                        )
                    with cont_5:
                        st.markdown(
                            """
                            <style>
                            .button-container {
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                justify-content: center;
                                height: 150%;
                            }
                            .stButton button {
                                margin-bottom: 26px;
                            }
                            </style>
                            """,
                            unsafe_allow_html=True,
                        )
                        with st.container():
                            st.markdown(
                                """
                                <div class="button-container">
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button("➕Agregar", key="agregar_repuesto_unique"):
                                st.session_state.data = agregar_repuesto(
                                    st.session_state.data,
                                    repuesto_select,
                                    costo_rep,
                                    precio_rep,
                                )
                                st.session_state.df_detalle = get_dataframe(
                                    st.session_state.data
                                )
                                st.session_state.selected_index = (
                                    len(st.session_state.df_detalle) - 1
                                )
                                st.rerun()
                            if st.button("➕Agregar", key="agregar_mano_obra_unique"):
                                st.session_state.data = agregar_repuesto(
                                    st.session_state.data,
                                    mano_obra,
                                    costo_mano_obra,
                                    precio_mano_obra,
                                )
                                st.session_state.df_detalle = get_dataframe(
                                    st.session_state.data
                                )
                                st.session_state.selected_index = (
                                    len(st.session_state.df_detalle) - 1
                                )
                                st.rerun()

                    with st.container(height=200, border=True):
                        vert_1, vert_2, vert_3, vert_4 = st.columns([5, 1, 1, 1])
                        with vert_1:
                            # FIXME: Nuevo codigo
                            budget_id = generar_siguiente_id_presupuesto()
                            st.markdown(
                                f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <div style="color: blue; font-size: 16px; font-weight: bold;">
            Presupuesto Id: {budget_id}
            <span style="display: inline-block; width: 150px;"></span>
            Descripción
        </div>
        <div style="color: blue; font-size: 16px; font-weight: bold; display: flex; align-items: center;">
            Control Filas
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-bar-right" viewBox="0 0 16 16" style="margin-left: 5px;">
                <path fill-rule="evenodd" d="M6 8a.5.5 0 0 0 .5.5h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L12.293 7.5H6.5A.5.5 0 0 0 6 8m-2.5 7a.5.5 0 0 1-.5-.5v-13a.5.5 0 0 1 1 0v13a.5.5 0 0 1-.5.5"/>
            </svg>
        </div>
    </div>
    """,
                                unsafe_allow_html=True,
                            )

                            # Define a currency formatting function
                            def format_currency(value):
                                return f"${value:.2f}"

                            # Apply the formatting to the DataFrame
                            formatted_df = st.session_state.df_detalle.style.format(
                                {
                                    "Costo en USD": format_currency,
                                    "Precio Venta en USD": format_currency,
                                }
                            )

                            st.write(formatted_df)  # Tabla de detalles
                        with vert_2:
                            if st.button("🔼 Subir", key="up_row_test_1_unique"):
                                st.session_state.df_detalle = subir_fila(
                                    st.session_state.df_detalle,
                                    st.session_state.selected_index,
                                )
                                st.rerun()
                            container = st.container()
                            container.markdown(
                                f"""
    <div style='width:250px; height:80px; background-color:#f0f0f0; border-radius:10px;display:flex; flex-direction:column;   align-items:center; justify-content:center; padding:10px;'>
        <span style='color:black; font-weight:bold; font-size:14px; text-align:center;line-height:1;'>Total Presupuesto:</span>
        <span style='color:blue; font-weight:bold; font-size:50px; text-align:center;line-height:1;'>${total_column_ventas:.2f}</span>
    </div>
    """,
                                unsafe_allow_html=True,
                            )
                        with vert_3:
                            st.session_state.selected_index = st.number_input(
                                "Fila a mover",
                                min_value=0,
                                max_value=(
                                    len(st.session_state.df_detalle) - 1
                                    if len(st.session_state.df_detalle) > 0
                                    else 0
                                ),
                                label_visibility="collapsed",
                                value=st.session_state.selected_index,
                                step=1,
                                key="input_index_unique",
                            )

                        with vert_4:
                            if st.button("🔽 Bajar", key="bajar_fila_unique"):
                                st.session_state.df_detalle = bajar_fila(
                                    st.session_state.df_detalle,
                                    st.session_state.selected_index,
                                )
                                st.rerun()

                            if st.button(
                                "🗑️ Eliminar   ultima fila ",
                                key="eliminar_ultima_fila_unique",
                            ):
                                st.session_state.df_detalle = eliminar_ultima_fila(
                                    st.session_state.df_detalle
                                )
                                # Actualizar st.session_state.data para que solo contenga las filas visibles
                                # st.session_state.data = (
                                st.session_state.data = (
                                    st.session_state.df_detalle.assign(
                                        ID=range(
                                            1, len(st.session_state.df_detalle) + 1
                                        ),
                                    )[
                                        [
                                            "ID",
                                            "Repuesto / Mano de Obra",
                                            "Costo en USD",
                                            "Precio Venta en USD",
                                        ]
                                    ].values.tolist()
                                )
                                st.rerun()

                    with st.container(height=50, border=False):
                        (
                            column_izq,
                            column_semi_izq,
                            column_center,
                            column_der,
                            column_uno,
                        ) = st.columns(
                            [
                                4,
                                1,
                                1,
                                1,
                                1,
                            ]
                        )
                        with column_semi_izq:
                            container = st.container()
                            container.markdown(
                                f"""
    <div style='width:100px; height:40px; background-color:#f0f0f0; border-radius:10px;display:flex; flex-direction:column;   align-items:center; justify-content:center; padding:10px;'>
        <span style='color:black; font-weight:bold; font-size:14px; text-align:center;line-height:1;'>Total costos:</span>
        <span style='color:red; font-weight:bold; font-size:14px; text-align:center;line-height:1;'>${total_column_costos:.2f}</span>
    </div>
    """,
                                unsafe_allow_html=True,
                            )
                        with column_center:
                            ganancia = total_column_ventas - total_column_costos
                            container = st.container()
                            container.markdown(
                                f"""
    <div style='width:100px; height:40px; background-color:#f0f0f0; border-radius:10px;display:flex; flex-direction:column;   align-items:center; justify-content:center; padding:10px;'>
        <span style='color:black; font-weight:bold; font-size:14px; text-align:center;line-height:1;'>Ganancia:</span>
        <span style='color:green; font-weight:bold; font-size:14px; text-align:center;line-height:1;'>${ganancia:.2f}</span>
    </div>
    """,
                                unsafe_allow_html=True,
                            )

                            # FIXME: Función para obtener un presupuesto con sus detalles
                            def obtener_presupuesto_con_detalles(id_presupuesto):
                                cursor.execute(
                                    """
                                SELECT p.*, d.IdDetalle, d.Descripcion, d.Costo, d.PrecioVenta
                                FROM Presupuesto p
                                LEFT JOIN DetallePresupuesto d ON p.IdPresupuesto = d.IdPresupuesto
                                WHERE p.IdPresupuesto = ?
                                """,
                                    (id_presupuesto,),
                                )
                                return cursor.fetchall()

                            # Función para generar el contenido del PDF
                            def generate_pdf(
                                propietario_select,
                                fecha_formateada,
                                vehiculos_select,
                                total_column_ventas,
                                ganancia,
                                opciones_telefono,
                                elemento_email,
                                df_detalle,
                                budget_id,
                                customer_id,
                                veh_id,
                                veh_observaciones,
                            ):
                                buffer = BytesIO()
                                doc = SimpleDocTemplate(buffer, pagesize=letter)
                                elements = []

                                styles = getSampleStyleSheet()
                                normal_style = styles["Normal"]

                                # Estilo para texto en negrita
                                bold_style = ParagraphStyle(
                                    name="Bold",
                                    parent=normal_style,
                                    fontName="Helvetica-Bold",
                                )

                                # Estilo para texto alineado a la derecha
                                right_align_style = ParagraphStyle(
                                    name="RightAlign",
                                    parent=normal_style,
                                    alignment=2,  # Alineación a la derecha
                                )

                                # Estilo para alineación al centro
                                center_align_style = ParagraphStyle(
                                    name="CenterAlign",
                                    parent=normal_style,
                                    alignment=1,  # TA_CENTER
                                )

                                # Estilo para alineación a la izquierda
                                left_align_style = ParagraphStyle(
                                    name="LeftAlign",
                                    parent=normal_style,
                                    alignment=0,  # TA_LEFT
                                )

                                # Estilo para el título alineado a la izquierda
                                title_left_align_style = ParagraphStyle(
                                    name="TitleLeftAlign",
                                    parent=styles["Title"],
                                    alignment=0,  # TA_LEFT
                                )

                                # Estilo para el título alineado a la izquierda
                                title_center_align_style = ParagraphStyle(
                                    name="TitleCenterAlign",
                                    parent=styles["Title"],
                                    alignment=1,  # TA_LEFT
                                )

                                # Añadir imagen al inicio
                                image = RLImage(image_path_taller_img)
                                image_width = 0.7 * inch
                                image_height = 0.7 * inch
                                image.drawWidth = image_width
                                image.drawHeight = image_height
                                image.hAlign = (
                                    "LEFT"  # Alinear la imagen a la izquierda
                                )

                                # Añadir espaciador y texto al lado de la imagen
                                text = Paragraph("Auto Diagnóstico J.R.M.", bold_style)
                                spacer = Spacer(
                                    1, 12
                                )  # Ajusta la altura del espaciador según sea necesario

                                # Crear una tabla con la imagen, el espaciador y el texto
                                table_data = [[image, spacer, text]]
                                table = Table(
                                    table_data,
                                    colWidths=[image_width, 0.1 * inch, 6.8 * inch],
                                )
                                table.setStyle(
                                    TableStyle(
                                        [
                                            ("VALIGN", (0, 0), (-1, -1), "CENTER"),
                                            (
                                                "ALIGN",
                                                (2, 0),
                                                (2, 0),
                                                "CENTER",
                                            ),  # Centrar el texto verticalmente en la celda
                                        ]
                                    )
                                )

                                elements.append(table)

                                elements.append(
                                    Spacer(1, 4)
                                )  # Espaciador después de la imagen

                                # elements.append(Paragraph("Auto Diagnóstic J.R.M.", bold_style))
                                elements.append(Spacer(1, 4))  # Línea en blanco

                                elements.append(
                                    Paragraph(
                                        f"<b>Fecha:</b> {fecha_formateada}",
                                        right_align_style,
                                    )
                                )
                                elements.append(Spacer(1, 12))
                                elements.append(
                                    Paragraph(
                                        f"<b>Cliente Id:</b> {customer_id}",
                                        right_align_style,
                                    )
                                )
                                elements.append(Spacer(1, 6))
                                elements.append(
                                    Paragraph(
                                        f"<b>Vehículo Id:</b> {veh_id}",
                                        right_align_style,
                                    )
                                )
                                elements.append(Spacer(1, 30))

                                elements.append(
                                    Paragraph("Datos Cliente / Vehículo :", bold_style)
                                )
                                elements.append(Spacer(1, 12))

                                # Nombre, Teléfono y Correo Electrónico en la misma línea
                                nombre_telefono_correo = (
                                    f"<b>Nombre:</b> {propietario_select}"
                                    f"    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"  # Dos tabulaciones
                                    f"<b>Teléfono:</b> {opciones_telefono}"
                                    f"    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"  # Dos tabulaciones
                                )
                                elements.append(
                                    Paragraph(nombre_telefono_correo, normal_style)
                                )
                                elements.append(Spacer(1, 12))
                                elements.append(
                                    Paragraph(
                                        f"<b>Email:</b> {elemento_email}",
                                        normal_style,
                                    )
                                )
                                elements.append(Spacer(1, 12))  # Línea en blanco
                                elements.append(
                                    Paragraph(
                                        f"<b>Vehículo:</b> {vehiculos_select}",
                                        normal_style,
                                    )
                                )
                                elements.append(Spacer(1, 30))  # Línea en blanco

                                # Encabezado
                                elements.append(
                                    Paragraph(
                                        f"<b> Presupuesto N°</b> {budget_id}",
                                        title_center_align_style,
                                    )
                                )
                                elements.append(Spacer(1, 6))  # Línea en blanco

                                elements.append(
                                    Paragraph(
                                        "<b> Detalle del Presupuesto </b>",
                                        center_align_style,
                                    )
                                )
                                elements.append(Spacer(1, 12))  # Línea en blanco

                                # Eliminar la columna 'Precio Venta en USD' del DataFrame
                                df_detalle = df_detalle.drop(columns=["Costo en USD"])

                                # Convertir DataFrame a lista de listas para crear la tabla
                                data = [
                                    df_detalle.columns.tolist()
                                ] + df_detalle.values.tolist()

                                # Formatear la columna 'Costo en USD'
                                for i, row in enumerate(data):
                                    if i == 0:  # Encabezados
                                        continue
                                    row[1] = f"${row[1]:.2f}"  # Costo en USD

                                # Ajustar el contenido de las celdas con wrap text
                                wrapped_data = []
                                for row in data:
                                    wrapped_row = []
                                    for j, cell in enumerate(row):
                                        if (
                                            j == 1
                                        ):  # Alinear 'Costo en USD' a la derecha
                                            wrapped_row.append(
                                                Paragraph(str(cell), right_align_style)
                                            )
                                        else:
                                            wrapped_row.append(
                                                Paragraph(str(cell), normal_style)
                                            )
                                    wrapped_data.append(wrapped_row)

                                # Crear la tabla con el contenido ajustado
                                col_widths = [
                                    4.5 * inch,
                                    2 * inch,
                                ]  # Ajustar los anchos de las columnas según sea necesario
                                table = Table(wrapped_data, colWidths=col_widths)
                                table.setStyle(
                                    TableStyle(
                                        [
                                            (
                                                "BACKGROUND",
                                                (0, 0),
                                                (-1, 0),
                                                colors.grey,
                                            ),
                                            (
                                                "TEXTCOLOR",
                                                (0, 0),
                                                (-1, 0),
                                                colors.whitesmoke,
                                            ),
                                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                            (
                                                "FONTNAME",
                                                (0, 0),
                                                (-1, 0),
                                                "Helvetica-Bold",
                                            ),
                                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                                            (
                                                "BACKGROUND",
                                                (0, 1),
                                                (-1, -1),
                                                colors.white,
                                            ),
                                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                                        ]
                                    )
                                )

                                elements.append(table)
                                elements.append(Spacer(1, 12))  # Línea en blanco

                                # Total Presupuesto alineado a la derecha
                                total_presupuesto = Paragraph(
                                    f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Total Presupuesto: <b>${total_column_ventas:.2f}</b>",
                                    center_align_style,
                                )
                                elements.append(total_presupuesto)
                                elements.append(Spacer(1, 12))  # Línea en blanco

                                elements.append(
                                    Paragraph(
                                        "<b> Observaciones: </b>", left_align_style
                                    )
                                )
                                elements.append(Spacer(1, 6))  # Línea en blanco
                                elements.append(
                                    Paragraph(veh_observaciones, normal_style)
                                )

                                elements.append(Spacer(1, 12))  # Línea en blanco

                                elements.append(
                                    Paragraph("<b> Notas: </b>", left_align_style)
                                )
                                elements.append(Spacer(1, 6))  # Línea en blanco

                                elements.append(
                                    Paragraph(
                                        "- Presupuesto valido solo por tres (3) días habíles desde su fecha de emisión",
                                        normal_style,
                                    )
                                )
                                elements.append(Spacer(1, 6))  # Línea en blanco
                                elements.append(
                                    Paragraph(
                                        "- La empresa se reserva el derecho a realizar cambios sin previo aviso",
                                        normal_style,
                                    )
                                )
                                elements.append(Spacer(1, 6))  # Línea en blanco
                                elements.append(
                                    Paragraph(
                                        "- Para el inicio de los trabajos el cliente debe abonar el 50&percnt del valor de este presupuesto",
                                        normal_style,
                                    )
                                )
                                elements.append(Spacer(1, 6))  # Línea en blanco
                                elements.append(
                                    Paragraph(
                                        "- El monto total del presupuesto no incluye impuestos nacionales, estadales, ni municipales",
                                        normal_style,
                                    )
                                )

                                doc.build(elements)
                                buffer.seek(0)

                                return buffer

                            @st.dialog("  Presupuesto", width="large")
                            def modal_prep(
                                fecha_formateada_mod,
                                budget_id_mod,
                                elemento_vehiculo_id_mod,
                                elemento_cliente_id_mod,
                                propietario_select_mod,
                                elemento_telefono_mod,
                                elemento_email_mod,
                                vehiculos_select_mod,
                                elemento_observaciones_veh_mod,
                                ganancia_mod,
                                df_detalle_mod,
                                total_column_ventas_mod,
                                total_column_costos_mod,
                            ):

                                fecha_formateada_modal = fecha_formateada_mod
                                budget_id_modal = budget_id_mod
                                elemento_vehiculo_id_modal = int(
                                    elemento_vehiculo_id_mod
                                )
                                elemento_cliente_id_modal = elemento_cliente_id_mod
                                propietario_select_modal = propietario_select_mod
                                elemento_telefono_modal = elemento_telefono_mod
                                elemento_email_modal = elemento_email_mod
                                vehiculos_select_modal = vehiculos_select_mod
                                elemento_observaciones_veh_modal = (
                                    elemento_observaciones_veh_mod
                                )
                                ganancia_modal = ganancia_mod
                                total_column_ventas_modal = total_column_ventas_mod
                                total_column_costos_modal = total_column_costos_mod

                                # Almacenar el DataFrame en st.session_state
                                st.session_state.df_modal = df_detalle_mod

                                # FIXME: NUEVO CODIGO 23-07-2024-Header con datos del presupuesto
                                html_content = f"""
<div style="border: 1px solid #ccc; padding: 10px; margin: 10px; width: 680px; height: 220px; overflow: auto; font-family: Arial, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1); font-size: 12px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style='display: flex; align-items: center; color: black; font-size: 12px; font-weight: bold;'>
            <img src="data:image/png;base64,{img_str}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; border: 2px solid black;">
            Auto Diagnostico J.M.R.
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-end;">
            <div style="display: flex; align-items: center;">
                <strong style="font-size: 12px;">Fecha:</strong>
                <p style="margin: 0 0 0 10px; font-size: 12px;">{fecha_formateada_modal}</p>
            </div>
            <div style="display: flex; align-items: center;">
                <strong style="font-size: 12px;">Presupuesto N°:</strong>
                <p style="margin: 0 0 0 10px; font-size: 12px;">{budget_id_modal}</p>
            </div>
            <div style="display: flex; align-items: center;">
                <strong style="font-size: 12px;">Vehículo Id:</strong>
                <p style="margin: 0 0 0 10px; font-size: 12px;">{elemento_vehiculo_id_modal}</p>
            </div>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: auto 1fr auto 1fr auto 1fr; gap: 10px; align-items: center; margin-top: 14px;">
        <strong style="font-size: 12px;">Cliente Id:</strong>
        <p style="margin: 0; font-size: 12px;">{elemento_cliente_id_modal}</p>
    </div>
    <div style="display: grid; grid-template-columns: auto 1fr auto 1fr auto 1fr; gap: 10px; align-items: center; margin-top: 14px;">
        <strong style="font-size: 12px;">Nombre:</strong>
        <p style="margin: 0; font-size: 12px;">{propietario_select_modal}</p>
        <strong style="font-size: 12px;">Teléfono:</strong>
        <p style="margin: 0; font-size: 12px;">{elemento_telefono_modal}</p>
        <strong style="font-size: 12px;">Correo electrónico:</strong>
        <p style="margin: 0; font-size: 12px;">{elemento_email_modal}</p>
    </div>
    <div style="display: grid; grid-template-columns: auto 1fr; gap: 5px; align-items: center; margin-top: 14px;">
        <strong style="font-size: 12px;">Vehículo:</strong>
        <p style="margin: 0; font-size: 12px;">{vehiculos_select_modal}</p>
        <strong style="font-size: 12px;">Observaciones vehículo:</strong>
        <div style="background-color: yellow; padding: 5px;">
            <p style="margin: 0; font-size: 12px;">{elemento_observaciones_veh_modal}</p>
        </div>
    </div>
</div>
"""
                                # Generate the PDF
                                st.markdown(html_content, unsafe_allow_html=True)

                                # DataFrame dentro de un bloque de HTML
                                st.markdown(
                                    """
                                <div style="border: 1px solid #ccc; padding: 10px; margin: 10px; width: 680px; height: 50px; overflow: auto; font-family: Arial, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                                    <div style="display: grid; grid-template-columns: auto 1fr; gap: 20px; align-items: center;">
                                        <strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; PRESUPUESTO</strong>
                                    </div>
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )
                                # df_modal = st.session_state.df_detalle.copy()
                                # df_modal = df_detalle_mod
                                df_modal = st.session_state.df_modal

                                def style_df(df):
                                    return (
                                        df.style.set_properties(
                                            **{
                                                "text-align": "left",
                                                "white-space": "pre-wrap",
                                                "font-size": "14px",
                                                "font-family": "Arial, sans-serif",
                                            }
                                        )
                                        .set_table_styles(
                                            [
                                                {
                                                    "selector": "th",
                                                    "props": [
                                                        ("font-size", "14px"),
                                                        ("text-align", "center"),
                                                        ("background-color", "#f0f0f0"),
                                                    ],
                                                },
                                                {
                                                    "selector": "td",
                                                    "props": [("text-align", "left")],
                                                },
                                                {
                                                    "selector": "td:nth-child(2), td:nth-child(3)",
                                                    "props": [("text-align", "right")],
                                                },  # Alinea las columnas 2 y 3 a la derecha
                                            ]
                                        )
                                        .hide(axis="index")
                                    )

                                # Crear una copia del dataframe para aplicar formato
                                df_display = df_modal.copy()
                                # Asegurarse de que las columnas sean numéricas
                                df_display["Costo en USD"] = pd.to_numeric(
                                    df_display["Costo en USD"], errors="coerce"
                                )
                                df_display["Precio Venta en USD"] = pd.to_numeric(
                                    df_display["Precio Venta en USD"], errors="coerce"
                                )

                                # Aplicar el formato de moneda directamente
                                df_display["Costo en USD"] = df_display[
                                    "Costo en USD"
                                ].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else x)
                                df_display["Precio Venta en USD"] = df_display[
                                    "Precio Venta en USD"
                                ].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else x)

                                # Aplicar el estilo y convertir a HTML
                                html_df = style_df(df_display).to_html()

                                # Eliminar la etiqueta </div> adicional
                                html_df = html_df.rstrip().rstrip("</div>")

                                # Envolver el DataFrame en un div con estilos específicos
                                html_content_3 = f"""
                                <div style="border: 1px solid #ccc; padding: 10px; margin: 10px; width: 680px; max-height: 300px; overflow: auto; font-family: Arial, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1);font-size: 14px;">
                                    {html_df}
                                </div>
                                """

                                # Mostrar el DataFrame estilizado dentro del contenedor
                                st.markdown(html_content_3, unsafe_allow_html=True)
                                # st.table(st.session_state.df_detalle)
                                # Formatear la ganancia como moneda
                                formatted_ganancia = f"${ganancia_modal:,.2f}"

                                html_content_2 = f"""
<div style="border: 1px solid #ccc; padding: 10px; margin: 10px; width: 680px; height: 140px; overflow: auto; font-family: Arial, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1); font-size: 14px;">
    <div style="display: flex; flex-direction: column; align-items: flex-end;">
        <div style="display: flex; align-items: center;">
            <strong>Total Presupuesto:</strong>
            <p style="margin: 0 0 0 10px;">${total_column_ventas_modal:.2f}</p>
        </div>
        <div style="display: flex; align-items: center; margin-top: 10px;">
            <strong>Costos:</strong>
            <p style="margin: 0 0 0 10px; color: red; font-weight: bold;">${total_column_costos_modal:.2f}</p>
        </div>
        <div style="display: flex; align-items: center; margin-top: 10px;">
            <strong>Ganancia:</strong>
            <p style="margin: 0 0 0 10px; color: green; font-weight: bold;">{formatted_ganancia}</p>
        </div>
    </div>
</div>
"""
                                st.markdown(html_content_2, unsafe_allow_html=True)
                                # FIXME: FIN DEL CODIGO NUEVO
                                with st.container(height=80, border=False):
                                    (
                                        mod_izq,
                                        mod_center,
                                        mod_der,
                                        mod_uno,
                                    ) = st.columns(
                                        [
                                            5,
                                            2,
                                            2,
                                            2,
                                        ]
                                    )

                                    with mod_izq:
                                        with st.container(height=70, border=False):
                                            st.markdown(
                                                """
                                                <p style="color:blue; font-size:14px; font-weight:bold; text-align:center;">
                                                    Para cerrar oprima 'Esc' o marque arriba la 'X'
                                                </p>
                                                """,
                                                unsafe_allow_html=True,
                                            )
                                            st.session_state.dialog_visible = False
                                            placeholder.empty()
                                    with mod_der:
                                        if st.button(
                                            "Descargar PDF",
                                            key="download_pdf_unique",
                                            on_click=None,
                                        ):
                                            pdf_buffer = generate_pdf(
                                                propietario_select_modal,
                                                fecha_formateada_modal,
                                                vehiculos_select_modal,
                                                total_column_ventas_modal,
                                                ganancia_modal,
                                                elemento_telefono_modal,
                                                elemento_email_modal,
                                                st.session_state.df_modal,
                                                budget_id_modal,
                                                elemento_cliente_id_modal,
                                                elemento_vehiculo_id_modal,
                                                elemento_observaciones_veh_modal,
                                            )
                                            with mod_uno:
                                                st.download_button(
                                                    "Haz clic para descargar",
                                                    pdf_buffer,
                                                    file_name="presupuesto.pdf",
                                                    key="download_button_unique",
                                                )

                        with column_der:
                            if st.button("🔭 Preview", key="preview_button_unique"):
                                st.session_state.dialog_visible = True
                                if st.session_state.dialog_visible:
                                    modal_prep(
                                        fecha_formateada,
                                        budget_id,
                                        elemento_vehiculo_id,
                                        elemento_cliente_id,
                                        propietario_select,
                                        elemento_telefono,
                                        elemento_email,
                                        vehiculos_select,
                                        elemento_observaciones_veh,
                                        ganancia,
                                        st.session_state.df_detalle,
                                        total_column_ventas,
                                        total_column_costos,
                                    )
                        with column_uno:
                            if st.button("💾 Guardar", key="save_button_budget_unique"):
                                toast()
                                presptosql(
                                    propietario_select,
                                    fecha_formateada,
                                    vehiculos_select,
                                    total_column_ventas,
                                    total_column_costos,
                                    ganancia,
                                    elemento_telefono,
                                    elemento_email,
                                    elemento_cliente_id,
                                    elemento_vehiculo_id,
                                    elemento_observaciones_veh,
                                )
                                st.rerun()

                    # FIXME: INICIO DE TABLA AGGRID
                with tab2:
                    with st.container(height=160, border=False):
                        card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(
                            [2, 1, 2, 2]
                        )
                        with card_col_1:
                            # with st.container(height=200, border=False):
                            st.markdown(
                                "<span style='font-size: 20px; color: blue; font-weight: bold;'>REPORTE PRESUPUESTO</span>",
                                unsafe_allow_html=True,
                            )
                            search_term_presp = st.text_input(
                                "Buscar",
                                label_visibility="collapsed",
                                placeholder="Buscar",
                                on_change=None,
                                key="search_box_presp",
                            )
                            streamlit_space.space(container=None, lines=2)
                            st.markdown(
                                f"""
                                <p style="font-size: 14px; color: blue; font-weight: bold; text-align: center; display: flex; align-items: center; justify-content: center;">
                                    Elija el presupuesto marcando el 'checkbox'
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="red" class="bi bi-check-square-fill" viewBox="0 0 16 16" style="margin-left: 5px;">
                                        <path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2zm10.03 4.97a.75.75 0 0 1 .011 1.05l-3.992 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.75.75 0 0 1 1.08-.022z"/>
                                    </svg>
                                </p>
                                """,
                                unsafe_allow_html=True,
                            )

                        with card_col_2:
                            streamlit_space.space(container=None, lines=2)
                            if st.button("Limpiar", key="clean_report_presp"):
                                search_term_presp = ""
                        with card_col_3:
                            
                            st.markdown(
    f"""
    <div style="width: 308px; height: 151px; border: 1px solid #ccc; border-radius: 8px; padding: 10px; box-shadow: 2px 2px 5px #ccc; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="font-size: 18px; font-weight: bold; color: blue; text-align: center;">
            <div>Presupuestos Aprobados</div>
            <div style="font-size: 14px; text-align: center;">(Total USD)</div>
        </div>
        <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px; text-align: center;">{formatted_valor_total_precio_venta}</div>
        <div style="font-size: 12px;">Ganancia total {formatted_valor_total_ganancia} esto es un rendimiento del {formatted_margen_ganancia} sobre los costos</div>
    </div>
    """,
    unsafe_allow_html=True
)
                            
                        with card_col_4:
                            st.markdown(
    f"""
    <div style="width: 298px; height: 151px; border: 1px solid #ccc; border-radius: 8px; padding: 10px; box-shadow: 2px 2px 5px #ccc; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="font-size: 18px; font-weight: bold; color: blue; text-align: center;">
            <div>Presupuestos Sin Aprobar</div>
            <div style="font-size: 14px; text-align: center;">(Total USD)</div>
        </div>
        <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px; text-align: center;">{formatted_valor_total_precio_venta_creados}</div>
        <div style="font-size: 12px;">Ganancia total {formatted_valor_total_ganancia} esto es un rendimiento del {formatted_margen_ganancia_creados} sobre los costos</div>
    </div>
    """,
    unsafe_allow_html=True
)

                    # FIXME: CONTAINER TABLA AGGRID
                    with st.container(height=215, border=True):
                        if search_term_presp:
                            # Filtrar por si el término de búsqueda aparece en cualquier columna
                            df_filtered_presp = df_presupuestos[
                                df_presupuestos.apply(
                                    lambda row: row.astype(str)
                                    .str.contains(search_term_presp, case=False)
                                    .any(),
                                    axis=1,
                                )
                            ]
                        else:
                            df_filtered_presp = df_presupuestos
                        # Dibujar el grid con agstyler
                        grid_response = agstyler.draw_grid(
                            df_filtered_presp,
                            formatter=formatter,
                            fit_columns=True,
                            selection="single",  # or 'single', or None
                            use_checkbox=True,  # or False by default
                            max_height=200,
                        )
                        # # Obtener las filas seleccionadas
                        selected_rows = grid_response["selected_rows"]
                        # print(type(selected_rows))
                        if selected_rows is not None:
                            id_presup_sql = selected_rows.iloc[0]["IdPresupuesto"]
                            st.write(
                                f"""
                                <div style="font-size: 14px;">
                                    Registro seleccionado
                                    <span style="font-size: 24px; font-weight: bold; color: blue;">{id_presup_sql}</span>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            presupuesto_con_detalles = obtener_presupuesto_con_detalles(
                                id_presup_sql
                            )
                            presupuesto_from_sql = presupuesto_con_detalles[0]

                            fecha_formateada_sql = presupuesto_from_sql[7]
                            budget_id_sql = presupuesto_from_sql[0]
                            elemento_vehiculo_id_sql = presupuesto_from_sql[2]
                            elemento_cliente_id_sql = presupuesto_from_sql[1]
                            propietario_select_sql = presupuesto_from_sql[3]
                            elemento_telefono_sql = presupuesto_from_sql[4]
                            elemento_email_sql = presupuesto_from_sql[5]
                            vehiculos_select_sql = presupuesto_from_sql[6]
                            elemento_observaciones_veh_sql = presupuesto_from_sql[11]
                            ganancia_sql = presupuesto_from_sql[10]
                            total_column_ventas_sql = presupuesto_from_sql[9]
                            total_column_costos_sql = presupuesto_from_sql[8]

                            # Crear un DataFrame con los detalles del presupuesto
                            detalles_data = {
                                "Repuesto / Mano de Obra": [
                                    detalle[14] for detalle in presupuesto_con_detalles
                                ],
                                "Costo en USD": [
                                    detalle[15] for detalle in presupuesto_con_detalles
                                ],
                                "Precio Venta en USD": [
                                    detalle[16] for detalle in presupuesto_con_detalles
                                ],
                            }
                            df_detalles_sql = pd.DataFrame(detalles_data)
                    with st.container(height=80, border=False):
                        (
                            par_izq,
                            par_semi_izq,
                            par_center,
                            par_der,
                            par_uno,
                        ) = st.columns(
                            [
                                2,
                                2,
                                2,
                                2,
                                2,
                            ]
                        )
                        with par_izq:
                            if st.button("🔭 Preview", key="preview_rep_presup"):
                                st.session_state.dialog_visible = True
                                if st.session_state.dialog_visible:
                                    modal_prep(
                                        fecha_formateada_sql,
                                        budget_id_sql,
                                        elemento_vehiculo_id_sql,
                                        elemento_cliente_id_sql,
                                        propietario_select_sql,
                                        elemento_telefono_sql,
                                        elemento_email_sql,
                                        vehiculos_select_sql,
                                        elemento_observaciones_veh_sql,
                                        ganancia_sql,
                                        df_detalles_sql,
                                        total_column_ventas_sql,
                                        total_column_costos_sql,
                                    )
                        with par_semi_izq:
                            if st.button(
                                "Descargar PDF", key="download_pdf_rep_presup"
                            ):
                                pdf_buffer = generate_pdf(
                                    propietario_select,
                                    fecha_formateada_sql,
                                    vehiculos_select_sql,
                                    total_column_ventas_sql,
                                    ganancia_sql,
                                    elemento_telefono_sql,
                                    elemento_email_sql,
                                    df_detalles_sql,
                                    budget_id_sql,
                                    elemento_cliente_id_sql,
                                    elemento_vehiculo_id_sql,
                                    elemento_observaciones_veh_sql,
                                )
                                with par_center:
                                    st.download_button(
                                        "Haz clic para descargar",
                                        pdf_buffer,
                                        file_name="presupuesto.pdf",
                                        key="download_button_sql",
                                    )
                        with par_der:
                            if st.button("Aprobar Presupuesto", key="budget_aproval"):
                                if selected_rows is not None:
                                    aprobar_presupuesto(budget_id_sql)
                        with par_uno:
                            if st.button(
                                "❌ Eliminar Presupuesto", key="delete_budget"
                            ):
                                if selected_rows is not None:
                                    st.session_state.dialog_visible = True
                                    if st.session_state.dialog_visible:
                                        advertencia(budget_id_sql)
                with tab3:
                    # Lista de columnas a borrar
                    columnas_a_borrar = ['vehiculo_id', 'Cliente_id', 'NombreCliente', 'Telefono', 'email', 'DatosVehiculos', 'Observaciones']
                    df_recortado = df_aprobados.drop(columns = columnas_a_borrar)
                    with st.container(height=480, border=True):
                        perf_1, perf_2, perf_4 = st.columns(
                            [2.6,0.6,5]
                        )
                        with perf_1:
                            fecha_inic = st.date_input("Inicio",on_change=None,max_value=datetime.today(), value=None)
                            fecha_final = st.date_input("Final",on_change=None, value=fecha_inic,max_value= datetime.today())
                            
                            def anuncios(anuncio_venta, anuncio_costo, anuncio_ganancia):
                                with perf_1:
                                    st.markdown(
                                        f"""
                                        <div style="display: flex; justify-content: space-between; text-align: center;">
                                            <div style="display: flex; flex-direction: column; align-items: center;">
                                                <p style="font-size: 14px; font-weight: bold; color: blue; margin: 0;">Ventas periodo:</p>
                                                <span style="color: green;">{anuncio_venta}</span>
                                            </div>
                                            <div style="display: flex; flex-direction: column; align-items: center;">
                                                <p style="font-size: 14px; font-weight: bold; color: blue; margin: 0;">Costos periodo:</p>
                                                <span style="color: red;">{anuncio_costo}</span>
                                            </div>
                                            <div style="display: flex; flex-direction: column; align-items: center;">
                                                <p style="font-size: 14px; font-weight: bold; color: blue; margin: 0;">Ganancias periodo:</p>
                                                <span style="color: #ea882a;">{anuncio_ganancia}</span>
                                            </div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                            st.markdown(
                                """
                                <div style="height: 1px;"></div>
                                """,
                                unsafe_allow_html=True
                            )
                            def despliegue_dataframe(tabla):
                                with perf_1:
                                    with st.container(height=230, border=True):
                                        st.markdown(
                                            """
                                            <div style="height: 10px;"></div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                                        st.dataframe(tabla)
                                        
                                        st.markdown(
                                            """
                                            <div style="height: 10px;"></div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                        with perf_2:
                            st.markdown(
                                """
                                <div style="height: 113px;"></div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            df_filtrado = df_recortado
                            
                            if st.button("Filtrar", key="boton_rango_fechas"):
                                if fecha_final < fecha_inic:
                                    print('La fecha de fin no puede ser menor que la fecha de inicio')
                                    anuncios(formatted_valor_total_precio_venta, formatted_valor_total_costo, formatted_valor_total_ganancia)
                                    despliegue_dataframe(df_recortado)
                                    data = Data()
                                    data.add_df(df_recortado)
                                elif fecha_final is None or fecha_inic is None:
                                    anuncios(formatted_valor_total_precio_venta, formatted_valor_total_costo, formatted_valor_total_ganancia)
                                    despliegue_dataframe(df_recortado)
                                    data = Data()
                                    data.add_df(df_recortado)
                                else:
                                    df_filtrado['Fecha'] = pd.to_datetime(df_filtrado['Fecha']).dt.date
                                    df_filtrado_dos = df_filtrado[(df_filtrado['Fecha'] >= fecha_inic) & (df_filtrado['Fecha'] <= fecha_final)]
                                    valor_venta_df_filtrado_dos = df_filtrado_dos["TotalVenta"].sum()
                                    valor_costo_df_filtrado_dos = df_filtrado_dos["TotalCosto"].sum()
                                    valor_ganancia_df_filtrado_dos = df_filtrado_dos["Ganancia"].sum()
                                    formatted_venta_df_filtrado_dos = f"${valor_venta_df_filtrado_dos:,.2f}"
                                    formatted_costo_df_filtrado_dos = f"${valor_costo_df_filtrado_dos:,.2f}"
                                    formatted_ganancia_df_filtrado_dos = f"${valor_ganancia_df_filtrado_dos:,.2f}"
                                    anuncios(formatted_venta_df_filtrado_dos, formatted_costo_df_filtrado_dos, formatted_ganancia_df_filtrado_dos)
                                    
                                    
                                    despliegue_dataframe(df_filtrado_dos)
                                    data = Data()
                                    data.add_df(df_filtrado_dos)
                            else:
                                anuncios(formatted_valor_total_precio_venta, formatted_valor_total_costo, formatted_valor_total_ganancia)
                                despliegue_dataframe(df_recortado)
                                data = Data()
                                data.add_df(df_recortado)
                            with perf_4:
                                with st.container(height=450, border=False):
                                    # data = Data()
                                    # data.add_df(df_filtrado)
                                    
                                    story = Story(data)
                                    
                                    story.set_size("100%",450)
                                    
                                    story.set_feature("tooltip", True)
                                    
                                    # Comenzamos a adicionar los slides de nuestra presentación
                                    slide1 = Slide(
                                        Step(
                                            Style(
                                                {
                                                    "legend": {
                                                        "label": {"fontSize": "1.1em"},
                                                        "paddingRight": "-1em",
                                                    },
                                                    "plot": {
                                                        "marker": {
                                                            "label": {"fontSize": "1.1em"},
                                                            "colorPalette": "#9355e8FF #123456FF #BDAF10FF"
                                                        },
                                                        "paddingLeft": "10em",
                                                        "xAxis": {
                                                            "title": {"color": "#00000000"},
                                                            "label": {"fontSize": "1.1em"},
                                                        },
                                                        "yAxis": {"label": {"fontSize": "1.1em"}},
                                                    },
                                                    "logo": {"width": "6em"},
                                                    "fontSize": "0.8em",
                                                }
                                            ),
                                            Config(
                                                {
                                                    "x": ["TotalVenta", "Ganancia", "TotalCosto"],
                                                    "y": "Fecha",
                                                    "color": "Ganancia",
                                                    "label": "TotalVenta",
                                                    "title": "Ventas para el periodo (por dia)"
                                                }
                                            ),
                                        )
                                    )
                                    story.add_slide(slide1)
                                    slide4 = Slide()
                                    slide4.add_step(
                                        Step(
                                            Style({"plot": {"yAxis": {"title": {"color": "#00000000"}}}}),
                                            Config(
                                                {
                                                    "x": "IdPresupuesto",
                                                    "y": ["Fecha", "Ganancia"],
                                                    "split": False,
                                                    "legend": "color",
                                                }
                                            ),
                                        )
                                    )
                                    slide4.add_step(
                                        Step(
                                            Style({"plot": {"marker": {"label": {"fontSize": "1.1em"}}}}),
                                            Config(
                                                {"y": "Ganancia", "title": "Ganancias para el periodo (por Id)"}
                                            ),
                                        )
                                    )
                                    story.add_slide(slide4)
                                    
                                    slide5 = Slide()

                                    slide5.add_step(
                                        Step(
                                            Config(
                                                {
                                                    "x": ["Ganancia", "Fecha"],
                                                    "y": None,
                                                    "label": ["Ganancia"],
                                                }
                                            )
                                        )
                                    )
                                    slide5.add_step(
                                        Step(
                                            Style({"plot": {"xAxis": {"label": {"color": "#00000000"}}}}),
                                            Config(
                                                {
                                                    "coordSystem": "polar",
                                                    "title": "Distribucion de las Ganancias por fecha "
                                                }
                                            ),
                                        )
                                    )
                                    story.add_slide(slide5)
                                    story.play()
                            with perf_2:
                                st.markdown(
                                """
                                <div style="height: 60px;"></div>
                                """,
                                unsafe_allow_html=True
                                )
                                st.markdown(
                                """
                                <div style="text-align: center; font-size: 11px; color: blue; font-weight: bold;">
                                    Tabla de datos
                                    <br>
                                    expandible
                                    <br>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="blue" stroke="blue" stroke-width="0" class="bi bi-arrow-return-left" viewBox="0 0 16 16">
                                        <path fill-rule="evenodd" d="M14.5 1.5a.5.5 0 0 1 .5.5v4.8a2.5 2.5 0 0 1-2.5 2.5H2.707l3.347 3.346a.5.5 0 0 1-.708.708l-4.2-4.2a.5.5 0 0 1 0-.708l4-4a.5.5 0 1 1 .708.708L2.707 8.3H12.5A1.5 1.5 0 0 0 14 6.8V2a.5.5 0 0 1 .5-.5"/>
                                    </svg>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            

# Pagina Ajustes
def ajustes():
    # Carga de datos a una lista desde la base de datos jhotem.db
    # Conectar a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()
    
    # Cargar los datos de la tabla 'clientes'
    cursor.execute("SELECT * FROM usuarios")
    rows = cursor.fetchall()
    
    test_data_usuarios = [list(row) for row in rows]
    # print(test_data_usuarios)
    m_user = test_data_usuarios[3][1]
    m_clave = test_data_usuarios[3][2]
    
    # print(test_data_usuarios[3][1])
    # print(test_data_usuarios[3][2])
    
    
    if "index_usuario" not in st.session_state:
        st.session_state.index_usuario = 0
        
    if "new_test_data_usuario" not in st.session_state:
        st.session_state.new_test_data_usuario = []
    if "is_new_user_usuario" not in st.session_state:
        st.session_state.is_new_user_usuario = False
    if "is_saved_usuario" not in st.session_state:  # ADDED
        st.session_state.is_saved_usuario = False  # ADDED
    if "validated" not in st.session_state:  # ADDED
        st.session_state.validated = False  # ADDED
    if "validation_attempted" not in st.session_state:  # ADDED
        st.session_state.validation_attempted = False  # ADDED
    
    def toast():
        st.toast("Optimizando")
        time.sleep(0.5)
        st.toast("Haciendo los cambios en la Base de Datos")
        time.sleep(0.5)
        st.toast("Listo", icon="🎉")
    
    # Funciones para cambiar el índice
    def next_usuario():
        if st.session_state.index_usuario < 2:  # Solo permitir hasta el índice 2 (tercer usuario)
            st.session_state.index_usuario += 1
        st.session_state.is_saved_usuario = False

    def prev_usuario():
        if st.session_state.index_usuario > 0:
            st.session_state.index_usuario -= 1
        st.session_state.is_saved_usuario = False
    
    def delete_usuario(identificador):
        Id_usuario = int(identificador)

        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM usuarios
            WHERE id = ?
            """,
            (Id_usuario,),
        )
        
    def edit_user_usuario(
        usuario_edit,
        clave_edit,
        estatus_edit,
        identificador,
    ):
        usuario = usuario_edit
        clave = clave_edit
        estatus = estatus_edit
        Id_usuario = int(identificador)

        conn = sqlite3.connect('jhotem.db')
        cursor = conn.cursor()

        try:
            # Ejecutar la consulta para actualizar el registro
            cursor.execute('''
            UPDATE usuarios
            SET usuario = ?, clave = ?, estatus = ?
            WHERE id = ?
            ''', (usuario, clave,estatus,Id_usuario))

            # Confirmar los cambios
            conn.commit()
            print("Credencial Actualizada Satisfactoriamente")
        except sqlite3.Error as e:
            st.error(f"Error al actualizar el usuario: {e}")
        finally:
            # Cerrar la conexión a la base de datos
            cursor.close()
            conn.close()

        # Recargar los datos después de guardar el nuevo usuario
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        rows = cursor.fetchall()
        
    # Mostrar los datos del usuario actual
    if st.session_state.is_new_user_usuario:
        current_user = st.session_state.new_test_data_usuario
    else:
        current_user = test_data_usuarios[st.session_state.index_usuario]
        
    lista_estatus = ['activo','inactivo'] 
    
    with placeholder.container():
        with col2:
            with st.container(height=70, border=True):
                left_co, cent_co, last_co = st.columns(3)
                with left_co:
                    st.markdown(
                        f"""
    <div style='display: flex; align-items: center; color: blue; font-size: 20px; font-weight: bold;'>
        <img src="data:image/png;base64,{img_str}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; border: 2px solid black;">
        Auto Diagnostico J.M.R.
    </div>
    """,
                        unsafe_allow_html=True,
                    )
                with last_co:
                    st.markdown(
                        f"""
                    <div style="display: flex; align-items: center; justify-content: flex-end;">
                        <div style="display: flex; flex-direction: column; align-items: flex-start;">
                            <span style="color: blue; font-size: 16px; font-weight: bold;">Modulo: Ajustes</span>
                            <span style="color: black; font-size: 14px; font-weight: bold;">Fecha: {fecha_formateada}</span>
                        </div>
                        <span style="margin-left: 10px;"></span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="blue" class="bi bi-gear-wide-connected" viewBox="0 0 16 16">
                            <path d="M7.068.727c.243-.97 1.62-.97 1.864 0l.071.286a.96.96 0 0 0 1.622.434l.205-.211c.695-.719 1.888-.03 1.613.931l-.08.284a.96.96 0 0 0 1.187 1.187l.283-.081c.96-.275 1.65.918.931 1.613l-.211.205a.96.96 0 0 0 .434 1.622l.286.071c.97.243.97 1.62 0 1.864l-.286.071a.96.96 0 0 0-.434 1.622l.211.205c.719.695.03 1.888-.931 1.613l-.284-.08a.96.96 0 0 0-1.187 1.187l.081.283c.275.96-.918 1.65-1.613.931l-.205-.211a.96.96 0 0 0-1.622.434l-.071.286c-.243.97-1.62.97-1.864 0l-.071-.286a.96.96 0 0 0-1.622-.434l-.205.211c-.695.719-1.888.03-1.613-.931l.08-.284a.96.96 0 0 0-1.186-1.187l-.284.081c-.96.275-1.65-.918-.931-1.613l.211-.205a.96.96 0 0 0-.434-1.622l-.286-.071c-.97-.243-.97-1.62 0-1.864l.286-.071a.96.96 0 0 0 .434-1.622l-.211-.205c-.719-.695-.03-1.888.931-1.613l.284.08a.96.96 0 0 0 1.187-1.186l-.081-.284c-.275-.96.918-1.65 1.613-.931l.205.211a.96.96 0 0 0 1.622-.434zM12.973 8.5H8.25l-2.834 3.779A4.998 4.998 0 0 0 12.973 8.5m0-1a4.998 4.998 0 0 0-7.557-3.779l2.834 3.78zM5.048 3.967l-.087.065zm-.431.355A4.98 4.98 0 0 0 3.002 8c0 1.455.622 2.765 1.615 3.678L7.375 8zm.344 7.646.087.065z"/>
                        </svg>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            def download_excel():
                # Obtener el directorio actual del script
                current_dir = os.path.dirname(os.path.abspath(__file__))

                # Ruta de la base de datos relativa al directorio actual del script
                ruta_base_de_datos = os.path.join(current_dir, "jhotem.db")

                # Verificar si el archivo de la base de datos existe
                if not os.path.exists(ruta_base_de_datos):
                    st.error(f"El archivo de la base de datos no se encuentra en la ruta: {ruta_base_de_datos}")
                else:
                    # Conectar a la base de datos
                    conn = sqlite3.connect(ruta_base_de_datos)

                    # Leer todas las tablas de la base de datos en DataFrames
                    tablas = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
                    dataframes = {}

                    for tabla in tablas['name']:
                        dataframes[tabla] = pd.read_sql_query(f"SELECT * from {tabla}", conn)

                    # Crear un archivo Excel en memoria
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for tabla, df in dataframes.items():
                            df.to_excel(writer, sheet_name=tabla, index=False)

                    # Cerrar la conexión a la base de datos
                    conn.close()

                    # Botón para descargar el archivo Excel
                    st.download_button(
                        label="Descargar Backup de la Base de Datos en Excel",
                        data=output.getvalue(),
                        file_name="backup_jhotem.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
            def download_sql():
                # Obtener el directorio actual del script
                current_dir = os.path.dirname(os.path.abspath(__file__))

                # Ruta de la base de datos relativa al directorio actual del script
                ruta_base_de_datos = os.path.join(current_dir, "jhotem.db")

                # Verificar si el archivo de la base de datos existe
                if not os.path.exists(ruta_base_de_datos):
                    st.error(f"El archivo de la base de datos no se encuentra en la ruta: {ruta_base_de_datos}")
                else:
                    # Leer el archivo de la base de datos en formato binario
                    with open(ruta_base_de_datos, "rb") as f:
                        archivo_binario = f.read()

                    # Crear un objeto BytesIO para simular un archivo en memoria
                    archivo_en_memoria = io.BytesIO(archivo_binario)

                    # Obtener el directorio de descargas del usuario
                    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')

                    # Nombre del archivo sugerido en la carpeta de descargas
                    suggested_file_name = os.path.join(downloads_dir, os.path.basename(ruta_base_de_datos))

                    # Botón para descargar el archivo de la base de datos
                    st.download_button(
                        label="Descargar Base de Datos",
                        data=archivo_en_memoria,
                        file_name=suggested_file_name,
                        mime="application/octet-stream"
                    )
                
            def salir_master_key():
                st.session_state.validated = False
                st.session_state.validation_attempted = False
            
            
            def validate_master(user_m,clave_m): # Funcion valida el master login
                if user_m != m_user and clave_m != m_clave:
                    with cont_1:
                        st.warning("Please entre a valid User/Password")
                    return False
                    
                elif user_m == m_user and clave_m == m_clave:
                    st.session_state.validated = True
                    return True
                
            with st.container(height=550, border=True):
                tab1, tab2 = st.tabs(
                    [
                        "Gestión de Usuarios",
                        "Backup Base de Datos",
                    ]
                )
                with tab1:
                    # CONTAINER: ENCABEZADO DE LA FICHA
                    with st.container(height=40, border=False):
                        
                        cont_1, cont_2, cont_3 = st.columns([3,1,3])
                        
                    if st.session_state.validated:
                            with cont_3:
                                st.markdown(
                                    """
                                    <div style="height: 10px;"></div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    """
                                    <p style="font-size: 14px; color: blue; font-weight: bold; text-align: center;">
                                        GESTION DE CREDENCIALES AUTORIZADAS 
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                    
                    with st.container(height=50, border=False):
                        dont_1, dont_2, dont_3, dont_4, dont_5,dont_6 = st.columns([6,5,3.2,1.5,1.2,1])
                        with dont_1:
                            st.markdown(
                                """
                                <p style="font-size: 24px; color: #ea882a; font-weight: bold; text-align: center; display: flex; justify-content: center; align-items: center;">
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Login&nbsp;<span style="display: inline-block;">Master&nbsp;Key</span>&nbsp;
                                    <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" fill="blue" class="bi bi-key-fill" viewBox="0 0 16 16" style="display: inline-block; vertical-align: middle; font-weight: bold;">
                                        <path d="M3.5 11.5a3.5 3.5 0 1 1 3.163-5H14L15.5 8 14 9.5l-1-1-1 1-1-1-1 1-1-1-1 1H6.663a3.5 3.5 0 0 1-3.163 2M2.5 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2"/>
                                    </svg>
                                </p>
                                """,
                                unsafe_allow_html=True
                            )
                    if st.session_state.validated:
                            with dont_3:
                                st.markdown(
                                f"<span style='color:blue;font-weight:bold;font-size:12px;'>USUARIO ID N° {current_user[0]}</span>"
                                f"<br><span style='color:blue;font-weight:bold;font-size:12px;'>Total Credenciales: {len(test_data_usuarios)-1}</span>",
                                unsafe_allow_html=True,
                            )
                            with dont_4:
                                st.button("Prev.", key="prev_mod_user",on_click=prev_usuario)
                                
                            with dont_5:
                                st.button("Sig.", key="siguiente_mod_user", on_click=next_usuario)
                    
                    with st.container(height=280, border=False):
                        font_1, font_2, font_3, font_4,font_5,font_6, font_7 = st.columns([0.5,3,0.5,1,0.5,3,0.5])
                        with font_2:
                            st.markdown(
                                """
                                <p style="font-size: 16px; color: blue; font-weight: bold; text-align: center;">
                                    Para continuar debe introducir la clave 'Maestra' asignada 
                                </p>
                                """,
                                unsafe_allow_html=True,
                            )
                            
                            username = st.text_input(
                                        "Usuario", on_change=None, key="verified_user"
                                    )

                            password = st.text_input(
                                "Clave",
                                on_change=None,
                                key="master_clave",
                                type="password",
                            )
                            if st.button("Submit", key="ingreso_master_key"):
                                if not st.session_state.validation_attempted:
                                    if validate_master(username, password):
                                        st.session_state.validation_attempted = True
                                        st.rerun()
                                    else:
                                        st.session_state.validation_attempted = False
                    if st.session_state.validated:
                        with font_6:
                            identificador = current_user[0]
                            usuario_actual = st.text_input(
                                            "Usuario actual :",
                                            on_change=None,
                                            value=current_user[1],
                                            key=f"modify_usuer_{current_user[0]}",
                                        )
                            clave_actual = st.text_input(
                                    "Clave actual :",
                                    on_change=None,
                                    value=current_user[2],
                                    key=f"modify_password_{current_user[0]}",
                                )
                            
                            posicion_en_lista = lista_estatus.index(current_user[3])
                            
                            estatus_actual = st.selectbox(
                                    "Estatus actual :", lista_estatus,
                                    on_change=None,
                                    index=posicion_en_lista,
                                    key=f"current_status_{current_user[0]}",
                                )
                    else:
                        with font_6:
                            with st.container(height=270, border=True):
                                st.markdown(
                                    """
                                    <p style="font-size: 14px; color: blue; font-weight: bold; text-align: center;">
                                        SOFTWARE DE GESTIÓN ADMINISTRATIVA 
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                st.markdown(
                                    """
                                    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Impact:400,800&display=swap">
                                    <div style='font-size: 42px; font-weight: 900; color: blue; font-family: "Arial", sans-serif; text-align: center; width: 100%;'>
                                        <div style='display: inline-block; border-bottom: 3px solid black; padding-bottom: 1px; margin-bottom: -2px;'>
                                            Ti<span style='color: #ea882a;'>i</span>gerSoft<span style='font-size: 52px;'></span><sup>&copy;</sup>
                                            <span style='font-size: 10px; color: black; margin-left: 5px; vertical-align: baseline;'>v 1.0</span>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                streamlit_space.space(container=None, lines=1)
                                st.markdown(
                                        f"""
                                        <div style="display: flex; align-items: center; justify-content: center;">
                                            <img src="data:image/png;base64,{tiger_peq_img}" style="width: 87px; height: 103px; margin-right: 20px;" />
                                            <div style="display: flex; flex-direction: column; align-items: center;">
                                                <p style='text-align: center; color: grey; font-size: 24px;'>
                                                    Version: <span style='font-weight: bold; color: blue;'>1.0</span>
                                                </p>
                                                <p style='text-align: center; color: grey; font-size: 12px;'>
                                                    Powered by <span style='font-weight: bold; color: blue;'>White Labs Technologies</span>
                                                </p>
                                            </div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                )
                # if st.session_state.validated:    
                    with st.container(height=50, border=False):
                        eont_1, eont_2, eont_3, eont_4, eont_5, eont_6 = st.columns([5.6,2,6.2,2,1.5,1])
                        if st.session_state.validated: 
                            with eont_4:
                                if st.button("Modificar", key="mod_user"):
                                    edit_user_usuario(usuario_actual,clave_actual,estatus_actual, identificador)
                                    toast()
                            with eont_5:
                                if st.button("Salir", key="del_mod_user"):
                                    salir_master_key()
                                    st.rerun()
                with tab2:
                    gont_1, gont_2 = st.columns(2)
                    # CONTAINER: ENCABEZADO DE LA FICHA
                    if st.session_state.validated:
                        with gont_1:
                            with st.container(height=440, border=True):
                                
                                streamlit_space.space(container=None, lines=1)
                                st.markdown(
                                    """
                                    <p style="font-size: 24px; color: blue; font-weight: bold; text-align: center;">
                                        GESTION DE BASE DE DATOS 
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                streamlit_space.space(container=None, lines=2)
                                
                                excel_file_content = """
                                <p style="font-size: 14px; color: blue; font-weight: bold; text-align: center;">
                                    Formato Excel <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="#ea882a" class="bi bi-filetype-xls" viewBox="0 0 16 16" style="display: inline-block; vertical-align: middle; margin-bottom: 10px;">
                                        <path fill-rule="evenodd" d="M14 4.5V14a2 2 0 0 1-2 2h-1v-1h1a1 1 0 0 0 1-1V4.5h-2A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v9H2V2a2 2 0 0 1 2-2h5.5zM6.472 15.29a1.2 1.2 0 0 1-.111-.449h.765a.58.58 0 0 0 .254.384q.106.073.25.114.143.041.319.041.246 0 .413-.07a.56.56 0 0 0 .255-.193.5.5 0 0 0 .085-.29.39.39 0 0 0-.153-.326q-.152-.12-.462-.193l-.619-.143a1.7 1.7 0 0 1-.539-.214 1 1 0 0 1-.351-.367 1.1 1.1 0 0 1-.123-.524q0-.366.19-.639.19-.272.527-.422.338-.15.777-.149.457 0 .78.152.324.153.5.41.18.255.2.566h-.75a.56.56 0 0 0-.12-.258.6.6 0 0 0-.247-.181.9.9 0 0 0-.369-.068q-.325 0-.513.152a.47.47 0 0 0-.184.384q0 .18.143.3a1 1 0 0 0 .405.175l.62.143q.326.075.566.211a1 1 0 0 1 .375.358q.135.222.135.56 0 .37-.188.656a1.2 1.2 0 0 1-.539.439q-.351.158-.858.158-.381 0-.665-.09a1.4 1.4 0 0 1-.478-.252 1.1 1.1 0 0 1-.29-.375m-2.945-3.358h-.893L1.81 13.37h-.036l-.832-1.438h-.93l1.227 1.983L0 15.931h.861l.853-1.415h.035l.85 1.415h.908L2.253 13.94zm2.727 3.325H4.557v-3.325h-.79v4h2.487z"/>
                                    </svg>
                                </p>
                                """

                                sql_lite_content = """
                                <p style="font-size: 14px; color: blue; font-weight: bold; text-align: center;">
                                    Formato Sqlite (Código binario) <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="#ea882a" class="bi bi-database-down" viewBox="0 0 16 16" style="display: inline-block; vertical-align: middle;">
                                        <path d="M12.5 9a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7m.354 5.854 1.5-1.5a.5.5 0 0 0-.708-.708l-.646.647V10.5a.5.5 0 0 0-1 0v2.793l-.646-.647a.5.5 0 0 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0"/>
                                        <path d="M12.096 6.223A5 5 0 0 0 13 5.698V7c0 .289-.213.654-.753 1.007a4.5 4.5 0 0 1 1.753.25V4c0-1.007-.875-1.755-1.904-2.223C11.022 1.289 9.573 1 8 1s-3.022.289-4.096.777C2.875 2.245 2 2.993 2 4v9c0 1.007.875 1.755 1.904 2.223C4.978 15.71 6.427 16 8 16c.536 0 1.058-.034 1.555-.097a4.5 4.5 0 0 1-.813-.927Q8.378 15 8 15c-1.464 0-2.766-.27-3.682-.687C3.356 13.875 3 13.373 3 13v-1.302c.271.202.58.378.904.525C4.978 12.71 6.427 13 8 13h.027a4.6 4.6 0 0 1 0-1H8c-1.464 0-2.766-.27-3.682-.687C3.356 10.875 3 10.373 3 10V8.698c.271.202.58.378.904.525C4.978 9.71 6.427 10 8 10q.393 0 .774-.024a4.5 4.5 0 0 1 1.102-1.132C9.298 8.944 8.666 9 8 9c-1.464 0-2.766-.27-3.682-.687C3.356 7.875 3 7.373 3 7V5.698c.271.202.58.378.904.525C4.978 6.711 6.427 7 8 7s3.022-.289 4.096-.777M3 4c0-.374.356-.875 1.318-1.313C5.234 2.271 6.536 2 8 2s2.766.27 3.682.687C12.644 3.125 13 3.627 13 4c0 .374-.356.875-1.318 1.313C10.766 5.729 9.464 6 8 6s-2.766-.27-3.682-.687C3.356 4.875 3 4.373 3 4"/>
                                    </svg>
                                </p>
                                """
                                # streamlit_space.space(container=None, lines=1)
                                # Opciones para el st.radio
                                
                                # Mostrar el st.radio con las opciones
                                selected_option = st.radio(
                                    "Elija el formato a descargar",
                                    [":orange[Formato Excel]", ":orange[Formato Base de Datos]"],
                                    key="visibility",
                                    horizontal=True,
                                )
                                # Mostrar el contenido seleccionado
                                if selected_option == ":orange[Formato Excel]":
                                    st.markdown(excel_file_content, unsafe_allow_html=True)
                                elif selected_option == ":orange[Formato Base de Datos]":
                                    st.markdown(sql_lite_content, unsafe_allow_html=True)
                                
                                if st.button("Seleccionar", key="boton_selector_file"):
                                    if selected_option ==  ":orange[Formato Base de Datos]":
                                        download_sql()
                                    elif selected_option == ":orange[Formato Excel]":
                                        download_excel()
                                streamlit_space.space(container=None, lines=1)
                                
                                st.markdown(
                                    """
                                    <p style="font-size: 14px; color: blue; font-weight: bold; text-align: center;">
                                        Nota: El archivo elegido sera descagado en la carpeta 'Download' <br> de su navegador
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                        with gont_2:
                                with st.container(height=440, border=True):
                                    streamlit_space.space(container=None, lines=3)
                                    st.markdown(
                                        """
                                        <p style="font-size: 24px; color: blue; font-weight: bold; text-align: center;">
                                            SOFTWARE DE<br>GESTIÓN ADMINISTRATIVA 
                                        </p>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                    st.markdown(
                                        """
                                        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Impact:400,800&display=swap">
                                        <div style='font-size: 42px; font-weight: 900; color: blue; font-family: "Arial", sans-serif; text-align: center; width: 100%;'>
                                            <div style='display: inline-block; border-bottom: 3px solid black; padding-bottom: 1px; margin-bottom: -2px;'>
                                                Ti<span style='color: #ea882a;'>i</span>gerSoft<span style='font-size: 52px;'></span><sup>&copy;</sup>
                                                <span style='font-size: 10px; color: black; margin-left: 5px; vertical-align: baseline;'>v 1.0</span>
                                            </div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                    streamlit_space.space(container=None, lines=1)
                                    st.markdown(
                                            f"""
                                            <div style="display: flex; align-items: center; justify-content: center;">
                                                <img src="data:image/png;base64,{tiger_peq_img}" style="width: 87px; height: 103px; margin-right: 20px;" />
                                                <div style="display: flex; flex-direction: column; align-items: center;">
                                                    <p style='text-align: center; color: grey; font-size: 24px;'>
                                                        Version: <span style='font-weight: bold; color: blue;'>1.0</span>
                                                    </p>
                                                    <p style='text-align: center; color: grey; font-size: 12px;'>
                                                        Powered by <span style='font-weight: bold; color: blue;'>White Labs Technologies</span>
                                                    </p>
                                                </div>
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                    )
                                    streamlit_space.space(container=None, lines=3)
                                    st.markdown(
                                    """
                                    <p style="font-size: 10px; color: blue; font-weight: bold; text-align: center;">
                                        (Espacio disponible para uso futuro)
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                    else:
                        with gont_1:
                            with st.container(height=440, border=True):
                                st.markdown(
                                    """
                                    <div style="height: 80px;"></div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    """
                                    <p style="font-size: 24px; color: blue; font-weight: bold; text-align: center;">
                                        GESTIÓN <br>DE BASE DE DATOS 
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                st.markdown(
                                    """
                                    <div style="height: 20px;"></div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    """
                                    <p style="font-size: 20px; color: #ea882a; font-weight: bold; text-align: center;">
                                        Módulo Restringido <br>Para avanzar debe introducir <br>la 'Clave Maestra' en la pestaña anterior
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            with gont_2:
                                with st.container(height=440, border=True):
                                    streamlit_space.space(container=None, lines=3)
                                    st.markdown(
                                        """
                                        <p style="font-size: 24px; color: blue; font-weight: bold; text-align: center;">
                                            SOFTWARE DE<br>GESTIÓN ADMINISTRATIVA 
                                        </p>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                    st.markdown(
                                        """
                                        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Impact:400,800&display=swap">
                                        <div style='font-size: 42px; font-weight: 900; color: blue; font-family: "Arial", sans-serif; text-align: center; width: 100%;'>
                                            <div style='display: inline-block; border-bottom: 3px solid black; padding-bottom: 1px; margin-bottom: -2px;'>
                                                Ti<span style='color: #ea882a;'>i</span>gerSoft<span style='font-size: 52px;'></span><sup>&copy;</sup>
                                                <span style='font-size: 10px; color: black; margin-left: 5px; vertical-align: baseline;'>v 1.0</span>
                                            </div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                    streamlit_space.space(container=None, lines=1)
                                    st.markdown(
                                            f"""
                                            <div style="display: flex; align-items: center; justify-content: center;">
                                                <img src="data:image/png;base64,{tiger_peq_img}" style="width: 87px; height: 103px; margin-right: 20px;" />
                                                <div style="display: flex; flex-direction: column; align-items: center;">
                                                    <p style='text-align: center; color: grey; font-size: 24px;'>
                                                        Version: <span style='font-weight: bold; color: blue;'>1.0</span>
                                                    </p>
                                                    <p style='text-align: center; color: grey; font-size: 12px;'>
                                                        Powered by <span style='font-weight: bold; color: blue;'>White Labs Technologies</span>
                                                    </p>
                                                </div>
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                    )
                                    streamlit_space.space(container=None, lines=3)
                                    st.markdown(
                                    """
                                    <p style="font-size: 10px; color: blue; font-weight: bold; text-align: center;">
                                        (Espacio disponible para uso futuro)
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                
                                
                                
                
# Pagina Clientes
def home():

    # Carga de datos a una lista desde la base de datos jhotem.db
    # Conectar a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()

    # Cargar los datos de la tabla 'clientes'
    cursor.execute("SELECT * FROM clientes")
    rows = cursor.fetchall()

    test_data_2 = [list(row) for row in rows]
    new_test_data = []
    if "index" not in st.session_state:
        st.session_state.index = 0

    if "new_test_data" not in st.session_state:
        st.session_state.new_test_data = []
    if "is_new_user" not in st.session_state:
        st.session_state.is_new_user = False
    if "is_saved" not in st.session_state:  # ADDED
        st.session_state.is_saved = False  # ADDED

    def toast():
        st.toast("Optimizando")
        time.sleep(0.5)
        st.toast("Confirmandos cambios en la Base de Datos")
        time.sleep(0.5)
        st.toast("Listo", icon="🎉")

    # Funciones para cambiar el índice
    def next_user():
        if st.session_state.index < len(test_data_2) - 1:
            st.session_state.index += 1
        st.session_state.is_saved = False  # ADDED

    def prev_user():
        if st.session_state.index > 0:
            st.session_state.index -= 1
        st.session_state.is_saved = False  # ADDED

    def delete_user(identificador):
        id = int(identificador)

        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM clientes
            WHERE id = ?
            """,
            (id,),
        )

        conn.commit()
        # conn.close()

    def edit_user(
        nombre,
        apellido,
        cedula,
        telefono,
        direccion,
        correo_electronico,
        nota,
        fecha,
        identificador,
    ):
        nombre = nombre
        apellido = apellido
        cedula = cedula
        telefono = telefono
        direccion = direccion
        correo_electronico = correo_electronico
        nota = nota
        fecha = fecha
        id = int(identificador)

        # new_test_data = st.session_state.new_test_data
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()

        # Consulta SQL corregida
        cursor.execute(
            """
            UPDATE clientes 
            SET nombre = ?, apellido = ?, cedula = ?, telefono = ?, direccion = ?, correo_electronico = ?, nota = ?, fecha = ?
            WHERE id = ?
        """,
            (
                nombre,
                apellido,
                cedula,
                telefono,
                direccion,
                correo_electronico,
                nota,
                fecha,
                id,
            ),
        )

        conn.commit()
        # conn.close()

    def save_new_user(
        nombre, apellido, cedula, telefono, direccion, correo_electronico, nota, fecha
    ):
        nombre = nombre
        apellido = apellido
        cedula = cedula
        telefono = telefono
        direccion = direccion
        correo_electronico = correo_electronico
        nota = nota
        fecha = fecha

        new_test_data = st.session_state.new_test_data
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nombre, apellido, cedula, telefono, direccion, correo_electronico, nota, fecha) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                nombre,
                apellido,
                cedula,
                telefono,
                direccion,
                correo_electronico,
                nota,
                fecha,
            ),
        )
        conn.commit()

        # Recargar los datos después de guardar el nuevo usuario
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        rows = cursor.fetchall()
        # conn.close()

        st.session_state.index = len(rows) - 1  # Establecer el índice al último usuario
        return [list(row) for row in rows]

    # Mostrar los datos del usuario actual
    if st.session_state.is_new_user:
        current_user = st.session_state.new_test_data
    else:
        current_user = test_data_2[st.session_state.index]

    with placeholder.container():

        # HEADER PAGINA
        with col2:
            with st.container(height=70, border=True):
                left_co, cent_co, last_co = st.columns(3)
                with left_co:
                    st.markdown(
                        f"""
    <div style='display: flex; align-items: center; color: blue; font-size: 20px; font-weight: bold;'>
        <img src="data:image/png;base64,{img_str}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; border: 2px solid black;">
        Auto Diagnostico J.M.R.
    </div>
    """,
                        unsafe_allow_html=True,
                    )
                with last_co:

                    st.markdown(
                        f"""
    <div style="display: flex; align-items: center; justify-content: flex-end;">
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
            <span style="color: blue; font-size: 16px; font-weight: bold;">Modulo: Clientes</span>
            <span style="color: black; font-size: 14px; font-weight: bold;">Fecha: {fecha_formateada}</span>
        </div>
        <span style="margin-left: 10px;"></span>
        <svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="blue" class="bi bi-person-vcard" viewBox="0 0 16 16">
            <path d="M5 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4m4-2.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1h-4a.5.5 0 0 1-.5-.5M9 8a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1h-4A.5.5 0 0 1 9 8m1 2.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5"/>
            <path d="M2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zM1 4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H8.96q.04-.245.04-.5C9 10.567 7.21 9 5 9c-2.086 0-3.8 1.398-3.984 3.181A1 1 0 0 1 1 12z"/>
        </svg>
    </div>
    """,
                        unsafe_allow_html=True,
                    )

            # MAIN CONTAINER: 1ER FRAME
            # SECOND CONTAINER 2DO FRAME
            with st.container(height=550, border=True):
                tab1, tab2, tab3 = st.tabs(
                    [
                        "Nuevo Cliente",
                        "Gestión de Clientes",
                        "Reporte de Clientes",
                    ]
                )
                # FICHA DE LOS REPORTES
                with tab3:
                    # CONTAINER: ENCABEZADO DE LA FICHA
                    with st.container(height=50, border=False):
                        cont_1, cont_2, cont_3 = st.columns([1, 2, 1])
                        with cont_1:
                            st.markdown(
                                "<span style='font-size: 20px; color: blue; font-weight: bold;'>REPORTE CLIENTES</span>",
                                unsafe_allow_html=True,
                            )
                            # streamlit_space.space(container=None, lines=1)

                        with cont_2:
                            search_term = st.text_input(
                                "Buscar",
                                label_visibility="collapsed",
                                placeholder="Buscar",
                                on_change=None,
                                key="search_box",
                            )
                        with cont_3:
                            if st.button("Limpiar"):
                                search_term = ""
                    # CONTAINER BODY: REPORTE DE DATOS
                    with st.container(height=350, border=False):
                        df_report = pd.DataFrame(
                            test_data_2,
                            columns=[
                                "ID",
                                "Nombre",
                                "Apellido",
                                "Cédula",
                                "Teléfono",
                                "Dirección",
                                "Correo Electrónico",
                                "Nota",
                                "Fecha",
                            ],
                        )
                        if search_term:
                            # Filtrar por si el término de búsqueda aparece en cualquier columna
                            df_filtered = df_report[
                                df_report.apply(
                                    lambda row: row.astype(str)
                                    .str.contains(search_term, case=False)
                                    .any(),
                                    axis=1,
                                )
                            ]
                        else:
                            df_filtered = df_report

                        st.dataframe(df_filtered)
                    # CONTAINER: COPYRIGHT
                    with st.container(height=50, border=False):
                        ult_1, ult_2, ult_3 = st.columns([1, 2, 1])
                        with ult_2:
                            st.write(
                                "© 2024 WhiteLabs Technologies - Todos los derechos reservados   "
                            )
                # FICHA DE CLIENTES ACTUALES
                with tab2:
                    # CONTAINER: ENCABEZADO DE LA FICHA
                    with st.container(height=50, border=False):
                        (
                            column_izq,
                            column_center,
                            column_der,
                            column_uno,
                            column_dos,
                            column_tres,
                        ) = st.columns([3, 3, 4, 3, 1.7, 1.7])
                        with column_izq:
                            # streamlit_space.space(container=None, lines=0)

                            st.markdown(
                                f"<span style='color:blue;font-weight:bold;'>ID N° {current_user[0]+1} / Total Registros: {len(test_data_2)}</span>",
                                unsafe_allow_html=True,
                            )
                        if not st.session_state.is_new_user:
                            with column_der:
                                st.markdown(
                                "<span style='font-size: 16px; color: blue; font-weight: bold;'>CLIENTES ACTUALES</span>",
                                unsafe_allow_html=True,
                            )
                            with column_dos:
                                boton_3 = st.button(
                                    "Previo", key="previo", on_click=prev_user
                                )
                            with column_tres:
                                boton_2 = st.button(
                                    "Siguiente", key="siguiente", on_click=next_user
                                )

                    # CONTAINER BODY: BODY
                    with st.container(height=350, border=True):
                        izquierda, derecha = st.columns(2)
                        with izquierda:
                            nombre = st.text_input(
                                "Nombre / Razón Social:",
                                value=current_user[1],
                                on_change=None,
                                key=f"nombre_{current_user[0]}",
                            )
                            ci_rif = st.text_input(
                                "C.I./ RIF :",
                                value=current_user[3],
                                on_change=None,
                                key=f"cedula_{current_user[0]}",
                            )
                            direccion = st.text_input(
                                "Dirección:",
                                value=current_user[5],
                                on_change=None,
                                key=f"direccion_{current_user[0]}",
                            )
                            observaciones = st.text_input(
                                "Observaciones:",
                                value=current_user[7],
                                on_change=None,
                                key=f"observaciones_{current_user[0]}",
                            )

                        with derecha:
                            apellido = st.text_input(
                                "Apellido:",
                                value=current_user[2],
                                on_change=None,
                                key=f"apellido_{current_user[0]}",
                            )
                            telefono = st.text_input(
                                "Telefonos:",
                                value=current_user[4],
                                on_change=None,
                                key=f"telefono_{current_user[0]}",
                            )
                            email = st.text_input(
                                "Correo electrónico:",
                                value=current_user[6],
                                on_change=None,
                                key=f"email_{current_user[0]}",
                            )
                            # Convertir las fechas en las sublistas directamente
                            current_user[8] = datetime.strptime(
                                current_user[8], "%Y-%m-%d"
                            ).date()
                            fecha = st.date_input(
                                "Fecha:",
                                value=current_user[8],
                                on_change=None,
                                key=f"fecha_{current_user[0]}",
                            )

                    with st.container(height=60, border=False):
                        linea_1, linea_2, linea_3, linea_4 = st.columns([6, 1, 1, 1])
                        with linea_3:
                            boton_1 = st.button("Modificar", key="guardar")
                        with linea_4:
                            boton_elimi_clien = st.button(
                                "Eliminar", key="eliminar_cliente"
                            )
                        identificador = current_user[0] - 1
                        if not st.session_state.is_saved:
                            if boton_1:
                                toast()
                                st.session_state.is_saved = True
                                edit_user(
                                    nombre,
                                    apellido,
                                    ci_rif,
                                    telefono,
                                    direccion,
                                    email,
                                    observaciones,
                                    fecha,
                                    identificador,
                                )
                            if boton_elimi_clien:
                                toast()
                                delete_user(identificador)
                                
                # FICHA NUEVOS CLIENTES
                with tab1:
                    with st.container(height=50, border=False):
                        (
                            column_izq,
                            column_center,
                            column_der,
                            column_uno,
                            column_dos,
                            column_tres,
                        ) = st.columns([4, 3, 4, 3, 1.7, 1.7])
                        with column_izq:
                            # streamlit_space.space(container=None, lines=0)

                            new_register = len(test_data_2) + 1
                            st.markdown(
                                f"<span style='font-size: 14px; color: blue; font-weight: bold;'>NUEVO CLIENTE SERÁ EL ID N° {new_register}</span>",
                                unsafe_allow_html=True,
                            )
                        with column_der:

                            new_register = len(test_data_2) + 1
                            st.markdown(
                                "<span style='font-size: 16px; color: blue; font-weight: bold;'>FORMATO NUEVOS CLIENTES</span>",
                                unsafe_allow_html=True,
                            )
                    # MAIN CONTAINER - ESTAN LAS TABS AQUI
                    with st.container(height=350, border=True):
                        izquierda, derecha = st.columns(2)
                        with izquierda:
                            nombre_new = st.text_input(
                                "Nombre / Razón Social: (Si es empresa coloque el nombre de la misma aqui)",
                            )
                            ci_rif_new = st.text_input("C.I./ RIF :")
                            direccion_new = st.text_input("Dirección:")
                            observaciones_new = st.text_input(
                                "Observaciones:",
                                on_change=None,
                            )

                        with derecha:
                            apellido_new = st.text_input("Apellido:")
                            telefono_new = st.text_input("Telefonos:")
                            email_new = st.text_input(
                                "Correo electrónico:",
                                on_change=None,
                                key="email_new",
                            )
                            fecha_new = st.date_input("Fecha:", key="fecha_new")
                        # Condicional para e uso de los botones de Previo y Siguiente

                        # Espacio en blanco para los botones
                        # streamlit_space.space(container=None, lines=2)

                    with st.container(height=60, border=False):
                        lin_1, lin_2, lin_3, lin_4 = st.columns([2, 1, 1, 1])
                        with lin_4:
                            boton_1_tab1 = st.button(
                                "Guardar Nuevo Cliente", key="guardar_nuevo_tab1"
                            )
                        if not st.session_state.is_saved:
                            if boton_1_tab1:
                                toast()

                                st.session_state.is_saved = True
                                save_new_user(
                                    nombre_new,
                                    apellido_new,
                                    ci_rif_new,
                                    telefono_new,
                                    direccion_new,
                                    email_new,
                                    observaciones_new,
                                    fecha_new,
                                )
                    # Tab de Reportes


# Pagina Vehiculos
def vehiculos():

    # Carga de datos a una lista desde la base de datos jhotem.db
    # Conectar a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()

    # Cargar los datos de la tabla 'clientes'
    cursor.execute("SELECT * FROM vehiculos")
    rows = cursor.fetchall()

    test_data_veh = [list(row) for row in rows]
    new_test_data_veh = []

    # Consulta para obtener los datos de la tabla vehiculos junto con el nombre del cliente
    cursor.execute(
        """
        SELECT v.vehiculos_id, c.nombre, c.apellido, v.marca, v.modelo, v.year, v.placa, v.fecha_entrada, v.observaciones
        FROM vehiculos v
        JOIN clientes c ON v.cliente_id = c.id
    """
    )
    filas = cursor.fetchall()

    # print(filas)

    # Crear la conexión a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()

    # Consulta para obtener los valores de los campos 'nombre' y 'apellido' junto con 'id' de la tabla 'clientes'
    cursor.execute(
        """
    SELECT nombre, apellido FROM clientes
    """
    )
    clientes_veh = cursor.fetchall()

    # Unificación de nombre y apellido del cliente
    temporal_veh = []
    for cliente in clientes_veh:
        nombre, apellido = cliente
        nombre_completo = f"{nombre} {apellido}"
        temporal_veh.append(nombre_completo)

    # print(temporal_veh)

    # Consulta para obtener los valores de los campos 'nombre' y 'apellido' junto con 'id' de la tabla 'clientes'
    cursor.execute(
        """
    SELECT id FROM clientes
    """
    )
    clientes_id_capture = cursor.fetchall()

    # print(clientes_id_capture)

    # Convertir las tuplas en clientes_id_capture a enteros
    clientes_id_capture_cleaned = [int(str(item)[1:-2]) for item in clientes_id_capture]

    # Crear el diccionario
    result_dict = {
        key: value for key, value in zip(clientes_id_capture_cleaned, temporal_veh)
    }

    dict_inverse = {
        key: value for key, value in zip(temporal_veh, clientes_id_capture_cleaned)
    }
    # print(dict_inverse)
    # print(result_dict)
    if "index_veh" not in st.session_state:
        st.session_state.index_veh = 0

    if "new_test_data_veh" not in st.session_state:
        st.session_state.new_test_data_veh = []
    if "is_new_user_veh" not in st.session_state:
        st.session_state.is_new_user_veh = False
    if "is_saved_veh" not in st.session_state:  # ADDED
        st.session_state.is_saved_veh = False  # ADDED

    # Estilo de boton en azul para el futuro
    #     boton_estilo = """
    # <style>
    # div.stButton > button:first-child {
    #     background-color: blue !important;
    #     color: white !important;
    #     border: 2px solid blue !important;
    #     border-radius: 5px;
    #     padding: 5px 20px; /* Reducir el padding superior e inferior a 5px */
    #     transition: background-color 0.3s, color 0.3s, border-color 0.3s, transform 0.3s;
    # }

    # div.stButton > button:first-child:hover {
    #     border-color: white !important;
    # }

    # div.stButton > button:first-child:active {
    #     background-color: white !important;
    #     color: blue !important;
    #     transform: scale(0.95);
    # }
    # </style>
    # """
    #     # Aplicar el estilo CSS
    #     st.markdown(boton_estilo, unsafe_allow_html=True)

    def toast():
        st.toast("Optimizando")
        time.sleep(0.5)
        st.toast("Haciendo los cambios en la Base de Datos")
        time.sleep(0.5)
        st.toast("Listo", icon="🎉")

    # Funciones para cambiar el índice
    def next_user():
        if st.session_state.index_veh < len(test_data_veh) - 1:
            st.session_state.index_veh += 1
        st.session_state.is_saved_veh = False  # ADDED

    def prev_user():
        if st.session_state.index_veh > 0:
            st.session_state.index_veh -= 1
        st.session_state.is_saved_veh = False  # ADDED

    def delete_vehicle(identificador):
        id = int(identificador)

        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM vehiculos
            WHERE vehiculos_id = ?
            """,
            (id,),
        )

        conn.commit()
        # conn.close()

    def edit_user_veh(
        marca_veh,
        modelo_veh,
        year_veh,
        placa_veh,
        fecha_veh,
        observaciones_veh,
        temporal_veh,
        selector1,
        identificador,
    ):
        marca = marca_veh
        modelo = modelo_veh
        year = year_veh
        placa = placa_veh
        fecha = fecha_veh
        observaciones = observaciones_veh
        temporal_veh = temporal_veh
        selector1 = selector1
        vehiculos_id = identificador

        # Busqueda del propietario (si este fue modificado)
        nombre_buscado = selector1.lower()

        # Buscar las posiciones del nombre en la lista
        posiciones = []

        for i, cliente in enumerate(temporal_veh):
            if cliente.lower() == nombre_buscado:
                posiciones.append(i)

        cliente_id = posiciones[0]

        # new_test_data = st.session_state.new_test_data
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()

        # Consulta SQL corregida
        cursor.execute(
            """
            UPDATE vehiculos
            SET marca = ?, modelo = ?, year = ?, placa = ?, fecha_entrada = ?, observaciones = ?, cliente_id = ?
            WHERE vehiculos_id = ?
        """,
            (
                marca,
                modelo,
                year,
                placa,
                fecha,
                observaciones,
                cliente_id,
                vehiculos_id,
            ),
        )

        conn.commit()
        # conn.close()

    def save_new_vehicle(
        new_register,
        selector_veh_new,
        marca_veh_new,
        modelo_veh_new,
        year_veh_new,
        placa_veh_new,
        fecha_veh_new,
        observaciones_veh_new,
        temporal_veh,
    ):
        vehiculos_id = new_register
        marca = marca_veh_new
        modelo = modelo_veh_new
        year = int(year_veh_new)
        placa = placa_veh_new
        fecha = fecha_veh_new
        observaciones = observaciones_veh_new

        # print(f"Esta es el dato del selector: {selector_veh_new}")
        
        # Busqueda del propietario (si este fue modificado)
        nombre_buscado = selector_veh_new
        
        # print(f"Nombre_buscado {nombre_buscado}")
        
        clave = dict_inverse.get(nombre_buscado)
        # print(clave)
        
        cliente_id = clave

        # print (f"Este es el valor del cliente_id {cliente_id}")
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vehiculos (cliente_id, marca, modelo, year, placa, fecha_entrada, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                cliente_id,
                marca,
                modelo,
                year,
                placa,
                fecha,
                observaciones,
            ),
        )
        conn.commit()

        # Recargar los datos después de guardar el nuevo usuario
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehiculos")
        rows = cursor.fetchall()
        # conn.close()

        st.session_state.index_veh = (
            len(rows) - 1
        )  # Establecer el índice al último usuario
        return [list(row) for row in rows]

    # Mostrar los datos del usuario actual
    if st.session_state.is_new_user_veh:
        current_user_veh = st.session_state.new_test_data_veh
    else:
        current_user_veh = test_data_veh[st.session_state.index_veh]

    with placeholder.container():
        # HEADER PAGINA
        with col2:
            with st.container(height=70, border=True):
                left_co, cent_co, last_co = st.columns(3)
                with left_co:
                    st.markdown(
                        f"""
                    <div style='display: flex; align-items: center; color: blue; font-size: 20px; font-weight: bold;'>
                        <img src="data:image/png;base64,{img_str}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; border: 2px solid black;">
                        Auto Diagnostico J.M.R.
                    </div>
                    """,
                                        unsafe_allow_html=True,
                                    )
                with last_co:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: flex-end;">
                            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                                <span style="color: blue; font-size: 16px; font-weight: bold;">Modulo: Vehiculos</span>
                                <span style="color: black; font-size: 14px; font-weight: bold;">Fecha: {fecha_formateada}</span>
                            </div>
                            <span style="margin-left: 10px;"></span>
                            <svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="blue" class="bi bi-car-front-fill" viewBox="0 0 16 16">
                                <path d="M2.52 3.515A2.5 2.5 0 0 1 4.82 2h6.362c1 0 1.904.596 2.298 1.515l.792 1.848c.075.175.21.319.38.404.5.25.855.715.965 1.262l.335 1.679q.05.242.049.49v.413c0 .814-.39 1.543-1 1.997V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.338c-1.292.048-2.745.088-4 .088s-2.708-.04-4-.088V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.892c-.61-.454-1-1.183-1-1.997v-.413a2.5 2.5 0 0 1 .049-.49l.335-1.68c.11-.546.465-1.012.964-1.261a.8.8 0 0 0 .381-.404l.792-1.848ZM3 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2m10 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2M6 8a1 1 0 0 0 0 2h4a1 1 0 1 0 0-2zM2.906 5.189a.51.51 0 0 0 .497.731c.91-.073 3.35-.17 4.597-.17s3.688.097 4.597.17a.51.51 0 0 0 .497-.731l-.956-1.913A.5.5 0 0 0 11.691 3H4.309a.5.5 0 0 0-.447.276L2.906 5.19Z"/>
                            </svg>
                        </div>
                        """,
                                            unsafe_allow_html=True,
                                        )


            # SECOND CONTAINER 2DO FRAME
            with st.container(height=550, border=True):
                tab1, tab2, tab3 = st.tabs(
                    [
                        "Nuevo Vehículo",
                        "Gestión de Vehículos",
                        "Reporte de Vehículos",
                    ]
                )
                # FICHA DE LOS REPORTES
                with tab3:
                    # CONTAINER: ENCABEZADO DE LA FICHA
                    with st.container(height=50, border=False):
                        cont_1_veh, cont_2_veh, cont_3_veh = st.columns([1, 2, 1])
                        with cont_1_veh:
                            st.markdown(
                                "<span style='font-size: 20px; color: blue; font-weight: bold;'>REPORTE VEHÍCULOS</span>",
                                unsafe_allow_html=True,
                            )
                            # streamlit_space.space(container=None, lines=1)
                        with cont_2_veh:
                            search_term_veh = st.text_input(
                                "Buscar",
                                label_visibility="collapsed",
                                placeholder="Buscar",
                                on_change=None,
                                key="search_box_veh",
                            )
                        with cont_3_veh:
                            if st.button("Limpiar"):
                                search_term_veh = ""
                    # CONTAINER BODY: REPORTE DE DATOS
                    with st.container(height=350, border=False):
                        df_report_veh = pd.DataFrame(
                            filas,
                            columns=[
                                "Vehiculos_id",
                                "Nombre",
                                "Apellido",
                                "Marca",
                                "Modelo",
                                "Año",
                                "Placa",
                                "Fecha_entrada",
                                "Observaciones",
                            ],
                        )
                        df_report_veh["Propietario"] = df_report_veh.apply(
                            lambda row: f"{row['Nombre']} {row['Apellido']}", axis=1
                        )
                        df_report_veh.drop(columns=["Nombre", "Apellido"], inplace=True)
                        # Mover la columna "Nombre / Razon Social" a la tercera posición
                        column_name = "Propietario"
                        column_index = (
                            1  # La tercera posición es el índice 2 (0-based index)
                        )

                        # Extraer la columna temporalmente
                        temp_col = df_report_veh.pop(column_name)
                        

                        # Insertar la columna en la posición deseada
                        df_report_veh.insert(column_index, column_name, temp_col)

                        # Restablecer el índice para que no se muestre
                        df_report_veh.reset_index(drop=True, inplace=True)
                        
                        # print(f"Contenido {df_report_veh}")
                        
                        if search_term_veh:
                            # Filtrar por si el término de búsqueda aparece en cualquier columna
                            df_report_veh = df_report_veh.set_index("Vehiculos_id")

                            df_filtered = df_report_veh[
                                df_report_veh.apply(
                                    lambda row: row.astype(str)
                                    .str.contains(search_term_veh, case=False)
                                    .any(),
                                    axis=1,
                                )
                            ]

                            # st.table(df_filtered)
                        else:
                            # df_report_veh = df_report_veh.drop(['id'],axis=0)
                            df_report_veh = df_report_veh.set_index("Vehiculos_id")
                            df_filtered = df_report_veh
                        st.table(df_filtered)
                        # Mostrar la tabla en Streamlit
                    # CONTAINER: COPYRIGHT
                    with st.container(height=50, border=False):
                        ult_1, ult_2, ult_3 = st.columns([1, 2, 1])
                        with ult_2:
                            st.write(
                                "© 2024 WhiteLabs Technologies - Todos los derechos reservados   "
                            )
                # FICHA DE VEHICULOS ACTUALES
                with tab2:
                    # CONTAINER: ENCABEZADO DE LA FICHA
                    with st.container(height=50, border=False):
                        (
                            column_izq,
                            column_center,
                            column_der,
                            column_uno,
                        ) = st.columns(
                            [
                                3,
                                4,
                                1,
                                1,
                            ]
                        )
                        with column_izq:
                            # streamlit_space.space(container=None, lines=0)
                            st.markdown(
                                f"<span style='color:blue;font-weight:bold;font-size:15px;'>VEHÍCULO ID N°: {current_user_veh[0]} / TOTAL REGISTROS: {len(test_data_veh)}</span>",
                                unsafe_allow_html=True,
                            )
                        with column_center:
                            st.markdown(
                                """
                                <div style="text-align: left;">
                                    <span style='font-size: 16px; color: blue; font-weight: bold;'>VEHÍCULOS ACTUALES</span>
                                </div>
                                """,
                                unsafe_allow_html=True,
)
                            if not st.session_state.is_new_user_veh:
                                with column_der:
                                    boton_3_veh = st.button(
                                        "Previo", on_click=prev_user, key="previo_veh"
                                    )
                                with column_uno:
                                    boton_2_veh = st.button(
                                        "Siguiente",
                                        on_click=next_user,
                                        key="siguiente_veh",
                                    )
                    # CONTAINER BODY: BODY

                    with st.container(height=350, border=True):

                        izquierda_veh, derecha_veh = st.columns(2)
                        with izquierda_veh:
                            numero = current_user_veh[0]

                            key = current_user_veh[1]
                            value = result_dict.get(key)
                            position_in_dict = temporal_veh.index(value)

                            selector1 = st.selectbox(
                                "Seleccione un propietario de la lista",
                                temporal_veh,
                                on_change=None,
                                index=position_in_dict,
                            )
                            # print(current_user_veh[1])
                            modelo_veh = st.text_input(
                                "Modelo:",
                                value=current_user_veh[3],
                                on_change=None,
                                key="modelo_veh",
                            )
                            placa_veh = st.text_input(
                                "Placa:",
                                value=current_user_veh[5],
                                on_change=None,
                                key="placa_veh",
                            )

                            observaciones_veh = st.text_input(
                                "Observaciones:",
                                value=current_user_veh[7],
                                key="notas_veh",
                                on_change=None,
                            )

                        with derecha_veh:
                            marca_veh = st.text_input(
                                "Marca",
                                value=current_user_veh[2],
                                on_change=None,
                                key="marca_veh",
                            )
                            year_veh = st.text_input(
                                "Año :",
                                value=current_user_veh[4],
                                on_change=None,
                                key="year_veh",
                            )
                            fecha_veh = st.date_input(
                                "Fecha Entrada:",
                                on_change=None,
                                key="fecha_veh",
                            )

                    with st.container(height=60, border=False):
                        linea_1_veh, linea_2_veh, linea_3_veh, linea_4_veh = st.columns(
                            [6, 1, 1, 1]
                        )
                        with linea_3_veh:
                            boton_1_veh = st.button(
                                "Modificar", key="modificar_vehiculo"
                            )
                        with linea_4_veh:
                            boton_elimi_clien_veh = st.button(
                                "Eliminar", key="eliminar_vehiculo"
                            )
                        identificador = current_user_veh[0]
                        if boton_1_veh:
                            toast()
                            st.session_state.is_saved = True
                            edit_user_veh(
                                marca_veh,
                                modelo_veh,
                                year_veh,
                                placa_veh,
                                fecha_veh,
                                observaciones_veh,
                                temporal_veh,
                                selector1,
                                identificador,
                            )
                        if boton_elimi_clien_veh:
                            toast()
                            delete_vehicle(identificador)
                            
                # FICHA NUEVOS VEHICULOS
                with tab1:
                    with st.container(height=50, border=False):
                        (
                            column_izq,
                            column_center,
                            column_der,
                            column_uno,
                            column_dos,
                            column_tres,
                        ) = st.columns([4, 3, 4, 3, 1.7, 1.7])
                        with column_izq:
                            # streamlit_space.space(container=None, lines=0)

                            new_register = len(test_data_veh) + 1
                            st.markdown(
                                f"<span style='font-size: 14px; color: blue; font-weight: bold;'>NUEVO VEHÍCULO SERÁ EL ID N° {new_register}</span>",
                                unsafe_allow_html=True,
                            )
                        with column_der:
                            st.markdown(
                                "<span style='font-size: 16px; color: blue; font-weight: bold;'>FORMATO NUEVOS VEHÍCULOS</span>",
                                unsafe_allow_html=True,
                            )
                    # MAIN CONTAINER - ESTAN LAS TABS AQUI
                    with st.container(height=350, border=True):
                        izquierda, derecha = st.columns(2)
                        with izquierda:
                            selector_veh_new = st.selectbox(
                                "Seleccion un cliente de la lista",
                                temporal_veh,
                                key="select_new_veh",
                            )
                            # print(selector_veh_new)
                            modelo_veh_new = st.text_input(
                                "Modelo:", on_change=None, key="modelo_veh_new"
                            )
                            placa_veh_new = st.text_input("Placa:", key="placa_veh_new")
                            observaciones_veh_new = st.text_input(
                                "Observaciones:",
                                key="notas_veh_new",
                                on_change=None,
                            )
                        with derecha:
                            marca_veh_new = st.text_input(
                                "Marca", on_change=None, key="marca_veh_new"
                            )
                            year_veh_new = st.number_input(
                                "Año :", value=1970, on_change=None, key="year_veh_new"
                            )
                            fecha_veh_new = st.date_input(
                                "Fecha Entrada:",
                                value="today",
                                on_change=None,
                                key="fecha_veh_new",
                            )
                    with st.container(height=60, border=False):
                        lin_1, lin_2, lin_3, lin_4 = st.columns([2, 1, 1, 1])
                        with lin_4:
                            boton_save_new_veh = st.button(
                                "Guardar Nuevo Vehiculo", key="guardar_nuevo_vehiculo"
                            )
                        # if not st.session_state.is_saved:
                            if boton_save_new_veh:
                                toast()

                                st.session_state.is_saved = True
                                save_new_vehicle(
                                    new_register,
                                    selector_veh_new,
                                    marca_veh_new,
                                    modelo_veh_new,
                                    year_veh_new,
                                    placa_veh_new,
                                    fecha_veh_new,
                                    observaciones_veh_new,
                                    temporal_veh,
                                )
                                st.rerun()


# Pagina repuestos
def repuestos():
    # Carga de datos a una lista desde la base de datos jhotem.db
    # Conectar a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()

    # Cargar los datos de la tabla 'clientes'
    cursor.execute("SELECT * FROM repuestos")
    rows = cursor.fetchall()

    test_data_rep = [list(row) for row in rows]
    new_test_data_rep = []

    # print(test_data_rep)
    if "index_rep" not in st.session_state:
        st.session_state.index_rep = 0

    if "new_test_data_rep" not in st.session_state:
        st.session_state.new_test_data_rep = []
    if "is_new_user_rep" not in st.session_state:
        st.session_state.is_new_user_rep = False
    if "is_saved_rep" not in st.session_state:  # ADDED
        st.session_state.is_saved_rep = False  # ADDED

    def toast():
        st.toast("Optimizando")
        time.sleep(0.5)
        st.toast("Haciendo los cambios en la Base de Datos")
        time.sleep(0.5)
        st.toast("Listo", icon="🎉")

    def repair():
        st.toast("No se puede guardar faltan cargar datos de la ficha", icon="⚠️")
        time.sleep(0.8)
        st.toast("Por favor revisa los datos a ingresar")
        time.sleep(0.8)

    # Funciones para cambiar el índice
    def next_rep():
        if st.session_state.index_rep < len(test_data_rep) - 1:
            st.session_state.index_rep += 1
        st.session_state.is_saved_rep = False  # ADDED

    def prev_rep():
        if st.session_state.index_rep > 0:
            st.session_state.index_rep -= 1
        st.session_state.is_saved_rep = False  # ADDED

    def delete_repuesto(identificador):
        Id_repuestos = int(identificador)

        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM repuestos
            WHERE Id_repuestos = ?
            """,
            (Id_repuestos,),
        )

        conn.commit()
        # conn.close()

    def edit_user_rep(
        descripcion_rep,
        costo_rep,
        proveedor_rep,
        Margen_rep,
        precio_de_venta_rep,
        identificador,
    ):
        descripcion = descripcion_rep
        costo = costo_rep
        proveedor = proveedor_rep
        margen = Margen_rep
        precio_de_venta = precio_de_venta_rep
        Id_repuestos = int(identificador)

        # new_test_data = st.session_state.new_test_data
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()

        # Consulta SQL corregida
        cursor.execute(
            """
            UPDATE repuestos
            SET Descripcion = ?, Costo = ?, Proveedor = ?, Precio_de_Venta = ?, Margen = ?
            WHERE Id_repuestos = ?
        """,
            (
                descripcion,
                costo,
                proveedor,
                precio_de_venta,
                margen,
                Id_repuestos,
            ),
        )

        conn.commit()
        # conn.close()

    def save_new_repuesto(
        descripcion_rep_new,
        costo_rep_new,
        proveedor_rep_new,
        Margen_rep_new,
        precio_de_venta_new_rep,
    ):
        descripcion = descripcion_rep_new
        costo = costo_rep_new
        proveedor = proveedor_rep_new
        margen = Margen_rep_new
        precio_de_venta = precio_de_venta_new_rep

        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO repuestos (Descripcion, Costo, Proveedor, Margen, Precio_de_Venta) VALUES (?, ?, ?, ?, ?)",
            (
                descripcion,
                costo,
                proveedor,
                margen,
                precio_de_venta,
            ),
        )
        conn.commit()

        # Recargar los datos después de guardar el nuevo usuario
        conn = sqlite3.connect("jhotem.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repuestos")
        rows = cursor.fetchall()
        # conn.close()

        st.session_state.index_rep = (
            len(rows) - 1
        )  # Establecer el índice al último usuario
        return [list(row) for row in rows]

    # Mostrar los datos del usuario actual
    if st.session_state.is_new_user_rep:
        current_user = st.session_state.new_test_data_rep
    else:
        current_user = test_data_rep[st.session_state.index_rep]

    with placeholder.container():
        with col2:
            with st.container(height=70, border=True):
                left_co, cent_co, last_co = st.columns(3)
                with left_co:
                    st.markdown(
                        f"""
    <div style='display: flex; align-items: center; color: blue; font-size: 20px; font-weight: bold;'>
        <img src="data:image/png;base64,{img_str}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; border: 2px solid black;">
        Auto Diagnostico J.M.R.
    </div>
    """,
                        unsafe_allow_html=True,
                    )
                with last_co:
                    st.markdown(
                        f"""
    <div style="display: flex; align-items: center; justify-content: flex-end;">
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
            <span style="color: blue; font-size: 16px; font-weight: bold;">Modulo: Repuestos</span>
            <span style="color: black; font-size: 14px; font-weight: bold;">Fecha: {fecha_formateada}</span>
        </div>
        <span style="margin-left: 10px;"></span>
        <svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="blue" class="bi bi-wrench-adjustable" viewBox="0 0 16 16">
            <path d="M16 4.5a4.5 4.5 0 0 1-1.703 3.526L13 5l2.959-1.11q.04.3.041.61"/>
            <path d="M11.5 9c.653 0 1.273-.139 1.833-.39L12 5.5 11 3l3.826-1.53A4.5 4.5 0 0 0 7.29 6.092l-6.116 5.096a2.583 2.583 0 1 0 3.638 3.638L9.908 8.71A4.5 4.5 0 0 0 11.5 9m-1.292-4.361-.596.893.809-.27a.25.25 0 0 1 .287.377l-.596.893.809-.27.158.475-1.5.5a.25.25 0 0 1-.287-.376l.596-.893-.809.27a.25.25 0 0 1-.287-.377l.596-.893-.809.27-.158-.475 1.5-.5a.25.25 0 0 1 .287.376M3 14a1 1 0 1 1 0-2 1 1 0 0 1 0 2"/>
        </svg>
    </div>
    """,
                        unsafe_allow_html=True,
                    )
            with st.container(height=550, border=True):
                tab1, tab2, tab3 = st.tabs(
                    [
                        "Nuevo Repuesto",
                        "Gestión de Repuestos",
                        "Reporte de Repuestos",
                    ]
                )
                # FICHA DE LOS REPORTES
                with tab3:
                    # CONTAINER: ENCABEZADO DE LA FICHA
                    with st.container(height=50, border=False):
                        cont_1_veh, cont_2_veh, cont_3_veh = st.columns([1, 2, 1])
                        with cont_1_veh:
                            st.markdown(
                                "<span style='font-size: 20px; color: blue; font-weight: bold;'>REPORTE REPUESTO</span>",
                                unsafe_allow_html=True,
                            )
                            # streamlit_space.space(container=None, lines=1)
                        with cont_2_veh:
                            search_term_rep = st.text_input(
                                "Buscar",
                                label_visibility="collapsed",
                                placeholder="Buscar",
                                on_change=None,
                                key="search_box_rep",
                            )
                        with cont_3_veh:
                            if st.button("Limpiar", key="clean_report_rep"):
                                search_term_rep = ""
                    # CONTAINER BODY: REPORTE DE DATOS
                    with st.container(height=350, border=False):
                        # st.write(test_data_rep)
                        df_report_rep = pd.DataFrame(
                            test_data_rep,
                            columns=[
                                "Id_repuestos",
                                "Descripcion",
                                "Costo",
                                "Proveedor",
                                "Precio_de_Venta",
                                "Margen",
                            ],
                        )
                        # Reorganizar las columnas
                        column_order = [
                            "Id_repuestos",
                            "Descripcion",
                            "Proveedor",
                            "Costo",
                            "Margen",
                            "Precio_de_Venta",
                        ]
                        df_report_rep = df_report_rep.reindex(columns=column_order)
                        if search_term_rep:
                            # Filtrar por si el término de búsqueda aparece en cualquier columna
                            df_filtered_rep = df_report_rep[
                                df_report_rep.apply(
                                    lambda row: row.astype(str)
                                    .str.contains(search_term_rep, case=False)
                                    .any(),
                                    axis=1,
                                )
                            ]
                        else:
                            df_filtered_rep = df_report_rep

                        # Dividir la columna "Margen" entre 100
                        df_filtered_rep["Margen"] = df_filtered_rep["Margen"] / 100

                        # Aplicar formato
                        df_filtered_rep = df_filtered_rep.style.format(
                            {
                                "Costo": "${:,.2f}",
                                "Precio_de_Venta": "${:,.2f}",
                                "Margen": "{:.2%}",
                            }
                        )
                        st.table(df_filtered_rep)

                    # FICHA DE REPUESTOS ACTUALES
                with tab2:
                    # CONTAINER: ENCABEZADO DE LA FICHA
                    with st.container(height=50, border=False):
                        (
                            column_izq,
                            column_center,
                            column_der,
                            column_uno,
                        ) = st.columns(
                            [
                                2,
                                4,
                                1,
                                1,
                            ]
                        )
                        with column_izq:
                            # streamlit_space.space(container=None, lines=0)

                            st.markdown(
                                f"<span style='font-size: 14px; color: blue; font-weight: bold;'>REPUESTO ID N° {current_user[0]} / TOTAL REGISTROS: {len(test_data_rep)}</span>",
                                unsafe_allow_html=True,
                            )
                        with column_center:
                            st.markdown(
                                """
                                <div style="text-align: center;">
                                    <span style='font-size: 16px; color: blue; font-weight: bold;'>REPUESTOS ACTUALES</span>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if not st.session_state.is_new_user_rep:
                                with column_der:
                                    boton_1_rep = st.button(
                                        "Previo", key="previo_rep", on_click=prev_rep
                                    )
                                with column_uno:
                                    boton_2_rep = st.button(
                                        "Siguiente",
                                        key="siguiente_rep",
                                        on_click=next_rep,
                                    )
                    # # CONTAINER BODY: BODY
                    with st.container(height=350, border=True):
                        izquierda_rep, derecha_rep = st.columns(2)
                        with izquierda_rep:
                            descripcion = st.text_input(
                                "Descripcion de la Pieza / Repuesto :",
                                on_change=None,
                                value=current_user[1],
                                key=f"descripcion_{current_user[0]}",
                            )
                            proveedor = st.text_input(
                                "Proveedor :",
                                on_change=None,
                                value=current_user[3],
                                key=f"proveedor_{current_user[0]}",
                            )

                        with derecha_rep:
                            costo = st.number_input(
                                "Costo en USD :",
                                value=current_user[2],
                                on_change=None,
                                key=f"costo_rep_{current_user[0]}",
                            )
                            Margen = st.number_input(
                                "Ganacia en (%) :",
                                value=current_user[5],
                                on_change=None,
                                key=f"margen_rep_{current_user[0]}",
                            )
                            if (
                                costo is not None
                                and costo != ""
                                and Margen is not None
                                and Margen != 0
                            ):
                                costo = float(costo)
                                Margen = float(Margen)
                                margen_porcen_rep = Margen / 100
                                factor = 1 + margen_porcen_rep
                                precio_de_venta_rep = costo * factor
                                container = st.container()
                                precio_formateado = "${:,.2f}".format(
                                    precio_de_venta_rep
                                )
                            container = st.container()
                            precio_formateado = "${:,.2f}".format(precio_de_venta_rep)
                            container.markdown(
                                f"""
    <div style='width:530px; height:140px; background-color:#f0f0f0; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:10px;'>
        <span style='color:black; font-weight:bold; font-size:28px; text-align:center;line-height:1;'>Precio de Venta:</span>
        <span style='color:blue; font-weight:bold; font-size:70px; text-align:center;line-height:1;'>US{precio_formateado}</span>
    </div>
    """,
                                unsafe_allow_html=True,
                            )
                    with st.container(height=60, border=False):
                        linea_1_veh, linea_2_veh, linea_3_veh, linea_4_veh = st.columns(
                            [6, 1, 1, 1]
                        )
                        with linea_3_veh:
                            boton_mod_repuesto = st.button(
                                "Modificar", key="modificar_repuesto"
                            )
                        with linea_4_veh:
                            boton_elimi_repuesto = st.button(
                                "Eliminar", key="eliminar_repuesto"
                            )
                        identificador = current_user[0]
                        if boton_mod_repuesto:
                            toast()
                            st.session_state.is_saved = True
                            with st.container():
                                edit_user_rep(
                                    descripcion,
                                    costo,
                                    proveedor,
                                    Margen,
                                    precio_de_venta_rep,
                                    identificador,
                                )
                        if boton_elimi_repuesto:
                            toast()
                            delete_repuesto(identificador)
                # FICHA NUEVOS REPUESTOS
                with tab1:
                    with st.container(height=50, border=False):
                        (
                            column_izq,
                            column_center,
                            column_uno,
                            column_tres,
                        ) = st.columns([3, 0.5, 3, 1])
                        with column_izq:
                            # streamlit_space.space(container=None, lines=0)

                            new_register = len(test_data_rep) + 1
                            st.markdown(
                                f"<span style='font-size: 14px; color: blue; font-weight: bold;'>NUEVO REPUESTO SERÁ EL ID N° {new_register}</span>",
                                unsafe_allow_html=True,
                            )
                        with column_uno:
                            st.markdown(
                                """
                                <div style="text-align: left;">
                                    <span style='font-size: 16px; color: blue; font-weight: bold;'>FORMATO NUEVO RESPUESTO</span>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    # MAIN CONTAINER - ESTAN LAS TABS AQUI
                    with st.container(height=350, border=True):
                        izquierda, derecha = st.columns(2)
                        with izquierda:
                            descripcion_rep_new = st.text_input(
                                "Decripcion de la Pieza / Repuesto :",
                                on_change=None,
                                key="descrip_new_rep",
                            )
                            proveedor_rep_new = st.text_input(
                                "Proveedor :",
                                on_change=None,
                                key="proveedor_new_rep",
                            )
                        with derecha:
                            costo_rep_new = st.number_input(
                                "Costo en USD :",
                                min_value=0,
                                max_value=10000,
                                step=1,
                                key="costo_new_rep",
                            )
                            Margen_rep_new = st.number_input(
                                "Ganancia en (%) :",
                                step=1,
                                key="margen_new_rep",
                            )

                            if (
                                costo_rep_new is not None
                                or costo_rep_new != 0
                                or Margen_rep_new is not None
                                or Margen_rep_new != 0
                            ):
                                costo_rep_new = float(costo_rep_new)
                                Margen_rep_new = float(Margen_rep_new)
                                margen_porcen_new_rep = Margen_rep_new / 100
                                factor = 1 + margen_porcen_new_rep
                                precio_de_venta_new_rep = costo_rep_new * factor
                                container = st.container()
                                precio_formateado = "${:,.2f}".format(
                                    precio_de_venta_new_rep
                                )
                                container.markdown(
                                    f"""
                                <div style='width:530px; height:140px; background-color:#f0f0f0; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:10px;'>
                                    <span style='color:black; font-weight:bold; font-size:28px; text-align:center;line-height:1;'>Precio de Venta:</span>
                                    <span style='color:blue; font-weight:bold; font-size:70px; text-align:center;line-height:1;'>US{precio_formateado}</span>
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )
                            else:
                                container = st.container()
                                valor = 0
                                precio_formateado = "${:,.2f}".format(valor)
                                container.markdown(
                                    f"""
                                <div style='width:530px; height:140px; background-color:#f0f0f0; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:10px;'>
                                    <span style='color:black; font-weight:bold; font-size:28px; text-align:center;line-height:1;'>Precio de Venta:</span>
                                    <span style='color:blue; font-weight:bold; font-size:70px; text-align:center;line-height:1;'>US{precio_formateado}</span>
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )
                    with st.container(height=60, border=False):
                        lin_1, lin_2, lin_3, lin_4 = st.columns([2, 1, 1, 1])
                        with lin_4:
                            if st.button(
                                "Guardar Nuevo Repuesto", key="guardar_nuevo_repuesto"
                            ):
                                # Validar que los datos estan completos
                                if (
                                    descripcion_rep_new != ""
                                    and proveedor_rep_new != ""
                                    and costo_rep_new != ""
                                    and Margen_rep_new != ""
                                ):
                                    # Guardar en la base de datos

                                    st.session_state.is_saved = True
                                    toast()
                                    save_new_repuesto(
                                        descripcion_rep_new,
                                        costo_rep_new,
                                        proveedor_rep_new,
                                        Margen_rep_new,
                                        precio_de_venta_new_rep,
                                    )
                                    st.rerun()
                                else:
                                    repair()


if __name__ == "__main__":
    # Diccionario de páginas
    pages = {
        "log_in": login_page,
        "Novedades": novedades,
        "Presupuestos": presupuestos,
        "Ajustes": ajustes,
        "Clientes": home,
        "Vehiculos": vehiculos,
        "Repuestos": repuestos,
        "Log-out": logout,
    }

    # Gestor de paginas con session state
    page = st.session_state.page
    pages[page]()

# Cierre de la version inicial 31-08-2024