import sqlite3
from datetime import datetime
import pandas as pd

# Datos de prueba
# test_data = [
#     [
#         1,
#         "John",
#         "Doe",
#         "V.-12.455.655",
#         "+58-412-3183550",
#         "Av. Principal de Prados del Este",
#         "foo@foo.com",
#         "Esto es una prueba",
#         "2024-01-15",
#     ],
#     [
#         2,
#         "Maria",
#         "Rodriguez",
#         "V-13.333.333",
#         "58-414-345-5433",
#         "Av. Principal de Mariperez",
#         "hello@hello.com",
#         "Esto es otra prueba",
#         "2024-02-01",
#     ],
#     [
#         3,
#         "Fernando",
#         "De Sousa",
#         "V-82.331.331",
#         "58-412-660-259",
#         "Av. Principal de Mariperez",
#         "fernandodesousa@hello.com",
#         "Probando esto",
#         "2024-04-16",
#     ],
# ]


# # # Crear la conexión a la base de datos
# conn = sqlite3.connect("jhotem.db")
# cursor = conn.cursor()

# # ##### TABLA CLIENTES #########
# # # Crear la tabla 'clientes'
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS clientes (
#     id INTEGER PRIMARY KEY,
#     nombre TEXT,
#     apellido TEXT,
#     cedula TEXT,
#     telefono TEXT,
#     direccion TEXT,
#     correo_electronico TEXT,
#     nota TEXT,
#     fecha TEXT
# )
# """)

# # Insertar los datos en la tabla
# for cliente in test_data:
#     cursor.execute("""
#     INSERT INTO clientes (id, nombre, apellido, cedula, telefono, direccion, correo_electronico, nota, fecha)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, cliente)

# # Confirmar los cambios y cerrar la conexión
# conn.commit()
# conn.close()

# ###### TABLA VEHICULOS  ######
# # Crear la tabla 'vehiculos'
# cursor.execute(
#     """
# CREATE TABLE IF NOT EXISTS vehiculos (
#     vehiculos_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     cliente_id INTEGER NOT NULL,
#     marca TEXT NOT NULL,
#     modelo TEXT NOT NULL,
#     year INTEGER NOT NULL,
#     placa TEXT NOT NULL,
#     fecha_entrada DATE NOT NULL,
#     FOREIGN KEY (cliente_id) REFERENCES clientes(id)
# )
# """
# )
# conn.commit()
# conn.close()
# print("tabla creada satisfactoriamente")

# # Insertar los datos en la tabla vehiculos

# cursor.execute(
#     """
# INSERT INTO vehiculos (cliente_id, marca, modelo, year, placa, fecha_entrada)
# VALUES (8,'Tesla','Cybertuck','2024','ZJH-789','2024-06-2')"""
# )

# # Confirmar los cambios y cerrar la conexión
# conn.commit()
# conn.close()

# # Ejemplo de cómo agregar una nueva columna llamada 'observaciones' a la tabla 'vehiculos'
# cursor.execute(
#     """
# ALTER TABLE vehiculos
# ADD COLUMN observaciones TEXT
# """
# )


# cursor.execute(
#     """
# UPDATE vehiculos
# SET observaciones = 'vehiculo presento dos abolladuras y se le hizo saber al propietario'
# WHERE vehiculos_id = 3
# """
# )

# # Creacion de la tabla 
# cursor.execute(
#     """
# CREATE TABLE repuestos (
#     Id_repuestos INTEGER PRIMARY KEY AUTOINCREMENT,
#     Descripcion TEXT NOT NULL,
#     Costo REAL NOT NULL,
#     Proveedor TEXT NOT NULL,
#     Precio_de_Venta REAL NOT NULL,
#     Margen REAL NOT NULL
# )
# """
# )

# # # Guardar los cambios
# conn.commit()

# # # Cerrar la conexión
# conn.close()


# # Conectar a la base de datos (o crearla si no existe)
# conn = sqlite3.connect('jhotem.db')
# cursor = conn.cursor()

# # Función para insertar un nuevo repuesto y calcular el Precio_de_Venta
# def insertar_repuesto(descripcion, costo, proveedor, margen):
#     precio_de_venta = costo * (1 + margen / 100)
#     cursor.execute("""
#     INSERT INTO repuestos (Descripcion, Costo, Proveedor, Precio_de_Venta, Margen)
#     VALUES (?, ?, ?, ?, ?)
#     """, (descripcion, costo, proveedor, precio_de_venta, margen))
#     conn.commit()



#FIXME:  Query de consulta en simultaneo para las tablas vehiculos y clientes
def consulta():
    # Conectar a la base de datos
    conn = sqlite3.connect("jhotem.db")
    cursor = conn.cursor()

    # Definir la consulta SQL en Vehiculos
    query = """
    SELECT 
        v.vehiculos_id, 
        c.id AS cliente_id,
        c.nombre, 
        c.apellido, 
        c.telefono, 
        c.correo_electronico,
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

    # # Ejecutar la consulta y cargar los resultados en un DataFrame
    # df = pd.read_sql_query(query, conn)
    # # Ajustar las opciones de visualización
    # pd.set_option('display.max_rows', None)  # Mostrar todas las filas
    # pd.set_option('display.max_columns', None)  # Mostrar todas las columnas
    # pd.set_option('display.width', None)  # Ajustar el ancho de la salida
    # pd.set_option('display.max_colwidth', None)  # Ajustar el ancho de las columnas

    # # Mostrar el DataFrame
    # print(df)

    # Cerrar la conexión
    # conn.close()
    
    
    
# Ejemplo de uso
# insertar_repuesto('4 Bujias NGK', 40, 'Proveedor A', 50)

# Cerrar la conexión
# conn.close()


# Conectar a la base de datos
conn = sqlite3.connect('jhotem.db')
cursor = conn.cursor()

# Crear tabla Presupuesto
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS Presupuesto (
#     IdPresupuesto TEXT PRIMARY KEY,
#     vehiculo_id INTEGER,
#     Cliente_id INTEGER,
#     NombreCliente TEXT,
#     Telefono TEXT,
#     email TEXT,
#     DatosVehiculos TEXT,
#     Fecha DATE,  -- Cambiado a tipo DATE
#     TotalCosto REAL,
#     TotalVenta REAL,
#     Ganancia REAL,
#     Observaciones TEXT,
#     Estatus TEXT,
#     FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(vehiculos_id),
#     FOREIGN KEY (Cliente_id) REFERENCES clientes(id)
# )
# ''')

# Crear tabla DetallePresupuesto
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS DetallePresupuesto (
#     IdDetalle INTEGER PRIMARY KEY AUTOINCREMENT,
#     IdPresupuesto TEXT,
#     Descripcion TEXT,
#     Costo REAL,
#     PrecioVenta REAL,
#     FOREIGN KEY (IdPresupuesto) REFERENCES Presupuesto(IdPresupuesto)
# )
# ''')

# Paso 2: Eliminar la tabla original
# cursor.execute('DROP TABLE usuarios')

# Crear la tabla si no existe
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS usuarios (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     usuario TEXT NOT NULL,
#     clave TEXT NOT NULL
# )
# ''')

# Agregar la columna 'estatus'
# cursor.execute('ALTER TABLE usuarios ADD COLUMN estatus TEXT')

# # Actualizar los registros existentes
# cursor.execute("UPDATE usuarios SET estatus = 'activo' WHERE id < 5")

# print("Tabla estatus creada satisfactoriamente ")
# Guardar los cambios y cerrar la conexión
# conn.commit()
# conn.close()

#---


# ---

# Función para generar el siguiente IdPresupuesto
def generar_id_presupuesto():
    cursor.execute("SELECT MAX(IdPresupuesto) FROM Presupuesto")
    last_id = cursor.fetchone()[0]
    if last_id is None:
        return 'P-0001'
    else:
        last_number = int(last_id.split('-')[1])
        new_number = last_number + 1
        return f'P-{new_number:04d}'

# Ejemplo de inserción de un nuevo presupuesto y detalles
# nuevo_id_presupuesto = generar_id_presupuesto()
# cursor.execute('''
# INSERT INTO Presupuesto (IdPresupuesto, vehiculo_id, Cliente_id, NombreCliente, Telefono, email, DatosVehiculos, Fecha, TotalCosto, TotalVenta, Ganancia, Observaciones, Estatus)
# VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# ''', (nuevo_id_presupuesto, 1, 1, 'Jhonattan Blanco', '0212-5765646', 'foo@foo.com', 'Suzuki Sidekick 2023', '2023-07-30', 1500.0, 3000.0, 200.0, 'Pertenece al hermano del dueño', 'Enviado'))

# # Insertar detalles del presupuesto
# detalles = [
#     (nuevo_id_presupuesto, 'Cambio de condensador AC', 750.0, 1000.0),
#     (nuevo_id_presupuesto, 'Reparacion sistema electrico en General (incluye computadora) 2', 750.0, 2000.0)
# ]
# cursor.executemany('''
# INSERT INTO DetallePresupuesto (IdPresupuesto, Descripcion, Costo, PrecioVenta)
# VALUES (?, ?, ?, ?)
# ''', detalles)

# Guardar los cambios y cerrar la conexión

# Función para insertar un usuario si hay menos de 3 registros
def insertar_usuario(usuario, clave):
    # Conectar a la base de datos
    conn = sqlite3.connect('jhotem.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    count = cursor.fetchone()[0]
    if count < 3:
        cursor.execute('INSERT INTO usuarios (usuario, clave) VALUES (?, ?)', (usuario, clave))
        conn.commit()
        print("Usuario insertado correctamente.")
    else:
        print("No se pueden insertar más de 3 usuarios.")

def master_user(usuario, clave):
    # Conectar a la base de datos
    conn = sqlite3.connect('jhotem.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    cursor.execute('INSERT INTO usuarios (usuario, clave) VALUES (?, ?)', (usuario, clave))
    conn.commit()
    print("Usuario Master insertado correctamente.")

# # Ejemplo de uso
# insertar_usuario('usuario1', 'prueba123')
# insertar_usuario('usuario2', 'prueba123')
# insertar_usuario('usuario3', 'prueba123')
# master_user('tigerjose', 'Mathi1310#')
# Paso 5: Eliminar la tabla temporal (opcional)

# Paso 1: Crear una tabla temporal
# cursor.execute('CREATE TABLE temp_usuarios AS SELECT * FROM usuarios')


# Paso 2: Eliminar la tabla original
# cursor.execute('DROP TABLE usuarios')

cursor.execute('''
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    clave TEXT NOT NULL,
    estatus TEXT
)
''')

# Paso 4: Insertar los datos de la tabla temporal a la nueva tabla
# cursor.execute('INSERT INTO usuarios (usuario, contraseña, estatus) SELECT usuario, contraseña, \'activo\' AS estatus FROM temp_usuarios')

# # Paso 5: Eliminar la tabla temporal (opcional)
# cursor.execute('DROP TABLE temp_usuarios')

conn.commit()
conn.close()
