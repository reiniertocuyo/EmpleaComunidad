// Esperamos a que todo el HTML cargue
document.addEventListener('DOMContentLoaded', () => {
    const formulario = document.getElementById('formRegistro');
    
    // Obtenemos referencias a los inputs
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');

    // Obtenemos referencias a los lugares donde mostraremos errores
    const errorEmail = document.getElementById('errorEmail');
    const errorPassword = document.getElementById('errorPassword');

    // Función para validar formato de email (Expresión Regular estándar)
    const validarFormatoEmail = (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    };

    // Escuchamos cuando se intente enviar el formulario
    formulario.addEventListener('submit', (evento) => {
        let hayErrores = false;

        // Limpiamos errores previos
        errorEmail.textContent = '';
        errorPassword.textContent = '';
        emailInput.style.borderColor = '';
        passwordInput.style.borderColor = '';
        confirmPasswordInput.style.borderColor = '';

        // --- VALIDACION DE EMAIL ---
        if (!validarFormatoEmail(emailInput.value)) {
            errorEmail.textContent = 'Por favor, introduce un correo electrónico válido.';
            emailInput.style.borderColor = 'red';
            hayErrores = true;
        }

        // --- VALIDACION DE CONTRASEÑA ---
        // 1. Validar longitud (ej: minimo 6 caracteres)
        if (passwordInput.value.length < 6) {
            errorPassword.textContent = 'La contraseña debe tener al menos 6 caracteres.';
            passwordInput.style.borderColor = 'red';
            hayErrores = true;
        } 
        // 2. Validar que coincidan (solo si la longitud es correcta para no acumular errores)
        else if (passwordInput.value !== confirmPasswordInput.value) {
            errorPassword.textContent = 'Las contraseñas no coinciden.';
            passwordInput.style.borderColor = 'red';
            confirmPasswordInput.style.borderColor = 'red';
            hayErrores = true;
        }

        // Si detectamos cualquier error, detenemos el envío
        if (hayErrores) {
            evento.preventDefault(); // IMPORTANTE: Evita que el formulario se envíe a Flask
        }
    });
});