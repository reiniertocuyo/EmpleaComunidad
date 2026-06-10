from flask import render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

# Función 1: Enviar correo de aceptación de vacante
def enviar_correo_aceptacion(email_destino, nombre_usuario, nombre_vacante, nombre_empresa):
    # Importamos 'mail' desde app en el momento exacto de usarlo para evitar errores circulares
    from app import mail 
    try:
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

# Modifica la Función 2 en mail_helper.py para que quede así:
def enviar_correo_recuperacion(email_destino, id_usuario):
    from app import app, mail 
    import os  # <-- Importamos os para leer la URL de Render
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
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
    from app import app, mail 
    import os
    try:
        # Obtenemos la URL para el botón de "Iniciar sesión"
        dominio_app = os.environ.get('APP_URL', 'http://127.0.0.1:5000')
        enlace_login = f"{dominio_app}/login"
        
        msg = Message(
            subject=f"Tienes un nuevo mensaje interno de: {nombre_remitente}",
            recipients=[email_destino]
        )
        
        # Renderizamos una nueva plantilla HTML para este correo
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