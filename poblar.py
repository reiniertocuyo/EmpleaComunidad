import sqlite3
import random
from datetime import datetime

DATABASE_NAME = "database.db"

def conectar():
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    # Activamos modo WAL también aquí para agilizar las inserciones masivas de prueba
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn

def poblar_sistema():
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        print("🚀 Iniciando la inserción de datos de prueba adaptados a las nuevas exigencias...")

        # -------------------------------------------------------------------------
        # 1. DEFINICIÓN DE LAS 8 EMPRESAS
        # -------------------------------------------------------------------------
        empresas_demo = [
            {"user": "netcore", "email": "contacto@netcore.com", "nombre": "NetCore Telecom", "desc": "Especialistas en redes, infraestructura de fibra óptica y conectividad empresarial."},
            {"user": "devsolutions", "email": "rrhh@devsolutions.dev", "nombre": "DevSolutions S.A.", "desc": "Fábrica de software enfocada en aplicaciones web, móviles y soluciones cloud."},
            {"user": "electrovolt", "email": "info@electrovolt.com", "nombre": "ElectroVolt Ingeniería", "desc": "Empresa de automatización eléctrica, sistemas embebidos y hardware industrial."},
            {"user": "cybershield", "email": "ops@cybershield.io", "nombre": "CyberShield Security", "desc": "Consultoría avanzada en ciberseguridad, hacking ético y auditorías SOC."},
            {"user": "datacrafters", "email": "jobs@datacrafters.ai", "nombre": "DataCrafters Analytics", "desc": "Modelado de datos, Big Data e implementación de Inteligencia Artificial."},
            {"user": "bytesupport", "email": "soporte@bytesupport.com", "nombre": "ByteSupport Global", "desc": "Soporte técnico integral, mantenimiento de servidores y Help Desk 24/7."},
            {"user": "cocacola", "email": "empleos@cocacola.com", "nombre": "Coca-Cola Femsa", "desc": "Líder global en la producción y distribución de bebidas refrescantes."},
            {"user": "mcdonalds", "email": "talento@mcdonalds.com", "nombre": "McDonald's Arcos Dorados", "desc": "Cadena internacional de restaurantes de servicio rápido y hospitalidad."}
        ]

        # DATOS DE CONTACTO PARA CADA EMPRESA
        contactos_demo = {
            "netcore": [("Teléfono", "+58 212-5551122"), ("Web", "https://netcore.com"), ("LinkedIn", "linkedin.com/company/netcore-telecom")],
            "devsolutions": [("Teléfono", "+58 212-5553344"), ("Slack Public", "devsolutions-community.slack.com"), ("Web", "https://devsolutions.dev")],
            "electrovolt": [("Teléfono", "+58 243-5557788"), ("Soporte", "soporte@electrovolt.com")],
            "cybershield": [("Web", "https://cybershield.io"), ("Signal", "cybershield.sec.ops")],
            "datacrafters": [("Web", "https://datacrafters.ai"), ("LinkedIn", "linkedin.com/company/datacrafters-ai")],
            "bytesupport": [("Teléfono", "+58 251-5559900"), ("WhatsApp", "+58 412-5550011"), ("Web", "https://bytesupport.com")],
            "cocacola": [("Teléfono", "+58 212-9991111"), ("Web", "https://coca-colafemsa.com"), ("Instagram", "@cocacolafemsa_ve")],
            "mcdonalds": [("Teléfono", "+58 212-8882222"), ("Web", "https://mcdonalds.com.ve"), ("Instagram", "@mcdonalds_ve")]
        }

        # Diccionario para mapear el usuario de la empresa con su ID generado en la BD
        empresa_ids = {}

        for emp in empresas_demo:
            try:
                cursor.execute('''
                    INSERT INTO usuarios (nombre, email, password, tipo, nombre_completo, descripcion, estatus)
                    VALUES (?, ?, ?, 'empresa', ?, ?, NULL)
                ''', (emp['user'], emp['email'], 'clave123', emp['nombre'], emp['desc']))
                empresa_ids[emp['user']] = cursor.lastrowid
                print(f"✅ Empresa creada: {emp['nombre']} (ID: {cursor.lastrowid})")
            except sqlite3.IntegrityError:
                res = cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (emp['user'],)).fetchone()
                empresa_ids[emp['user']] = res['id']
                print(f"ℹ️ La empresa {emp['nombre']} ya existía (ID: {res['id']})")

            id_empresa = original_id = empresa_ids[emp['user']]
            cursor.execute("DELETE FROM contactos_empresa WHERE usuario_id = ?", (id_empresa,))
            
            for tipo, valor in contactos_demo[emp['user']]:
                cursor.execute('''
                    INSERT INTO contactos_empresa (usuario_id, tipo_contacto, valor)
                    VALUES (?, ?, ?)
                ''', (id_empresa, tipo, valor))

        # -------------------------------------------------------------------------
        # 2. INSERTAR USUARIOS TIPO PERSONA (Candidatos de prueba)
        # -------------------------------------------------------------------------
        personas_demo = [
            {"user": "pedro_dev", "email": "pedro@gmail.com", "nombre": "Pedro Pérez", "desc": "Desarrollador enfocado en Python.", "estatus": "Disponible"},
            {"user": "maria_infra", "email": "maria@gmail.com", "nombre": "María Rodríguez", "desc": "Técnico especialista en redes.", "estatus": "Contratado"},
            {"user": "luis_ayudante", "email": "luis@gmail.com", "nombre": "Luis Gómez", "desc": "Bachiller buscando su primer empleo.", "estatus": "Inactivo"}
        ]
        
        # Mapeamos los candidatos por nombre de usuario para controlar la lógica relacional posterior
        persona_ids_dict = {}
        for per in personas_demo:
            try:
                cursor.execute('''
                    INSERT INTO usuarios (nombre, email, password, tipo, nombre_completo, descripcion, estatus, cv_ruta)
                    VALUES (?, ?, ?, 'persona', ?, ?, ?, NULL)
                ''', (per['user'], per['email'], 'clave123', per['nombre'], per['desc'], per['estatus']))
                persona_ids_dict[per['user']] = cursor.lastrowid
            except sqlite3.IntegrityError:
                res = cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (per['user'],)).fetchone()
                persona_ids_dict[per['user']] = res['id']
                # Actualizamos el estatus por si acaso quedó desincronizado en pruebas previas
                cursor.execute("UPDATE usuarios SET estatus = ? WHERE id = ?", (per['estatus'], res['id']))

        # -------------------------------------------------------------------------
        # 3. DEFINICIÓN DE LAS VACANTES ADAPTADAS CON PAGO MANDATORIO
        # -------------------------------------------------------------------------
        vacantes_demo = [
            # --- NetCore Telecom ---
            {"empresa": "netcore", "titulo": "Técnico de Cableado Estructurado", "lugar": "Caracas", "mod": "Presencial", "e_min": 18, "e_max": 35, "edu": "Bachiller", "pago": 15.0, "p_tipo": "Por día", "desc": "Instalación de racks, tendido de cable UTP/Fibra óptica. Trabajo de campo físico. No requiere experiencia previa."},
            {"empresa": "netcore", "titulo": "Administrador de Redes Cisco", "lugar": "Maracaibo", "mod": "Híbrido", "e_min": 23, "e_max": 45, "edu": "Certificaciones", "pago": 8.5, "p_tipo": "Por hora", "desc": "Configuración de switches, routers y VLANs. Soporte a fallas de enrutamiento y firewalls corporativos."},
            {"empresa": "netcore", "titulo": "Ingeniero de Telecomunicaciones Senior", "lugar": "Valencia", "mod": "Remoto", "e_min": 30, "e_max": 60, "edu": "Universitario", "pago": 80.0, "p_tipo": "Por día", "desc": "Diseño de arquitecturas de red a gran escala para proveedores de servicios de internet (ISP). Certificación CCNP deseable."},

            # --- DevSolutions S.A. ---
            {"empresa": "devsolutions", "titulo": "Pasantía / Desarrollador Frontend Jr", "lugar": "Remoto", "mod": "Remoto", "e_min": 18, "e_max": 25, "edu": "Certificaciones", "pago": 4.0, "p_tipo": "Por hora", "desc": "Oportunidad para estudiantes. Maquetación de interfaces usando HTML, CSS y JavaScript básico. Tutoría incluida."},
            {"empresa": "devsolutions", "titulo": "Desarrollador Python / Flask Fullstack", "lugar": "Caracas", "mod": "Híbrido", "e_min": 22, "e_max": 40, "edu": "Universitario", "pago": 15.0, "p_tipo": "Por hora", "desc": "Creación y mantenimiento de aplicaciones web con Flask y bases de datos relacionales. Estructura de código limpia."},
            {"empresa": "devsolutions", "titulo": "Arquitecto de Software Cloud", "lugar": "Remoto", "mod": "Remoto", "e_min": 28, "e_max": 55, "edu": "Universitario", "pago": 120.0, "p_tipo": "Por día", "desc": "Diseño de microservicios e infraestructura en la nube AWS/Azure. Optimización de costos y alta disponibilidad empresarial."},

            # --- ElectroVolt Ingeniería ---
            {"empresa": "electrovolt", "titulo": "Ayudante de Electricidad Industrial", "lugar": "Maracay", "mod": "Presencial", "e_min": 19, "e_max": 30, "edu": "Bachiller", "pago": 12.5, "p_tipo": "Por día", "desc": "Asistencia en el montaje de tableros eléctricos y mantenimiento preventivo de motores industriales."},
            {"empresa": "electrovolt", "titulo": "Técnico en Automatización PLC", "lugar": "Valencia", "mod": "Presencial", "e_min": 24, "e_max": 50, "edu": "Certificaciones", "pago": 25.0, "p_tipo": "Por día", "desc": "Programación y calibración de controladores lógicos programables (PLC) para líneas de producción automatizadas."},
            {"empresa": "electrovolt", "titulo": "Ingeniero de Sistemas Embebidos", "lugar": "Caracas", "mod": "Híbrido", "e_min": 25, "e_max": 45, "edu": "Universitario", "pago": 20.0, "p_tipo": "Por hora", "desc": "Diseño de firmware en C/C++ para microcontroladores arquitecturas ARM. Integración con sensores IoT."},

            # --- CyberShield Security ---
            {"empresa": "cybershield", "titulo": "Analista de Seguridad SOC Operativo", "lugar": "Remoto", "mod": "Remoto", "e_min": 21, "e_max": 35, "edu": "Certificaciones", "pago": 12.0, "p_tipo": "Por hora", "desc": "Monitoreo de alertas de seguridad en tiempo real, detección de anomalías y gestión de incidentes iniciales."},
            {"empresa": "cybershield", "titulo": "Consultor de Penetration Testing", "lugar": "Caracas", "mod": "Híbrido", "e_min": 24, "e_max": 45, "edu": "Universitario", "pago": 65.0, "p_tipo": "Por día", "desc": "Ejecución de pruebas de hackeo ético controladas contra aplicaciones e infraestructura interna corporativa."},
            {"empresa": "cybershield", "titulo": "Auditor Líder de Ciberseguridad", "lugar": "Remoto", "mod": "Remoto", "e_min": 32, "e_max": 60, "edu": "Universitario", "pago": 90.0, "p_tipo": "Por día", "desc": "Evaluación de normativas legales y estándares de seguridad internacional para entidades bancarias y de seguros."},

            # --- DataCrafters Analytics ---
            {"empresa": "datacrafters", "titulo": "Pasantía en Análisis de Datos con Excel", "lugar": "San Cristóbal", "mod": "Híbrido", "e_min": 18, "e_max": 24, "edu": "Bachiller", "pago": 3.5, "p_tipo": "Por hora", "desc": "Limpieza de tablas de datos, creación de reportes visuales dinámicos y apoyo al equipo de Business Intelligence."},
            {"empresa": "datacrafters", "titulo": "Ingeniero de Datos / ETL Developer", "lugar": "Caracas", "mod": "Remoto", "e_min": 23, "e_max": 40, "edu": "Universitario", "pago": 18.0, "p_tipo": "Por hora", "desc": "Construcción de tuberías de datos (pipelines) automatizadas, extracción y carga desde APIs hacia data warehouses."},
            {"empresa": "datacrafters", "titulo": "Científico de Datos para Modelos Predictivos", "lugar": "Remoto", "mod": "Remoto", "e_min": 26, "e_max": 50, "edu": "Universitario", "pago": 100.0, "p_tipo": "Por día", "desc": "Desarrollo de algoritmos de Machine Learning y Deep Learning aplicados al comportamiento del consumidor financiero."},

            # --- ByteSupport Global ---
            {"empresa": "bytesupport", "titulo": "Agente de Soporte Técnico - Help Desk", "lugar": "Barquisimeto", "mod": "Presencial", "e_min": 18, "e_max": 28, "edu": "Bachiller", "pago": 5.0, "p_tipo": "Por hora", "desc": "Atención telefónica y remota de usuarios finales. Configuración de sistemas operativos, correos e instalación de software."},
            {"empresa": "bytesupport", "titulo": "Administrador de Servidores Linux/Windows", "lugar": "Caracas", "mod": "Híbrido", "e_min": 22, "e_max": 45, "edu": "Certificaciones", "pago": 30.0, "p_tipo": "Por día", "desc": "Gestión de active directory, servidores web Apache/Nginx, backups automatizados y políticas de accesos corporativos."},
            {"empresa": "bytesupport", "titulo": "Gerente de Infraestructura IT", "lugar": "Valencia", "mod": "Presencial", "e_min": 30, "e_max": 55, "edu": "Universitario", "pago": 70.0, "p_tipo": "Por día", "desc": "Coordinación y liderazgo de equipos de soporte físico, adquisición de servidores y optimización del data center local."},

            # --- Coca-Cola Femsa ---
            {"empresa": "cocacola", "titulo": "Operario de Planta de Producción", "lugar": "Valencia", "mod": "Presencial", "e_min": 18, "e_max": 45, "edu": "Bachiller", "pago": 20.0, "p_tipo": "Por día", "desc": "Control de empaquetado, etiquetado y supervisión de bandas transportadoras en planta industrial. Turnos rotativos."},
            {"empresa": "cocacola", "titulo": "Coordinador de Despacho y Logística", "lugar": "Guatire", "mod": "Presencial", "e_min": 25, "e_max": 50, "edu": "Certificaciones", "pago": 35.0, "p_tipo": "Por día", "desc": "Planificación de rutas de camiones de distribución, inventarios de almacén de salida y control de facturación física."},
            {"empresa": "cocacola", "titulo": "Especialista Funcional de Sistemas SAP", "lugar": "Caracas", "mod": "Híbrido", "e_min": 26, "e_max": 48, "edu": "Universitario", "pago": 25.0, "p_tipo": "Por hora", "desc": "Gestión interna del ERP de la empresa (módulos MM y SD). Ajuste de procesos de ventas e inventario digital corporativo."},

            # --- McDonald's Arcos Dorados ---
            {"empresa": "mcdonalds", "titulo": "Personal de Equipo / Atención al Cliente", "lugar": "Caracas", "mod": "Presencial", "e_min": 18, "e_max": 24, "edu": "Bachiller", "pago": 2.5, "p_tipo": "Por hora", "desc": "Atención en caja, preparación de alimentos en cocina y mantenimiento de la limpieza del establecimiento. Ideal primer empleo."},
            {"empresa": "mcdonalds", "titulo": "Técnico de Mantenimiento de Maquinaria", "lugar": "Maracay", "mod": "Presencial", "e_min": 22, "e_max": 45, "edu": "Certificaciones", "pago": 25.0, "p_tipo": "Por día", "desc": "Reparación y mantenimiento preventivo de freidoras industriales, máquinas de helado, sistemas de refrigeración y hornos."},
            {"empresa": "mcdonalds", "titulo": "Gerente de Turno de Restaurante", "lugar": "Valencia", "mod": "Presencial", "e_min": 24, "e_max": 38, "edu": "Certificaciones", "pago": 40.0, "p_tipo": "Por día", "desc": "Liderazgo de equipos de atención rápidos, cuadre de cajas finales de turno, reportes de inventario diario y atención de reclamos."}
        ]

        # Limpiamos las vacantes y postulaciones viejas para evitar conflictos relacionales
        cursor.execute("DELETE FROM postulaciones")
        cursor.execute("DELETE FROM solicitudes_trabajo")

        # Insertamos todas las vacantes
        vacantes_ids_generados = []
        for vac in vacantes_demo:
            id_empresa = empresa_ids[vac['empresa']]
            cursor.execute('''
                INSERT INTO solicitudes_trabajo 
                (empresa_id, titulo, descripcion, modalidad, edad_minima, edad_maxima, nivel_educativo, lugar, pago_monto, pago_tipo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_empresa, vac['titulo'], vac['desc'], vac['mod'], vac['e_min'], vac['e_max'], vac['edu'], vac['lugar'], vac['pago'], vac['p_tipo']))
            vacantes_ids_generados.append(cursor.lastrowid)

        # -------------------------------------------------------------------------
        # ACTUALIZADO: AUTO-POSTULAR DE FORMA COHERENTE CON LOS ESTADOS (Check Constraints)
        # -------------------------------------------------------------------------
        if persona_ids_dict and vacantes_ids_generados:
            for username, pid in persona_ids_dict.items():
                # Tomamos 2 vacantes al azar
                vacantes_muestreadas = random.sample(vacantes_ids_generados, 2)
                
                for idx, vid in enumerate(vacantes_muestreadas):
                    # Forzamos lógica relacional basada en su estatus de perfil:
                    if username == "maria_infra":
                        # El primer registro de María será 'Aceptado' para satisfacer el algoritmo 'obtener_estatus_real'
                        estado_postulacion = 'Aceptado' if idx == 0 else 'Pendiente'
                    elif username == "luis_ayudante":
                        # Luis está inactivo, simulamos que fue rechazado o sigue pendiente
                        estado_postulacion = 'Rechazado' if idx == 0 else 'Pendiente'
                    else:
                        # Pedro_dev está disponible, dejamos que sus postulaciones estén en revisión activa
                        estado_postulacion = 'Pendiente'

                    cursor.execute('''
                        INSERT OR IGNORE INTO postulaciones (usuario_id, vacante_id, estado)
                        VALUES (?, ?, ?)
                    ''', (pid, vid, estado_postulacion))

        conn.commit()
        print(f"\n🎉 ¡Éxito! Se registraron las empresas, sus canales de contacto, las {len(vacantes_demo)} vacantes estructuradas y el histórico relacional de postulaciones con estados sincronizados.")

    except Exception as e:
        print(f"❌ Error crítico al poblar la base de datos: {e}")
        if conn:
            conn.rollback()
            
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    poblar_sistema()