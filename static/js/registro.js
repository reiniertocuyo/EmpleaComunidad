document.addEventListener('DOMContentLoaded', () => {
    const formulario = document.getElementById('formRegistro');
    const usuarioInput = document.getElementById('usuario');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');

    // --- MEJORA DE UX: LIMPIEZA EN TIEMPO REAL ---
    usuarioInput.addEventListener('input', () => {
        // Convierte a minúscula y elimina cualquier cosa que no sea a-z o 0-9
        usuarioInput.value = usuarioInput.value.toLowerCase().replace(/[^a-z0-9]/g, '');
    });

    // Función de validación para el submit
    const validarFormatoEmail = (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    };

    formulario.addEventListener('submit', (evento) => {
        let hayErrores = false;

        // Limpiar errores previos
        document.getElementById('errorUsuario').textContent = '';
        document.getElementById('errorEmail').textContent = '';
        document.getElementById('errorPassword').textContent = '';

        // Validar Usuario (por si acaso pegan texto con símbolos)
        if (usuarioInput.value.length < 3) {
            document.getElementById('errorUsuario').textContent = 'El usuario es muy corto.';
            hayErrores = true;
        }

        // Validar Email
        if (!validarFormatoEmail(emailInput.value)) {
            document.getElementById('errorEmail').textContent = 'Email no válido.';
            hayErrores = true;
        }

        // Validar Password
        if (passwordInput.value.length < 6) {
            document.getElementById('errorPassword').textContent = 'Mínimo 6 caracteres.';
            hayErrores = true;
        } else if (passwordInput.value !== confirmPasswordInput.value) {
            document.getElementById('errorPassword').textContent = 'No coinciden.';
            hayErrores = true;
        }

        if (hayErrores) {
            evento.preventDefault();
        } else {
            evento.preventDefault();
            const formData = new FormData(formulario);
            fetch('/registro', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') window.location.href = data.redirect;
                else alert(data.message);
            });
        }
    });
});