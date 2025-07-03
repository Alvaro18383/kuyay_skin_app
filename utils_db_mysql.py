
import mysql.connector
from datetime import datetime


# ✅ Conexión a MySQL
def conectar():
    return mysql.connector.connect(
        host="127.0.0.1",          # o puedes poner "localhost"
        port=3306,                 # siempre ponlo si es MySQL por este puerto
        user="root",               # tu usuario MySQL
        password="123456",  # tu contraseña MySQL
        database="kuyay_skin"      # nombre de tu base de datos
    )


def registrar_usuario(email, nombre, password, tipo):
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        INSERT INTO usuario (email, nombre, password, tipo)
        VALUES (%s, %s, %s, %s)
    """, (email, nombre, password, tipo))

    conn.commit()
    conn.close()


def verificar_usuario_existente(email, password=None):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM usuario WHERE email = %s", (email,))
    datos = c.fetchone()
    conn.close()

    if datos is None:
        return False  # No existe el usuario

    if password is not None:
        if datos[2] == password:  # datos[2] es la contraseña
            return datos  # Retorna todos los datos del usuario si coincide
        else:
            return False  # Contraseña incorrecta
    else:
        return datos  # Si solo quiere verificar existencia (sin validar password)




# ✅ Crear las tablas
def crear_db():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            email VARCHAR(255) PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            tipo VARCHAR(20) NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS diagnostico (
            email VARCHAR(255) PRIMARY KEY,
            tipo_piel VARCHAR(50),
            descripcion TEXT,
            causas TEXT,
            advertencias TEXT,
            faq TEXT,
            fecha DATETIME,
            FOREIGN KEY (email) REFERENCES usuario(email)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS cuestionario (
            email VARCHAR(255) PRIMARY KEY,
            edad INT,
            genero VARCHAR(50),
            tipo_piel VARCHAR(50),
            sensibilidad VARCHAR(10),
            acne VARCHAR(10),
            manchas VARCHAR(10),
            exposicion VARCHAR(10),
            hidratacion VARCHAR(10),
            protector VARCHAR(10),
            fecha DATETIME,
            FOREIGN KEY (email) REFERENCES usuario(email)
        )
    """)

    conn.commit()
    conn.close()


def guardar_diagnostico(email, tipo_piel, descripcion, causas, advertencias, faq):
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        INSERT INTO diagnostico (email, tipo_piel, descripcion, causas, advertencias, faq, fecha)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            tipo_piel = VALUES(tipo_piel),
            descripcion = VALUES(descripcion),
            causas = VALUES(causas),
            advertencias = VALUES(advertencias),
            faq = VALUES(faq),
            fecha = VALUES(fecha)
    """, (email, tipo_piel, descripcion, causas, advertencias, faq, datetime.now()))

    conn.commit()
    conn.close()


def guardar_cuestionario(email, edad, genero, tipo_piel, sensibilidad, acne, manchas, exposicion, hidratacion, protector):
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        INSERT INTO cuestionario (email, edad, genero, tipo_piel, sensibilidad, acne, manchas, exposicion, hidratacion, protector, fecha)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            edad = VALUES(edad),
            genero = VALUES(genero),
            tipo_piel = VALUES(tipo_piel),
            sensibilidad = VALUES(sensibilidad),
            acne = VALUES(acne),
            manchas = VALUES(manchas),
            exposicion = VALUES(exposicion),
            hidratacion = VALUES(hidratacion),
            protector = VALUES(protector),
            fecha = VALUES(fecha)
    """, (email, edad, genero, tipo_piel, sensibilidad, acne, manchas, exposicion, hidratacion, protector, datetime.now()))

    conn.commit()
    conn.close()


def cargar_diagnostico(email):
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT * FROM diagnostico WHERE email = %s', (email,))
    datos = c.fetchone()
    conn.close()
    return datos


def cargar_cuestionario(email):
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT * FROM cuestionario WHERE email = %s', (email,))
    datos = c.fetchone()
    conn.close()
    return datos


def guardar_historial_visual(email, imagen):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO historial_visual (email, imagen, fecha)
        VALUES (%s, %s, %s)
    """, (email, imagen, datetime.now()))
    conn.commit()
    conn.close()


def cargar_historial_visual(email):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT id, imagen, fecha FROM historial_visual
        WHERE email = %s ORDER BY fecha DESC
    """, (email,))
    datos = c.fetchall()
    conn.close()
    return datos


def eliminar_historial_visual(id_foto):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM historial_visual WHERE id = %s", (id_foto,))
    conn.commit()
    conn.close()


def guardar_foro(email, nombre_usuario, categoria, texto, imagen):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO foro (email, nombre_usuario, categoria, texto, imagen, fecha)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (email, nombre_usuario, categoria, texto, imagen, datetime.now()))
    conn.commit()
    conn.close()


def cargar_foro():
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT id, nombre_usuario, categoria, texto, imagen, fecha FROM foro
        ORDER BY fecha DESC
    """)
    datos = c.fetchall()
    conn.close()
    return datos


def eliminar_foro(id_post):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM foro WHERE id = %s", (id_post,))
    conn.commit()
    conn.close()

# Guardar historial del estado
def guardar_historial_estado(email, tipo_piel, hidratacion, sensibilidad, protector):
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        INSERT INTO historial_estado (email, fecha, tipo_piel, hidratacion, sensibilidad, protector)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (email, datetime.now(), tipo_piel, hidratacion, sensibilidad, protector))

    conn.commit()
    conn.close()


# Cargar historial del estado
def cargar_historial_estado(email):
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        SELECT fecha, tipo_piel, hidratacion, sensibilidad, protector
        FROM historial_estado
        WHERE email = %s
        ORDER BY fecha ASC
    """, (email,))

    datos = c.fetchall()
    conn.close()
    return datos

# ✅ Cargar último historial
def cargar_ultimo_historial(email):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM historial_estado
        WHERE email = %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (email,))
    datos = c.fetchone()
    conn.close()
    return datos

