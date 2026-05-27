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
        # 1. Tabla de Usuarios (Añadimos 'estatus' con CHECK y 'cv_ruta')
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
            foto TEXT, -- Nombre del archivo de imagen (ej: "usuario_1.png")
            estatus TEXT DEFAULT 'Disponible' CHECK(estatus IN ('Disponible', 'Inactivo', 'Contratado')),
            cv_ruta TEXT -- Nombre del archivo PDF/PNG del Currículum (ej: "cv_1.pdf")
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

        # 5. Tabla de Solicitudes de Trabajo (Añadimos pago_monto y pago_tipo obligatorios)
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
            pago_monto REAL NOT NULL, -- Obligatorio
            pago_tipo TEXT NOT NULL CHECK(pago_tipo IN ('Por hora', 'Por día')), -- Obligatorio
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (empresa_id) REFERENCES usuarios (id)
        )
        ''')

        # 6. Postulaciones (Relación Muchos a Muchos)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS postulaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            vacante_id INTEGER NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
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
    Actualiza los datos básicos de personas o empresas. 
    'datos' ahora puede incluir 'estatus' y 'cv_ruta'.
    """
    conn = conectar()
    try:
        # Agregamos COALESCE para cv_ruta y estatus para que mantengan su valor si no se envían nuevos datos
        conn.execute('''
            UPDATE usuarios SET 
                nombre_completo = ?, 
                descripcion = ?, 
                genero = ?, 
                fecha_nacimiento = ?,
                foto = COALESCE(?, foto),
                estatus = COALESCE(?, estatus),
                cv_ruta = COALESCE(?, cv_ruta)
            WHERE id = ?
        ''', (
            datos['nombre_completo'], 
            datos['descripcion'], 
            datos.get('genero'), 
            datos.get('fecha_nacimiento'),
            datos.get('foto'),
            datos.get('estatus'),
            datos.get('cv_ruta'),
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
        # Por defecto el estatus inicial para 'persona' es 'Disponible'
        estatus_inicial = 'Disponible' if tipo == 'persona' else None
        conn.execute(
            "INSERT INTO usuarios (nombre, email, password, tipo, estatus) VALUES (?, ?, ?, ?, ?)", 
            (nombre, email, password, tipo, estatus_inicial)
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
        
        if usuario:
            usuario_dict = dict(usuario)
            if usuario_dict['tipo'] == 'persona':
                # Llamamos a la función que acabamos de corregir
                usuario_dict['estatus'] = obtener_estatus_real(usuario_dict['id'])
            return usuario_dict
        return None
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


# --- GESTIÓN DE VACANTES (SOLICITUDES DE TRABAJO) ---

def crear_solicitud(empresa_id, datos):
    conn = conectar()
    try:
        # Se añaden 'pago_monto' y 'pago_tipo' a la inserción obligatoria
        conn.execute('''
            INSERT INTO solicitudes_trabajo 
            (empresa_id, titulo, descripcion, modalidad, edad_minima, edad_maxima, nivel_educativo, lugar, pago_monto, pago_tipo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            empresa_id, datos['titulo'], datos['descripcion'], 
            datos['modalidad'], datos['edad_minima'], datos['edad_maxima'], 
            datos['nivel_educativo'], datos['lugar'], datos['pago_monto'], datos['pago_tipo']
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
        # Ahora también traemos pago_monto y pago_tipo en el SELECT general
        query = """
            SELECT s.*, u.nombre AS empresa_username, u.nombre_completo AS empresa_nombre_real 
            FROM solicitudes_trabajo s
            INNER JOIN usuarios u ON s.empresa_id = u.id
            WHERE 1=1
        """
        params = []

        if filtros:
            if filtros.get('keyword'):
                query += " AND (s.titulo LIKE ? OR s.descripcion LIKE ? OR s.lugar LIKE ?)"
                lk = f"%{filtros['keyword']}%"
                params.extend([lk, lk, lk])

            if filtros.get('modalidad'):
                query += " AND s.modalidad = ?"
                params.append(filtros['modalidad'])

            # --- NUEVOS FILTROS DE PAGO ---
            if filtros.get('pago_min'):
                query += " AND s.pago_monto >= ?"
                params.append(filtros['pago_min'])

            if filtros.get('pago_tipo'):
                query += " AND s.pago_tipo = ?"
                params.append(filtros['pago_tipo'])

        if perfil_usuario:
            if perfil_usuario.get('edad'):
                query += " AND (s.edad_minima <= ? AND s.edad_maxima >= ?)"
                params.extend([perfil_usuario['edad'], perfil_usuario['edad']])
            
            niveles_edu = perfil_usuario.get('niveles_educativos') or perfil_usuario.get('nivel_educativo')
            
            if niveles_edu:
                if isinstance(niveles_edu, str):
                    niveles_edu = [niveles_edu]
                
                niveles_edu = [n for n in niveles_edu if n and n != "Sin-especificar"]
                
                if niveles_edu:
                    placeholders = ', '.join(['?'] * len(niveles_edu))
                    query += f" AND s.nivel_educativo IN ({placeholders})"
                    params.extend(niveles_edu)

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
    conn = conectar()
    try:
        usuario = conn.execute("SELECT * FROM usuarios WHERE nombre = ?", (username,)).fetchone()
        return usuario
    finally:
        conn.close()


# --- GESTIÓN DE POSTULACIONES Y MÉTRICAS ---

def registrar_postulacion(usuario_id, vacante_id):
    conn = conectar()
    try:
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
    conn = conectar()
    try:
        # Traemos el id de la postulación (como postulacion_id) y su estado real 
        query = """
            SELECT p.id AS postulacion_id, p.estado AS estado_postulacion, 
                   u.id AS usuario_id, u.nombre, u.nombre_completo, u.foto, u.estatus, u.cv_ruta
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
    conn = conectar()
    try:
        resultados = conn.execute("SELECT vacante_id FROM postulaciones WHERE usuario_id = ?", (usuario_id,)).fetchall()
        return [r['vacante_id'] for r in resultados]
    except Exception as e:
        print(f"Error en obtener_vacantes_postuladas_por_usuario: {e}")
        return []
    finally:
        conn.close() 

def calcular_tasa_contratacion(empresa_id):
    """
    Calcula dinámicamente la tasa de contratación de una empresa basándose en 
    el estatus actual de las personas que se han postulado a sus vacantes.
    """
    conn = conectar()
    try:
        # 1. Contamos el total de personas únicas postuladas a las vacantes de esta empresa
        total_postulados = conn.execute("""
            SELECT COUNT(DISTINCT p.usuario_id) 
            FROM postulaciones p
            INNER JOIN solicitudes_trabajo s ON p.vacante_id = s.id
            WHERE s.empresa_id = ?
        """, (empresa_id,)).fetchone()[0]

        if total_postulados == 0:
            return 0.0

        # 2. Contamos cuántos de esos postulados específicos tienen estatus de 'Contratado'
        total_contratados = conn.execute("""
            SELECT COUNT(DISTINCT p.usuario_id) 
            FROM postulaciones p
            INNER JOIN solicitudes_trabajo s ON p.vacante_id = s.id
            INNER JOIN usuarios u ON p.usuario_id = u.id
            WHERE s.empresa_id = ? AND u.estatus = 'Contratado'
        """, (empresa_id,)).fetchone()[0]

        # Calculamos el porcentaje
        porcentaje = (total_contratados / total_postulados) * 100
        return round(porcentaje, 1)
    except Exception as e:
        print(f"Error al calcular tasa de contratación: {e}")
        return 0.0
    finally:
        conn.close()



def obtener_estatus_real(usuario_id):
    conn = conectar()
    try:
        # IMPORTANTE: Asegúrate de que la tabla 'postulaciones' 
        # tenga una columna llamada 'estado' y que exista el valor 'Aceptado'
        contratacion = conn.execute("""
            SELECT 1 FROM postulaciones 
            WHERE usuario_id = ? AND estado = 'Aceptado' 
            LIMIT 1
        """, (usuario_id,)).fetchone()
        
        return 'Contratado' if contratacion else 'Disponible'
    finally:
        conn.close()


def actualizar_estado_postulacion(postulacion_id, empresa_id, nuevo_estado):
    """
    Actualiza el estado de una postulación.
    nuevo_estado debe ser 'Aceptado' o 'Rechazado'.
    """
    conn = conectar()
    try:
        # Verificamos primero que la vacante pertenezca realmente a la empresa 
        # para evitar que una empresa modifique postulaciones ajenas
        cursor = conn.execute("""
            UPDATE postulaciones 
            SET estado = ? 
            WHERE id = ? AND vacante_id IN (
                SELECT id FROM solicitudes_trabajo WHERE empresa_id = ?
            )
        """, (nuevo_estado, postulacion_id, empresa_id))
        
        conn.commit()
        return cursor.rowcount > 0 # Retorna True si se actualizó algo
    except Exception as e:
        print(f"Error al actualizar estado: {e}")
        return False
    finally:
        conn.close()