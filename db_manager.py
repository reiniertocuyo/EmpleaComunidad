import sqlite3
import uuid

DATABASE_NAME = "database.db"

def conectar():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = conectar()
    
    # 1. Tabla de Usuarios (Añadimos 'foto' para guardar la ruta de la imagen)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE, 
        password TEXT NOT NULL,
        token TEXT,
        tipo TEXT NOT NULL DEFAULT 'persona', -- 'persona' o 'empresa'
        nombre_completo TEXT,
        descripcion TEXT,
        genero TEXT,
        fecha_nacimiento TEXT,
        foto TEXT -- Aquí guardaremos el nombre del archivo (ej: "usuario_1.png")
    )
    ''')

    # 2. Experiencia Laboral
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

    # 3. Educación
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

    # 4. Contactos para Empresas
    conn.execute('''
    CREATE TABLE IF NOT EXISTS contactos_empresa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        tipo_contacto TEXT NOT NULL, 
        valor TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')

    conn.commit()
    conn.close()

# --- GESTIÓN DE PERFIL GENERAL ---

def actualizar_perfil(usuario_id, datos):
    """
    Actualiza los datos básicos. 
    'datos' puede incluir 'foto' si el usuario subió una nueva imagen.
    """
    try:
        conn = conectar()
        # Usamos COALESCE para la foto: si no viene en 'datos', mantiene la que ya estaba en la BD
        conn.execute('''
            UPDATE usuarios SET 
                nombre_completo = ?, 
                descripcion = ?, 
                genero = ?, 
                fecha_nacimiento = ?,
                foto = COALESCE(?, foto) 
            WHERE id = ?
        ''', (
            datos['nombre_completo'], 
            datos['descripcion'], 
            datos.get('genero'), 
            datos.get('fecha_nacimiento'),
            datos.get('foto'), # Ruta de la imagen
            usuario_id
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return False

# --- FUNCIONES PARA EMPRESAS ---

def agregar_contacto(usuario_id, tipo_contacto, valor):
    conn = conectar()
    conn.execute("INSERT INTO contactos_empresa (usuario_id, tipo_contacto, valor) VALUES (?, ?, ?)",
                 (usuario_id, tipo_contacto, valor))
    conn.commit()
    conn.close()

def obtener_contactos(usuario_id):
    conn = conectar()
    contactos = conn.execute("SELECT * FROM contactos_empresa WHERE usuario_id = ?", (usuario_id,)).fetchall()
    conn.close()
    return contactos

# --- GESTIÓN DE SESIÓN Y REGISTRO ---

def registrar_usuario(nombre, email, password, tipo='persona'):
    try:
        conn = conectar()
        # Al registrarse, la foto empieza como NULL (puedes poner una por defecto luego en el HTML)
        conn.execute(
            "INSERT INTO usuarios (nombre, email, password, tipo) VALUES (?, ?, ?, ?)", 
            (nombre, email, password, tipo)
        )
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

# --- FUNCIONES PARA LISTAS (COMPARTIDAS) ---

def obtener_experiencia(usuario_id):
    conn = conectar()
    exps = conn.execute("SELECT * FROM experiencia WHERE usuario_id = ? ORDER BY ano DESC", (usuario_id,)).fetchall()
    conn.close()
    return exps

def obtener_educacion(usuario_id):
    conn = conectar()
    eds = conn.execute("SELECT * FROM educacion WHERE usuario_id = ? ORDER BY ano DESC", (usuario_id,)).fetchall()
    conn.close()
    return eds

def agregar_experiencia(usuario_id, compania, puesto, ano):
    conn = conectar()
    conn.execute("INSERT INTO experiencia (usuario_id, compania, puesto, ano) VALUES (?, ?, ?, ?)",
                 (usuario_id, compania, puesto, ano))
    conn.commit()
    conn.close()

def agregar_educacion(usuario_id, institucion, nivel, ano):
    conn = conectar()
    conn.execute("INSERT INTO educacion (usuario_id, institucion, nivel, ano) VALUES (?, ?, ?, ?)",
                 (usuario_id, institucion, nivel, ano))
    conn.commit()
    conn.close()

def eliminar_item(tabla, item_id, usuario_id):
    conn = conectar()
    conn.execute(f"DELETE FROM {tabla} WHERE id = ? AND usuario_id = ?", (item_id, usuario_id))
    conn.commit()
    conn.close()