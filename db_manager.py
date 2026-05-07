import sqlite3
import uuid

DATABASE_NAME = "database.db"

def conectar():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = conectar()
    
    # 1. Tabla de Usuarios (Limpiamos las columnas de texto plano 'experiencia' y 'educacion')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE, 
        password TEXT NOT NULL,
        token TEXT,
        nombre_completo TEXT,
        descripcion TEXT,
        genero TEXT,
        fecha_nacimiento TEXT
    )
    ''')

    # 2. Nueva Tabla: Experiencia Laboral
    # Relacionada con el usuario mediante usuario_id (Llave foránea)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS experiencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        compania TEXT NOT NULL,
        puesto TEXT NOT NULL,
        ano TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')

    # 3. Nueva Tabla: Educación
    conn.execute('''
    CREATE TABLE IF NOT EXISTS educacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        institucion TEXT NOT NULL,
        nivel TEXT NOT NULL,
        ano TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')

    conn.commit()
    conn.close()

# --- FUNCIONES DE GESTIÓN DE PERFIL ---

def actualizar_perfil(usuario_id, datos):
    try:
        conn = conectar()
        conn.execute('''
            UPDATE usuarios SET 
                nombre_completo = ?, 
                descripcion = ?, 
                genero = ?, 
                fecha_nacimiento = ?
            WHERE id = ?
        ''', (
            datos['nombre_completo'], 
            datos['descripcion'], 
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

# --- NUEVAS FUNCIONES PARA LISTAS DINÁMICAS ---

def agregar_experiencia(usuario_id, compania, puesto, ano):
    conn = conectar()
    conn.execute("INSERT INTO experiencia (usuario_id, compania, puesto, ano) VALUES (?, ?, ?, ?)",
                 (usuario_id, compania, puesto, ano))
    conn.commit()
    conn.close()

def obtener_experiencia(usuario_id):
    conn = conectar()
    # Ordenamos por año descendente para que lo más nuevo salga arriba
    exps = conn.execute("SELECT * FROM experiencia WHERE usuario_id = ? ORDER BY ano DESC", (usuario_id,)).fetchall()
    conn.close()
    return exps

def agregar_educacion(usuario_id, institucion, nivel, ano):
    conn = conectar()
    conn.execute("INSERT INTO educacion (usuario_id, institucion, nivel, ano) VALUES (?, ?, ?, ?)",
                 (usuario_id, institucion, nivel, ano))
    conn.commit()
    conn.close()

def obtener_educacion(usuario_id):
    conn = conectar()
    eds = conn.execute("SELECT * FROM educacion WHERE usuario_id = ? ORDER BY ano DESC", (usuario_id,)).fetchall()
    conn.close()
    return eds

def eliminar_item(tabla, item_id, usuario_id):
    """Permite borrar una entrada específica de educación o experiencia"""
    conn = conectar()
    conn.execute(f"DELETE FROM {tabla} WHERE id = ? AND usuario_id = ?", (item_id, usuario_id))
    conn.commit()
    conn.close()

# --- FUNCIONES DE USUARIO EXISTENTES (Sin cambios mayores) ---

def registrar_usuario(nombre, email, password):
    try:
        conn = conectar()
        conn.execute("INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)", (nombre, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verificar_usuario(nombre, password):
    conn = conectar()
    usuario = conn.execute("SELECT * FROM usuarios WHERE nombre = ? AND password = ?", (nombre, password)).fetchone()
    conn.close()
    return usuario

def asignar_nuevo_token(usuario_id):
    nuevo_token = str(uuid.uuid4())
    conn = conectar()
    conn.execute("UPDATE usuarios SET token = ? WHERE id = ?", (nuevo_token, usuario_id))
    conn.commit()
    conn.close()
    return nuevo_token

def obtener_usuario_por_token(token):
    if not token: return None
    conn = conectar()
    usuario = conn.execute("SELECT * FROM usuarios WHERE token = ?", (token,)).fetchone()
    conn.close()
    return usuario

def borrar_token(token):
    conn = conectar()
    conn.execute("UPDATE usuarios SET token = NULL WHERE token = ?", (token,))
    conn.commit()
    conn.close()