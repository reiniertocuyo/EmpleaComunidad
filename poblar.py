import sqlite3
from datetime import datetime

DATABASE_NAME = "database.db"

def conectar():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def poblar_sistema():
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        print("🚀 Iniciando la inserción de datos de prueba...")

        # -------------------------------------------------------------------------
        # 1. DEFINICIÓN DE LAS 8 EMPRESAS
        # -------------------------------------------------------------------------
        empresas_demo = [
            # 6 Empresas del sector Informática/Tecnología
            {"user": "netcore", "email": "contacto@netcore.com", "nombre": "NetCore Telecom", "desc": "Especialistas en redes, infraestructura de fibra óptica y conectividad empresarial."},
            {"user": "devsolutions", "email": "rrhh@devsolutions.dev", "nombre": "DevSolutions S.A.", "desc": "Fábrica de software enfocada en aplicaciones web, móviles y soluciones cloud."},
            {"user": "electrovolt", "email": "info@electrovolt.com", "nombre": "ElectroVolt Ingeniería", "desc": "Empresa de automatización eléctrica, sistemas embebidos y hardware industrial."},
            {"user": "cybershield", "email": "ops@cybershield.io", "nombre": "CyberShield Security", "desc": "Consultoría avanzada en ciberseguridad, hacking ético y auditorías SOC."},
            {"user": "datacrafters", "email": "jobs@datacrafters.ai", "nombre": "DataCrafters Analytics", "desc": "Modelado de datos, Big Data e implementación de Inteligencia Artificial."},
            {"user": "bytesupport", "email": "soporte@bytesupport.com", "nombre": "ByteSupport Global", "desc": "Soporte técnico integral, mantenimiento de servidores y Help Desk 24/7."},
            
            # 2 Empresas de consumo masivo (Nada que ver con tech)
            {"user": "cocacola", "email": "empleos@cocacola.com", "nombre": "Coca-Cola Femsa", "desc": "Líder global en la producción y distribución de bebidas refrescantes."},
            {"user": "mcdonalds", "email": "talento@mcdonalds.com", "nombre": "McDonald's Arcos Dorados", "desc": "Cadena internacional de restaurantes de servicio rápido y hospitalidad."}
        ]

        # Diccionario para mapear el usuario de la empresa con su ID generado en la BD
        empresa_ids = {}

        for emp in empresas_demo:
            try:
                # Insertamos la empresa en la tabla de usuarios
                cursor.execute('''
                    INSERT INTO usuarios (nombre, email, password, tipo, nombre_completo, descripcion)
                    VALUES (?, ?, ?, 'empresa', ?, ?)
                ''', (emp['user'], emp['email'], 'clave123', emp['nombre'], emp['desc']))
                
                # Obtenemos el ID asignado automáticamente por SQLite
                empresa_ids[emp['user']] = cursor.lastrowid
                print(f"✅ Empresa creada: {emp['nombre']} (ID: {cursor.lastrowid})")
            except sqlite3.IntegrityError:
                # Si el usuario ya existe, lo buscamos para poder asignarle las vacantes de todos modos
                res = cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (emp['user'],)).fetchone()
                empresa_ids[emp['user']] = res['id']
                print(f"ℹ️ La empresa {emp['nombre']} ya existía (ID: {res['id']})")

        # -------------------------------------------------------------------------
        # 2. DEFINICIÓN DE LAS 3 VACANTES POR EMPRESA (Total: 24 vacantes)
        # Sincronizadas exactamente con: 'Bachiller', 'Certificaciones', 'Universitario'
        # -------------------------------------------------------------------------
        vacantes_demo = [
            # --- NetCore Telecom (Redes y Telecomunicaciones) ---
            {"empresa": "netcore", "titulo": "Técnico de Cableado Estructurado", "lugar": "Caracas", "mod": "Presencial", "e_min": 18, "e_max": 35, "edu": "Bachiller", "desc": "Instalación de racks, tendido de cable UTP/Fibra óptica. Trabajo de campo físico. No requiere experiencia previa."},
            {"empresa": "netcore", "titulo": "Administrador de Redes Cisco", "lugar": "Maracaibo", "mod": "Híbrido", "e_min": 23, "e_max": 45, "edu": "Certificaciones", "desc": "Configuración de switches, routers y VLANs. Soporte a fallas de enrutamiento y firewalls corporativos."},
            {"empresa": "netcore", "titulo": "Ingeniero de Telecomunicaciones Senior", "lugar": "Valencia", "mod": "Remoto", "e_min": 30, "e_max": 60, "edu": "Universitario", "desc": "Diseño de arquitecturas de red a gran escala para proveedores de servicios de internet (ISP). Certificación CCNP deseable."},

            # --- DevSolutions S.A. (Software) ---
            {"empresa": "devsolutions", "titulo": "Pasantía / Desarrollador Frontend Jr", "lugar": "Remoto", "mod": "Remoto", "e_min": 18, "e_max": 25, "edu": "Certificaciones", "desc": "Oportunidad para estudiantes. Maquetación de interfaces usando HTML, CSS y JavaScript básico. Tutoría incluida."},
            {"empresa": "devsolutions", "titulo": "Desarrollador Python / Flask Fullstack", "lugar": "Caracas", "mod": "Híbrido", "e_min": 22, "e_max": 40, "edu": "Universitario", "desc": "Creación y mantenimiento de aplicaciones web con Flask y bases de datos relacionales. Estructura de código limpia."},
            {"empresa": "devsolutions", "titulo": "Arquitecto de Software Cloud", "lugar": "Remoto", "mod": "Remoto", "e_min": 28, "e_max": 55, "edu": "Universitario", "desc": "Diseño de microservicios e infraestructura en la nube AWS/Azure. Optimización de costos y alta disponibilidad empresarial."},

            # --- ElectroVolt Ingeniería (Electricidad/Hardware) ---
            {"empresa": "electrovolt", "titulo": "Ayudante de Electricidad Industrial", "lugar": "Maracay", "mod": "Presencial", "e_min": 19, "e_max": 30, "edu": "Bachiller", "desc": "Asistencia en el montaje de tableros eléctricos y mantenimiento preventivo de motores industriales."},
            {"empresa": "electrovolt", "titulo": "Técnico en Automatización PLC", "lugar": "Valencia", "mod": "Presencial", "e_min": 24, "e_max": 50, "edu": "Certificaciones", "desc": "Programación y calibración de controladores lógicos programables (PLC) para líneas de producción automatizadas."},
            {"empresa": "electrovolt", "titulo": "Ingeniero de Sistemas Embebidos", "lugar": "Caracas", "mod": "Híbrido", "e_min": 25, "e_max": 45, "edu": "Universitario", "desc": "Diseño de firmware en C/C++ para microcontroladores arquitecturas ARM. Integración con sensores IoT."},

            # --- CyberShield Security (Ciberseguridad) ---
            {"empresa": "cybershield", "titulo": "Analista de Seguridad SOC Operativo", "lugar": "Remoto", "mod": "Remoto", "e_min": 21, "e_max": 35, "edu": "Certificaciones", "desc": "Monitoreo de alertas de seguridad en tiempo real, detección de anomalías y gestión de incidentes iniciales."},
            {"empresa": "cybershield", "titulo": "Consultor de Penetration Testing", "lugar": "Caracas", "mod": "Híbrido", "e_min": 24, "e_max": 45, "edu": "Universitario", "desc": "Ejecución de pruebas de hackeo ético controladas contra aplicaciones e infraestructura interna corporativa."},
            {"empresa": "cybershield", "titulo": "Auditor Líder de Ciberseguridad", "lugar": "Remoto", "mod": "Remoto", "e_min": 32, "e_max": 60, "edu": "Universitario", "desc": "Evaluación de normativas legales y estándares de seguridad internacional para entidades bancarias y de seguros."},

            # --- DataCrafters Analytics (Datos/IA) ---
            {"empresa": "datacrafters", "titulo": "Pasantía en Análisis de Datos con Excel", "lugar": "San Cristóbal", "mod": "Híbrido", "e_min": 18, "e_max": 24, "edu": "Bachiller", "desc": "Limpieza de tablas de datos, creación de reportes visuales dinámicos y apoyo al equipo de Business Intelligence."},
            {"empresa": "datacrafters", "titulo": "Ingeniero de Datos / ETL Developer", "lugar": "Caracas", "mod": "Remoto", "e_min": 23, "e_max": 40, "edu": "Universitario", "desc": "Construcción de tuberías de datos (pipelines) automatizadas, extracción y carga desde APIs hacia data warehouses."},
            {"empresa": "datacrafters", "titulo": "Científico de Datos para Modelos Predictivos", "lugar": "Remoto", "mod": "Remoto", "e_min": 26, "e_max": 50, "edu": "Universitario", "desc": "Desarrollo de algoritmos de Machine Learning y Deep Learning aplicados al comportamiento del consumidor financiero."},

            # --- ByteSupport Global (Soporte Técnico) ---
            {"empresa": "bytesupport", "titulo": "Agente de Soporte Técnico - Help Desk", "lugar": "Barquisimeto", "mod": "Presencial", "e_min": 18, "e_max": 28, "edu": "Bachiller", "desc": "Atención telefónica y remota de usuarios finales. Configuración de sistemas operativos, correos e instalación de software."},
            {"empresa": "bytesupport", "titulo": "Administrador de Servidores Linux/Windows", "lugar": "Caracas", "mod": "Híbrido", "e_min": 22, "e_max": 45, "edu": "Certificaciones", "desc": "Gestión de active directory, servidores web Apache/Nginx, backups automatizados y políticas de accesos corporativos."},
            {"empresa": "bytesupport", "titulo": "Gerente de Infraestructura IT", "lugar": "Valencia", "mod": "Presencial", "e_min": 30, "e_max": 55, "edu": "Universitario", "desc": "Coordinación y liderazgo de equipos de soporte físico, adquisición de servidores y optimización del data center local."},

            # --- Coca-Cola Femsa (No Tech - Consumo Masivo) ---
            {"empresa": "cocacola", "titulo": "Operario de Planta de Producción", "lugar": "Valencia", "mod": "Presencial", "e_min": 18, "e_max": 45, "edu": "Bachiller", "desc": "Control de empaquetado, etiquetado y supervisión de bandas transportadoras en planta industrial. Turnos rotativos."},
            {"empresa": "cocacola", "titulo": "Coordinador de Despacho y Logística", "lugar": "Guatire", "mod": "Presencial", "e_min": 25, "e_max": 50, "edu": "Certificaciones", "desc": "Planificación de rutas de camiones de distribución, inventarios de almacén de salida y control de facturación física."},
            {"empresa": "cocacola", "titulo": "Especialista Funcional de Sistemas SAP", "lugar": "Caracas", "mod": "Híbrido", "e_min": 26, "e_max": 48, "edu": "Universitario", "desc": "Gestión interna del ERP de la empresa (módulos MM y SD). Ajuste de procesos de ventas e inventario digital corporativo."},

            # --- McDonald's Arcos Dorados (No Tech - Alimentos) ---
            {"empresa": "mcdonalds", "titulo": "Personal de Equipo / Atención al Cliente", "lugar": "Caracas", "mod": "Presencial", "e_min": 18, "e_max": 24, "edu": "Bachiller", "desc": "Atención en caja, preparación de alimentos en cocina y mantenimiento de la limpieza del establecimiento. Ideal primer empleo."},
            {"empresa": "mcdonalds", "titulo": "Técnico de Mantenimiento de Maquinaria", "lugar": "Maracay", "mod": "Presencial", "e_min": 22, "e_max": 45, "edu": "Certificaciones", "desc": "Reparación y mantenimiento preventivo de freidoras industriales, máquinas de helado, sistemas de refrigeración y hornos."},
            {"empresa": "mcdonalds", "titulo": "Gerente de Turno de Restaurante", "lugar": "Valencia", "mod": "Presencial", "e_min": 24, "e_max": 38, "edu": "Certificaciones", "desc": "Liderazgo de equipos de atención rápidos, cuadre de cajas finales de turno, reportes de inventario diario y atención de reclamos."}
        ]

        # Insertamos todas las vacantes asociándolas con el id correcto de su empresa
        for vac in vacantes_demo:
            id_empresa = empresa_ids[vac['empresa']]
            cursor.execute('''
                INSERT INTO solicitudes_trabajo 
                (empresa_id, titulo, descripcion, modalidad, edad_minima, edad_maxima, nivel_educativo, lugar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_empresa, vac['titulo'], vac['desc'], vac['mod'], vac['e_min'], vac['e_max'], vac['edu'], vac['lugar']))
        
        conn.commit()
        print(f"\n🎉 ¡Éxito rotundo! Se registraron las 8 empresas y {len(vacantes_demo)} vacantes de prueba.")

    except Exception as e:
        print(f"❌ Error crítico al poblar la base de datos: {e}")
        if conn:
            conn.rollback()
            
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    poblar_sistema()