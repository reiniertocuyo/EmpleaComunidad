import sqlite3
import uuid

DATABASE_NAME = "database.db"

def conectar():
    # Incrementamos el timeout a 30 segundos por seguridad
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    # ACTIVAMOS EL MODO WAL: Evita el 99% de los problemas de "database is locked" en servidores web
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = conectar()
    try:
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

        # 5. Tabla de Solicitudes de Trabajo (Tu código original)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes_trabajo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            modalidad TEXT CHECK(modalidad IN ('Remoto', 'Presencial', 'Híbrido')),
            edad_minima INTEGER,
            edad_maxima INTEGER,
            nivel_educativo TEXT,
            lugar TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (empresa_id) REFERENCES usuarios (id)
        )
        ''')

        # --- NUEVA TABLA: 6. Postulaciones (Relación Muchos a Muchos) ---
        conn.execute('''
        CREATE TABLE IF NOT EXISTS postulaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            vacante_id INTEGER NOT NULL,
            fecha_postulacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (vacante_id) REFERENCES solicitudes_trabajo (id),
            UNIQUE(usuario_id, vacante_id) -- Evita que un usuario se postule dos veces a la misma vacante
        )
        ''')

        conn.commit()
    finally:
        conn.close()




# --- GESTIÓN DE PERFIL GENERAL ---

def actualizar_perfil(usuario_id, datos):
    """
    Actualiza los datos básicos. 
    'datos' puede incluir 'foto' si el usuario subió una nueva imagen.
    """
    conn = conectar()
    try:
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
        return True
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return False
    finally:
        conn.close()


# --- FUNCIONES PARA EMPRESAS ---

def agregar_contacto(usuario_id, tipo_contacto, valor):
    conn = conectar()
    try:
        conn.execute("INSERT INTO contactos_empresa (usuario_id, tipo_contacto, valor) VALUES (?, ?, ?)",
                     (usuario_id, tipo_contacto, valor))
        conn.commit()
    finally:
        conn.close()

def obtener_contactos(usuario_id):
    conn = conectar()
    try:
        contactos = conn.execute("SELECT * FROM contactos_empresa WHERE usuario_id = ?", (usuario_id,)).fetchall()
        return contactos
    finally:
        conn.close()

# --- GESTIÓN DE SESIÓN Y REGISTRO ---

def registrar_usuario(nombre, email, password, tipo='persona'):
    conn = conectar()
    try:
        # Al registrarse, la foto empieza como NULL (puedes poner una por defecto luego en el HTML)
        conn.execute(
            "INSERT INTO usuarios (nombre, email, password, tipo) VALUES (?, ?, ?, ?)", 
            (nombre, email, password, tipo)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_usuario(nombre, password):
    conn = conectar()
    try:
        usuario = conn.execute("SELECT * FROM usuarios WHERE nombre = ? AND password = ?", (nombre, password)).fetchone()
        return usuario
    finally:
        conn.close()

def asignar_nuevo_token(usuario_id):
    nuevo_token = str(uuid.uuid4())
    conn = conectar()
    try:
        conn.execute("UPDATE usuarios SET token = ? WHERE id = ?", (nuevo_token, usuario_id))
        conn.commit()
        return nuevo_token
    finally:
        conn.close()

def obtener_usuario_por_token(token):
    if not token: return None
    conn = conectar()
    try:
        usuario = conn.execute("SELECT * FROM usuarios WHERE token = ?", (token,)).fetchone()
        return usuario
    finally:
        conn.close()

def borrar_token(token):
    conn = conectar()
    try:
        conn.execute("UPDATE usuarios SET token = NULL WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()

# --- FUNCIONES PARA LISTAS (COMPARTIDAS) ---

def obtener_experiencia(usuario_id):
    conn = conectar()
    try:
        exps = conn.execute("SELECT * FROM experiencia WHERE usuario_id = ? ORDER BY ano DESC", (usuario_id,)).fetchall()
        return exps
    finally:
        conn.close()

def obtener_educacion(usuario_id):
    conn = conectar()
    try:
        eds = conn.execute("SELECT * FROM educacion WHERE usuario_id = ? ORDER BY ano DESC", (usuario_id,)).fetchall()
        return eds
    finally:
        conn.close()

def agregar_experiencia(usuario_id, compania, puesto, ano):
    conn = conectar()
    try:
        conn.execute("INSERT INTO experiencia (usuario_id, compania, puesto, ano) VALUES (?, ?, ?, ?)",
                     (usuario_id, compania, puesto, ano))
        conn.commit()
    finally:
        conn.close()

def agregar_educacion(usuario_id, institucion, nivel, ano):
    conn = conectar()
    try:
        conn.execute("INSERT INTO educacion (usuario_id, institucion, nivel, ano) VALUES (?, ?, ?, ?)",
                     (usuario_id, institucion, nivel, ano))
        conn.commit()
    finally:
        conn.close()

def eliminar_item(tabla, item_id, usuario_id):
    conn = conectar()
    try:
        conn.execute(f"DELETE FROM {tabla} WHERE id = ? AND usuario_id = ?", (item_id, usuario_id))
        conn.commit()
    finally:
        conn.close()


# vacantes de empresa y esas cosas
def crear_solicitud(empresa_id, datos):
    conn = conectar()
    try:
        conn.execute('''
            INSERT INTO solicitudes_trabajo 
            (empresa_id, titulo, descripcion, modalidad, edad_minima, edad_maxima, nivel_educativo, lugar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            empresa_id, datos['titulo'], datos['descripcion'], 
            datos['modalidad'], datos['edad_minima'], datos['edad_maxima'], 
            datos['nivel_educativo'], datos['lugar']
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al crear solicitud: {e}")
        return False
    finally:
        conn.close()

def obtener_mis_solicitudes(empresa_id):
    conn = conectar()
    try:
        solicitudes = conn.execute('''
            SELECT * FROM solicitudes_trabajo 
            WHERE empresa_id = ? 
            ORDER BY fecha_creacion DESC
        ''', (empresa_id,)).fetchall()
        return solicitudes
    finally:
        conn.close()

def eliminar_solicitud(solicitud_id, empresa_id):
    conn = conectar()
    try:
        conn.execute("DELETE FROM solicitudes_trabajo WHERE id = ? AND empresa_id = ?", (solicitud_id, empresa_id))
        conn.commit()
    finally:
        conn.close()


def obtener_solicitudes_busqueda(filtros=None, perfil_usuario=None):
    conn = conectar() 
    try:
        # Seleccionamos los datos de la vacante y el nombre/nombre_completo de la empresa
        query = """
            SELECT s.*, u.nombre AS empresa_username, u.nombre_completo AS empresa_nombre_real 
            FROM solicitudes_trabajo s
            INNER JOIN usuarios u ON s.empresa_id = u.id
            WHERE 1=1
        """
        params = []

        # 1. Filtro por palabra clave (Título, Descripción o Lugar)
        if filtros and filtros.get('keyword'):
            query += " AND (s.titulo LIKE ? OR s.descripcion LIKE ? OR s.lugar LIKE ?)"
            lk = f"%{filtros['keyword']}%"
            params.extend([lk, lk, lk])

        # 2. Filtro por Modalidad
        if filtros and filtros.get('modalidad'):
            query += " AND s.modalidad = ?"
            params.append(filtros['modalidad'])

        # 3. Matching Automático
        if perfil_usuario:
            # Filtro de Edad
            if perfil_usuario.get('edad'):
                query += " AND (s.edad_minima <= ? AND s.edad_maxima >= ?)"
                params.extend([perfil_usuario['edad'], perfil_usuario['edad']])
            
            # --- CAMBIO LÓGICO AQUÍ: Filtro Educativo Acumulativo ---
            # Intentamos leer la lista de niveles, o el nivel individual por compatibilidad
            niveles_edu = perfil_usuario.get('niveles_educativos') or perfil_usuario.get('nivel_educativo')
            
            if niveles_edu:
                # Si llega como un solo string (un solo estudio), lo convertimos a lista automáticamente
                if isinstance(niveles_edu, str):
                    niveles_edu = [niveles_edu]
                
                # Limpiamos de forma estricta strings vacíos o "Sin-especificar"
                niveles_edu = [n for n in niveles_edu if n and n != "Sin-especificar"]
                
                # Si el usuario tiene estudios válidos en su lista
                if niveles_edu:
                    # Creamos dinámicamente tantos "?" como elementos tenga la lista
                    # Ejemplo: si tiene 2 estudios, generará la cadena "?, ?"
                    placeholders = ', '.join(['?'] * len(niveles_edu))
                    
                    # Cambiamos el "=" por el operador "IN" de SQL
                    query += f" AND s.nivel_educativo IN ({placeholders})"
                    
                    # Agregamos todos los niveles al arreglo de parámetros de SQLite
                    params.extend(niveles_edu)

        # Especificamos s.fecha_creacion para el ordenamiento
        query += " ORDER BY s.fecha_creacion DESC"
        
        resultados = conn.execute(query, params).fetchall()
        return resultados

    except Exception as e:
        print(f"Error en obtener_solicitudes_busqueda: {e}")
        return []
    finally:
        conn.close()


# --- FUNCIONES PARA PERFILES PÚBLICOS DINÁMICOS ---

def obtener_usuario_por_username(username):
    """Busca cualquier tipo de usuario por su nombre exacto (el @)"""
    conn = conectar()
    try:
        # Trae todos los datos: id, nombre, tipo, descripcion, foto, etc.
        usuario = conn.execute("SELECT * FROM usuarios WHERE nombre = ?", (username,)).fetchone()
        return usuario
    finally:
        conn.close()



# --- NUEVAS FUNCIONES DE NEGOCIO EN DB_MANAGER ---

def registrar_postulacion(usuario_id, vacante_id):
    """Inserta un registro de postulación en la base de datos."""
    conn = conectar()
    try:
        # Usamos INSERT OR IGNORE por seguridad debido al constraint UNIQUE
        conn.execute("""
            INSERT OR IGNORE INTO postulaciones (usuario_id, vacante_id) 
            VALUES (?, ?)
        """, (usuario_id, vacante_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error en registrar_postulacion: {e}")
        return False
    finally:
        conn.close()

def obtener_postulados_por_vacante(vacante_id):
    """Devuelve la lista de usuarios que se han anexado a una vacante específica."""
    conn = conectar()
    try:
        query = """
            SELECT u.nombre, u.nombre_completo, u.foto
            FROM postulaciones p
            INNER JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.vacante_id = ?
            ORDER BY p.fecha_postulacion DESC
        """
        return conn.execute(query, (vacante_id,)).fetchall()
    except Exception as e:
        print(f"Error en obtener_postulados_por_vacante: {e}")
        return []
    finally:
        conn.close()

def obtener_vacantes_postuladas_por_usuario(usuario_id):
    """Devuelve una lista plana con los IDs de las vacantes a las que aplicó el usuario."""
    conn = conectar()
    try:
        resultados = conn.execute("SELECT vacante_id FROM postulaciones WHERE usuario_id = ?", (usuario_id,)).fetchall()
        return [r['vacante_id'] for r in resultados]
    except Exception as e:
        print(f"Error en obtener_vacantes_postuladas_por_usuario: {e}")
        return []
    finally:
        conn.close() 