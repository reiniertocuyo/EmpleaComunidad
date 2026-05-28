import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from datetime import date
from flask_mail import Mail # <--- ¡PRIMERO IMPORTAMOS LA HERRAMIENTA MAIL!
import db_manager

app = Flask(__name__)
app.secret_key = 'clave_para_firmar_cookies'


# CONFIGURACIÓN PARA SUBIDA DE ARCHIVOS (IMÁGENES Y CVs)
UPLOAD_FOLDER_FOTOS = 'static/uploads'
UPLOAD_FOLDER_CVS = 'static/cvs'

# Separamos por seguridad las extensiones válidas para cada tipo
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOCUMENTS = {'pdf', 'png', 'jpg', 'jpeg'}  # Permite PDFs e imágenes para el CV

app.config['UPLOAD_FOLDER_FOTOS'] = UPLOAD_FOLDER_FOTOS
app.config['UPLOAD_FOLDER_CVS'] = UPLOAD_FOLDER_CVS

# Asegurar la existencia de ambas carpetas al iniciar el servidor
for carpeta in [UPLOAD_FOLDER_FOTOS, UPLOAD_FOLDER_CVS]:
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

# Funciones de validación independientes
def es_foto_permitida(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES

def es_cv_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENTS


def procesar_subida_foto(archivo_formulario, usuario_id):
    """
    Procesa, valida y guarda la foto de perfil en static/uploads.
    Devuelve el nombre seguro del archivo o None si no es válido.
    """
    if archivo_formulario and archivo_formulario.filename != '':
        if es_foto_permitida(archivo_formulario.filename):
            ext = archivo_formulario.filename.rsplit('.', 1)[1].lower()
            # Creamos un nombre único basado en el ID del usuario: ej. "perfil_5.png"
            nombre_archivo = f"perfil_{usuario_id}.{ext}"
            nombre_seguro = secure_filename(nombre_archivo)
            ruta_completa = os.path.join(app.config['UPLOAD_FOLDER_FOTOS'], nombre_seguro)
            archivo_formulario.save(ruta_completa)
            return nombre_seguro
    return None

def procesar_subida_cv(archivo_formulario, usuario_id):
    """
    Procesa, valida y guarda el currículum en static/cvs.
    Devuelve el nombre seguro del archivo o None si no es válido.
    """
    if archivo_formulario and archivo_formulario.filename != '':
        if es_cv_permitido(archivo_formulario.filename):
            ext = archivo_formulario.filename.rsplit('.', 1)[1].lower()
            # Creamos un nombre único basado en el ID del usuario: ej. "cv_5.pdf"
            nombre_archivo = f"cv_{usuario_id}.{ext}"
            nombre_seguro = secure_filename(nombre_archivo)
            ruta_completa = os.path.join(app.config['UPLOAD_FOLDER_CVS'], nombre_seguro)
            archivo_formulario.save(ruta_completa)
            return nombre_seguro
    return None



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = ''          # <--- Tu correo real de Gmail
app.config['MAIL_PASSWORD'] = '' # <--- Código de 16 letras de Google
app.config['MAIL_DEFAULT_SENDER'] = ('Bolsa de Empleo', '')# <--- Tu correo real de Gmail otravez

mail = Mail(app)
from mail_helper import enviar_correo_aceptacion, enviar_correo_recuperacion


@app.before_request
def vigilante_acceso():
    destino = request.endpoint
    if not destino or destino in ['static']: return

    rutas_publicas = ['index', 'login', 'registro', 'olvide_password', 'restablecer_password']
    token_cliente = session.get('user_token')
    
    # Buscamos al usuario en la base de datos
    usuario = db_manager.obtener_usuario_por_token(token_cliente) if token_cliente else None

    if token_cliente and not usuario:
        session.clear()
        token_cliente = None  # Reseteamos la variable local para los siguientes condicionales

    # 1. Si el usuario está logueado e intenta ir a Login/Registro, lo mandamos al Dashboard
    if usuario and destino in rutas_publicas:
        return redirect(url_for('dashboard'))

    # 2. Si el usuario NO está logueado e intenta ir a una ruta protegida, lo mandamos al Index
    if not usuario and destino not in rutas_publicas:
        return redirect(url_for('index'))


@app.context_processor
def inyectar_usuario():
    token_cliente = session.get('user_token')
    if token_cliente:
        usuario = db_manager.obtener_usuario_por_token(token_cliente)
        if usuario:
            return dict(usuario_actual=usuario)
    return dict(usuario_actual=None)


@app.route('/')
def index():
    return render_template('inicio.html')

def iniciar_sesion(user, pw):
    usuario_valido = db_manager.verificar_usuario(user, pw)    
    if usuario_valido:
        token = db_manager.asignar_nuevo_token(usuario_valido['id'])
        session['user_token'] = token
        session['user_nombre'] = usuario_valido['nombre']
        session['user_tipo'] = usuario_valido['tipo']
        session['user_id'] = usuario_valido['id'] 
        return True
    return False

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        user = request.form.get('usuario')
        email = request.form.get('email')
        pw = request.form.get('password')
        tipo = request.form.get('tipo', 'persona')
        
        # Validar obligatoriedad estricta del email en el backend
        if not email or not email.strip():
            return jsonify({"status": "error", "message": "El correo electrónico es estrictamente obligatorio"}), 400
        
        # Al registrarse pasamos el estatus 'Disponible' por defecto si es 'persona'
        estatus_inicial = 'Disponible' if tipo == 'persona' else None

        if db_manager.registrar_usuario(user, email, pw, tipo):
            if iniciar_sesion(user, pw):
                return jsonify({"status": "success", "redirect": url_for('dashboard')}), 200
        return jsonify({"status": "error", "message": "Registro fallido o usuario duplicado"}), 400
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Lógica de procesamiento de datos
        user = request.form.get('usuario')
        pw = request.form.get('password')
        if iniciar_sesion(user, pw):
            return jsonify({"status": "success", "redirect": url_for('dashboard')}), 200
        return jsonify({"status": "error", "message": "Credenciales incorrectas"}), 401
    
    # Si es GET, simplemente mostramos la página
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    
    if not usuario:
        return redirect(url_for('index'))

    # LOGICA PARA EMPRESAS INTEGRADA CON POSTULACIONES Y TASA DE CONTRATACIÓN
    if usuario['tipo'] == 'empresa':
        contactos = db_manager.obtener_contactos(usuario['id'])
        mis_vacantes = db_manager.obtener_mis_solicitudes(usuario['id'])
        
        # Calcular la tasa de contratación usando la lógica de la BD
        tasa_contratacion = db_manager.calcular_tasa_contratacion(usuario['id'])
        
        vacantes_con_postulados = []
        for v in mis_vacantes:
            vacante_dict = dict(v)
            vacante_dict['postulados'] = db_manager.obtener_postulados_por_vacante(v['id'])
            vacantes_con_postulados.append(vacante_dict)
            
        return render_template('dashboard_empresa.html', 
                               u=usuario, 
                               contactos=contactos, 
                               vacantes=vacantes_con_postulados,
                               tasa_contratacion=tasa_contratacion) # Pasamos la tasa al HTML
    
    # LÓGICA PARA PERSONAS
    experiencias = db_manager.obtener_experiencia(usuario['id'])
    educaciones = db_manager.obtener_educacion(usuario['id'])
    edad = "No definida"
    if usuario['fecha_nacimiento']:
        fecha_nac = date.fromisoformat(usuario['fecha_nacimiento'])
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    
    return render_template('dashboard.html', 
                           u=usuario, 
                           edad=edad, 
                           experiencias=experiencias, 
                           educaciones=educaciones)


@app.route('/perfil/editar', methods=['GET', 'POST'])
def editar_perfil():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)

    if request.method == 'POST':
        # 1. Procesar la foto de perfil usando el procesador independiente de la Fase 2
        nombre_archivo_foto = usuario['foto']
        if 'foto' in request.files:
            nueva_foto = procesar_subida_foto(request.files['foto'], usuario['id'])
            if nueva_foto:
                nombre_archivo_foto = nueva_foto

        # 2. Procesar el CV si el usuario es de tipo 'persona'
        nombre_archivo_cv = usuario.get('cv_ruta') # Mantiene el CV actual por defecto
        if usuario['tipo'] == 'persona' and 'cv' in request.files:
            nuevo_cv = procesar_subida_cv(request.files['cv'], usuario['id'])
            if nuevo_cv:
                nombre_archivo_cv = nuevo_cv

        # 3. Construcción del diccionario de datos recolectados
        datos = {
            'nombre_completo': request.form.get('nombre_completo'),
            'descripcion': request.form.get('descripcion'),
            'genero': request.form.get('genero'),
            'fecha_nacimiento': request.form.get('fecha_nacimiento'),
            'foto': nombre_archivo_foto,
            'estatus': request.form.get('estatus') if usuario['tipo'] == 'persona' else None,
            'cv_ruta': nombre_archivo_cv if usuario['tipo'] == 'persona' else None
        }
        
        if db_manager.actualizar_perfil(usuario['id'], datos):
            return redirect(url_for('dashboard'))
        return "Error al actualizar", 500

    if usuario['tipo'] == 'empresa':
        contactos = db_manager.obtener_contactos(usuario['id'])
        return render_template('editar_perfil_empresa.html', u=usuario, contactos=contactos)
    
    exps = db_manager.obtener_experiencia(usuario['id'])
    edus = db_manager.obtener_educacion(usuario['id'])
    return render_template('editar_perfil.html', u=usuario, experiencias=exps, educaciones=edus)


# --- RUTAS DE ACCIÓN (AGREGAR) ---

@app.route('/perfil/agregar_experiencia', methods=['POST'])
def ruta_agregar_experiencia():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    datos = request.json
    db_manager.agregar_experiencia(usuario['id'], datos['compania'], datos['puesto'], datos['ano'])
    return jsonify({"status": "success"})

@app.route('/perfil/agregar_educacion', methods=['POST'])
def ruta_agregar_educacion():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    datos = request.json
    db_manager.agregar_educacion(usuario['id'], datos['institucion'], datos['nivel'], datos['ano'])
    return jsonify({"status": "success"})

@app.route('/perfil/agregar_contacto', methods=['POST'])
def ruta_agregar_contacto():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    tipo_c = request.json.get('tipo_contacto')
    valor = request.json.get('valor')
    db_manager.agregar_contacto(usuario['id'], tipo_c, valor)
    return jsonify({"status": "success"})


# --- RUTAS DE ELIMINACIÓN ---

@app.route('/perfil/eliminar/<tabla>/<int:item_id>', methods=['POST'])
def ruta_eliminar_item(tabla, item_id):
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    tablas_permitidas = ['experiencia', 'educacion', 'contactos_empresa']
    
    actual_tabla = 'contactos_empresa' if tabla == 'contacto' else tabla

    if actual_tabla in tablas_permitidas:
        db_manager.eliminar_item(actual_tabla, item_id, usuario['id'])
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route('/logout')
def logout():
    token = session.get('user_token')
    if token:
        db_manager.borrar_token(token)
    session.clear()
    return redirect(url_for('index'))


# vacantes
@app.route('/perfil/gestionar_vacantes')
def gestionar_vacantes():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    
    if not usuario or usuario['tipo'] != 'empresa':
        return redirect(url_for('dashboard'))
    
    vacantes = db_manager.obtener_mis_solicitudes(usuario['id'])
    return render_template('crear_vacante.html', u=usuario, vacantes=vacantes)

@app.route('/solicitudes/crear', methods=['POST'])
def ruta_crear_solicitud():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)

    if not usuario or usuario['tipo'] != 'empresa':
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    # Capturar de manera obligatoria el salario económico
    pago_monto = request.form.get('pago_monto')
    pago_tipo = request.form.get('pago_tipo')

    if not pago_monto or not pago_tipo:
        return "Error: El monto de pago y el tipo de pago son campos obligatorios.", 400

    datos = {
        'titulo': request.form.get('titulo'),
        'descripcion': request.form.get('descripcion'),
        'modalidad': request.form.get('modalidad'),
        'edad_minima': int(request.form.get('edad_minima', 0)),
        'edad_maxima': int(request.form.get('edad_maxima', 99)),
        'nivel_educativo': request.form.get('nivel_educativo'),
        'lugar': request.form.get('lugar'),
        'pago_monto': float(pago_monto),
        'pago_tipo': pago_tipo
    }

    if db_manager.crear_solicitud(usuario['id'], datos):
        return redirect(url_for('dashboard'))
    return "Error al crear la vacante", 500


@app.route('/solicitudes/eliminar/<int:solicitud_id>', methods=['POST'])
def ruta_eliminar_solicitud(solicitud_id):
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    
    if usuario and usuario['tipo'] == 'empresa':
        db_manager.eliminar_solicitud(solicitud_id, usuario['id'])
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error"}), 403


# explorar vacantes pa
@app.route('/empleos/recomendados')
def empleos_recomendados():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)

    if not usuario or usuario['tipo'] != 'persona':
        return redirect(url_for('index'))

    edad_usuario = None
    if usuario['fecha_nacimiento']:
        fecha_nac = date.fromisoformat(usuario['fecha_nacimiento'])
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        edad_usuario = edad
    
    educacion = db_manager.obtener_educacion(usuario['id'])
    mis_niveles = list(set([edu['nivel'] for edu in educacion if edu['nivel'] and edu['nivel'] != "Sin-especificar"]))

    perfil_auto = {
        'edad': edad_usuario,
        'niveles_educativos': mis_niveles
    }

    vacantes = db_manager.obtener_solicitudes_busqueda(perfil_usuario=perfil_auto)
    mis_postulaciones = db_manager.obtener_vacantes_postuladas_por_usuario(usuario['id'])

    return render_template('empleos_recomendados.html', 
                           u=usuario, 
                           vacantes=vacantes, 
                           mis_postulaciones=mis_postulaciones)


@app.route('/empleos/buscar')
def empleos_buscar():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)

    query_texto = request.args.get('q', '').strip()
    modalidad_filtro = request.args.get('modalidad', '')
    
    # Capturamos los nuevos inputs del usuario
    pago_min = request.args.get('pago_min', '')
    pago_tipo = request.args.get('pago_tipo', '')

    mis_filtros = {
        'keyword': query_texto,
        'modalidad': modalidad_filtro,
        'pago_min': float(pago_min) if pago_min.replace('.', '', 1).isdigit() else None,
        'pago_tipo': pago_tipo if pago_tipo else None
    }

    vacantes = db_manager.obtener_solicitudes_busqueda(filtros=mis_filtros)

    return render_template('empleos_recomendados.html', 
                           u=usuario, 
                           vacantes=vacantes, 
                           busqueda_actual=query_texto,
                           modalidad_actual=modalidad_filtro,
                           pago_min_actual=pago_min,
                           pago_tipo_actual=pago_tipo)


@app.route('/@<username>')
def perfil_publico(username):
    perfil = db_manager.obtener_usuario_por_username(username)
    
    if not perfil:
        return "Usuario o empresa no encontrado", 404

    if perfil['tipo'] == 'empresa':
        contactos = db_manager.obtener_contactos(perfil['id'])
        vacantes = db_manager.obtener_mis_solicitudes(perfil['id'])
        
        return render_template('perfil_publico_empresa.html', 
                               perfil=perfil, 
                               contactos=contactos, 
                               vacantes=vacantes)

    elif perfil['tipo'] == 'persona':
        experiencias = db_manager.obtener_experiencia(perfil['id'])
        educaciones = db_manager.obtener_educacion(perfil['id'])
        
        edad = "No definida"
        if perfil['fecha_nacimiento']:
            fecha_nac = date.fromisoformat(perfil['fecha_nacimiento'])
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            
        return render_template('perfil_publico_persona.html', 
                               perfil=perfil, 
                               edad=edad, 
                               experiencias=experiencias, 
                               educaciones=educaciones)


# --- RUTA: Procesar la postulación ---
@app.route('/postular/<int:vacante_id>', methods=['POST'])
def postular(vacante_id):
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    
    if not usuario or usuario['tipo'] != 'persona':
        return redirect(url_for('index'))
        
    db_manager.registrar_postulacion(usuario['id'], vacante_id)
    return redirect(request.referrer or url_for('empleos_recomendados'))


@app.route('/empresa/gestionar_postulacion/<int:id>/<accion>', methods=['POST'])
def gestionar_postulacion(id, accion):
    if session.get('user_tipo') != 'empresa': return "No autorizado", 403 
    
    nuevo_estado = 'Aceptado' if accion == 'aceptar' else 'Rechazado'
    exito = db_manager.actualizar_estado_postulacion(id, session['user_id'], nuevo_estado)
    
    if exito:
        # === DISPARADOR DE CORREO EN CASO DE ACEPTACIÓN ===
        if accion == 'aceptar':
            datos_postulacion = db_manager.obtener_detalle_postulacion(id)
            if datos_postulacion:
                # Si el usuario no configuró su 'nombre_completo' usamos su 'username' por defecto
                nombre_destino = datos_postulacion['nombre_usuario'] or "Postulante"
                
                enviar_correo_aceptacion(
                    email_destino=datos_postulacion['email'],
                    nombre_usuario=nombre_destino,
                    nombre_vacante=datos_postulacion['titulo_vacante'],
                    nombre_empresa=session.get('user_nombre', 'La Empresa')
                )
        # ==================================================
        return jsonify({"mensaje": "Estado actualizado"}), 200
    return jsonify({"error": "No se pudo actualizar"}), 400


# --- RUTA: Ver postulaciones de un usuario persona (CORREGIDA) ---
@app.route('/mis_postulaciones')
def mis_postulaciones():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    if not usuario or usuario['tipo'] != 'persona':
        return redirect(url_for('index'))
        
    # 1. Conseguimos todas las ofertas laborales del sistema
    todas_las_vacantes = db_manager.obtener_solicitudes_busqueda()
    
    # 2. Conseguimos los IDs de las vacantes a las que se postuló este usuario
    ids_mis_postulaciones = db_manager.obtener_vacantes_postuladas_por_usuario(usuario['id'])
    
    # 3. Filtramos para quedarnos solo con las tarjetas que le corresponden y les inyectamos su estado real
    mis_procesos = []
    for v in todas_las_vacantes:
        if v['id'] in ids_mis_postulaciones:
            vacante_dict = dict(v)
            
            # Buscamos el estado específico de esta postulación en la base de datos
            conn = db_manager.conectar()
            postulacion = conn.execute(
                "SELECT id, estado FROM postulaciones WHERE usuario_id = ? AND vacante_id = ?", 
                (usuario['id'], v['id'])
            ).fetchone()
            conn.close()
            
            if postulacion:
                vacante_dict['postulacion_id'] = postulacion['id']
                vacante_dict['estado_tramite'] = postulacion['estado']
                mis_procesos.append(vacante_dict)
                
    return render_template('mis_postulaciones.html', u=usuario, vacantes=mis_procesos)


# --- RUTA: Ofertas de trabajo (Panel exclusivo de administración) ---
@app.route('/empresa/ofertas_trabajo', methods=['GET'])
def ofertas_trabajo():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    
    # Validación limpia: si no hay usuario en BD o no es tipo empresa, directo al index
    if not usuario or usuario['tipo'] != 'empresa': 
        return redirect(url_for('index'))
    
    # Conseguimos las vacantes para listarlas en la administración
    mis_vacantes = db_manager.obtener_mis_solicitudes(usuario['id'])
    return render_template('ofertas_trabajo.html', u=usuario, vacantes=mis_vacantes)


# --- RUTA: Postulantes globales de la empresa ---
@app.route('/empresa/postulantes', methods=['GET'])
def lista_postulantes_empresa():
    token = session.get('user_token')
    usuario = db_manager.obtener_usuario_por_token(token)
    
    # Validación limpia e idéntica utilizando el campo 'tipo' de la BD
    if not usuario or usuario['tipo'] != 'empresa':
        return redirect(url_for('index'))
    
    # Estructuramos el árbol de vacantes con sus postulados correspondientes
    mis_vacantes = db_manager.obtener_mis_solicitudes(usuario['id'])
    vacantes_con_postulados = []
    for v in mis_vacantes:
        vacante_dict = dict(v)
        vacante_dict['postulados'] = db_manager.obtener_postulados_por_vacante(v['id'])
        vacantes_con_postulados.append(vacante_dict)
        
    return render_template('postulantes.html', u=usuario, vacantes=vacantes_con_postulados)




# 1. Ruta que procesa el formulario de "Olvidé mi contraseña"
@app.route('/olvide_password', methods=['GET', 'POST'])
def olvide_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Buscamos en tu db_manager si el usuario existe por su email
        usuario = db_manager.obtener_usuario_por_email(email) # Asegúrate de tener esta función en tu DB
        
        if usuario:
            enviar_correo_recuperacion(usuario['email'], usuario['id'])
            
        # Mensaje ambiguo por seguridad, para que no adivinen correos existentes
        return render_template('login.html', mensaje="Si el correo es correcto, recibirás instrucciones en breve.")
    return render_template('olvide_password.html') # Tu vista con un input para el email


# 2. Ruta a la que llegará el usuario desde su celular al hacer clic en el correo
@app.route('/restablecer-password/<token>', methods=['GET', 'POST'])
def restablecer_password(token):
    from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    
    try:
        # El token expira en 1800 segundos (30 minutos)
        usuario_id = serializer.loads(token, salt='recuperar-password-salt', max_age=1800)
    except (SignatureExpired, BadTimeSignature):
        return "El enlace ha expirado o es inválido. Por favor, solicita uno nuevo.", 400

    if request.method == 'POST':
        nueva_pw = request.form.get('password')
        
        # Actualizamos la contraseña en la base de datos usando tu db_manager
        # Recuerda encriptarla en tu db_manager tal como haces en el registro
        if db_manager.actualizar_password_usuario(usuario_id, nueva_pw):
            return redirect(url_for('login'))
        return "Error al actualizar la contraseña.", 500
        
    return render_template('restablecer_password.html', token=token)


if __name__ == '__main__':
    db_manager.inicializar_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
