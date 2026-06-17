import os
from flask import render_template, current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

def _obtener_mail_instancia():
    """Función auxiliar interna para recuperar la extensión de correo de forma segura."""
    try:
        return current_app.extensions['mail']
    except RuntimeError:
        # Si ocurre un RuntimeError es porque estamos en un hilo secundario sin contexto explícito.
        # En ese caso, requerimos que la app o la extensión se manejen mediante el 'with app_context' que configuramos en app.py
        raise RuntimeError(
            "No se pudo acceder al contexto de Flask. "
            "Asegúrate de envolver esta llamada en 'with app.app_context():' si estás usando hilos."
        )

# Función 1: Enviar correo de aceptación de vacante
def enviar_correo_aceptacion(email_destino, nombre_usuario, nombre_vacante, nombre_empresa):
    try:
        mail = _obtener_mail_instancia()
        msg = Message(
            subject=f"¡Felicidades! Has sido aceptado en la vacante: {nombre_vacante}",
            recipients=[email_destino]
        )
        
        msg.html = render_template(
            'email_vacante.html', 
            usuario=nombre_usuario, 
            vacante=nombre_vacante, 
            empresa=nombre_empresa
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo de vacante: {e}")
        return False


# Función 2: Enviar correo de recuperación de contraseña
def enviar_correo_recuperacion(email_destino, id_usuario):
    try:
        mail = _obtener_mail_instancia()
        # Usamos el SECRET_KEY desde la configuración de la app activa
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(id_usuario, salt='recuperar-password-salt')
        
        # Si la app está en Render usará la URL real; si estás en tu PC usará localhost
        dominio_app = os.environ.get('APP_URL', 'http://127.0.0.1:5000')
        enlace_recuperacion = f"{dominio_app}/restablecer-password/{token}"
        
        msg = Message(
            subject="Recuperación de contraseña - Bolsa de Empleo",
            recipients=[email_destino]
        )
        
        msg.html = render_template(
            'email_password.html', 
            enlace=enlace_recuperacion
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo de recuperación: {e}")
        return False


# Función 3: Enviar correo de notificación de nuevo mensaje interno
def enviar_correo_nuevo_mensaje(email_destino, nombre_remitente, asunto_mensaje, contenido_mensaje):
    try:
        mail = _obtener_mail_instancia()
        # Obtenemos la URL para el botón de "Iniciar sesión"
        dominio_app = os.environ.get('APP_URL', 'http://127.0.0.1:5000')
        enlace_login = f"{dominio_app}/login"
        
        msg = Message(
            subject=f"Tienes un nuevo mensaje interno de: {nombre_remitente}",
            recipients=[email_destino]
        )
        
        # Renderizamos la plantilla HTML para este correo
        msg.html = render_template(
            'email_nuevo_mensaje.html', 
            remitente=nombre_remitente, 
            asunto=asunto_mensaje, 
            contenido=contenido_mensaje,
            enlace=enlace_login
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo de notificación de mensaje: {e}")
        return False