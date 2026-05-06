import sqlite3
import uuid

DATABASE_NAME = "database.db"

def conectar():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- EN db_manager.py ---

def inicializar_db():
    # Mantenemos los nombres pre-existentes y añadimos los nuevos
    sql = '''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE, 
        password TEXT NOT NULL,
        token TEXT,
        nombre_completo TEXT,
        descripcion TEXT,
        experiencia TEXT,
        educacion TEXT,
        genero TEXT,
        fecha_nacimiento TEXT
    )
    '''
    conn = conectar()
    conn.execute(sql)
    conn.commit()
    conn.close()


def actualizar_perfil(usuario_id, datos):
    """
    'datos' es un diccionario con las llaves: 
    nombre_completo, descripcion, experiencia, educacion, genero, fecha_nacimiento
    """
    try:
        conn = conectar()
        conn.execute('''
            UPDATE usuarios SET 
                nombre_completo = ?, 
                descripcion = ?, 
                experiencia = ?, 
                educacion = ?, 
                genero = ?, 
                fecha_nacimiento = ?
            WHERE id = ?
        ''', (
            datos['nombre_completo'], 
            datos['descripcion'], 
            datos['experiencia'], 
            datos['educacion'], 
            datos['genero'], 
            datos['fecha_nacimiento'], 
            usuario_id
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return False


# ACTUALIZADO: Acepta 'email'
def registrar_usuario(nombre, email, password):
    try:
        conn = conectar()
        # ACTUALIZADO: Incluimos email en el INSERT
        conn.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)", 
            (nombre, email, password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Esto ocurre si el nombre O el email ya existen
        conn.close()
        return False


def verificar_usuario(nombre, password):
    conn = conectar()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE nombre = ? AND password = ?", 
        (nombre, password)
    ).fetchone()
    conn.close()
    return usuario

# --- NUEVAS FUNCIONES PARA EL GAFETE ---

def asignar_nuevo_token(usuario_id):
    """Genera una llave aleatoria, la guarda en la BD y la devuelve"""
    nuevo_token = str(uuid.uuid4()) # Crea algo como 'a1b2c3d4...'
    conn = conectar()
    conn.execute("UPDATE usuarios SET token = ? WHERE id = ?", (nuevo_token, usuario_id))
    conn.commit()
    conn.close()
    return nuevo_token

def obtener_usuario_por_token(token):
    """Busca si existe un usuario con esa llave específica"""
    if not token: return None
    conn = conectar()
    usuario = conn.execute("SELECT * FROM usuarios WHERE token = ?", (token,)).fetchone()
    conn.close()
    return usuario

def borrar_token(token):
    """Elimina la llave de la BD (Cerrar sesión)"""
    conn = conectar()
    conn.execute("UPDATE usuarios SET token = NULL WHERE token = ?", (token,))
    conn.commit()
    conn.close()