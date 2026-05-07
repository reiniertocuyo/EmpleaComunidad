document.addEventListener('DOMContentLoaded', () => {
    const formulario = document.getElementById('formRegistro');
    const usuarioInput = document.getElementById('usuario');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');

    // --- MEJORA DE UX: LIMPIEZA EN TIEMPO REAL ---
    usuarioInput.addEventListener('input', () => {
        usuarioInput.value = usuarioInput.value.toLowerCase().replace(/[^a-z0-9]/g, '');
    });

    const validarFormatoEmail = (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    };

    formulario.addEventListener('submit', (evento) => {
        evento.preventDefault(); // Detenemos siempre el envío tradicional
        
        let hayErrores = false;

        // Limpiar errores previos
        document.getElementById('errorUsuario').textContent = '';
        document.getElementById('errorEmail').textContent = '';
        document.getElementById('errorPassword').textContent = '';

        // Validaciones de Front-end
        if (usuarioInput.value.length < 3) {
            document.getElementById('errorUsuario').textContent = 'El usuario es muy corto.';
            hayErrores = true;
        }

        if (!validarFormatoEmail(emailInput.value)) {
            document.getElementById('errorEmail').textContent = 'Email no válido.';
            hayErrores = true;
        }

        if (passwordInput.value.length < 6) {
            document.getElementById('errorPassword').textContent = 'Mínimo 6 caracteres.';
            hayErrores = true;
        } else if (passwordInput.value !== confirmPasswordInput.value) {
            document.getElementById('errorPassword').textContent = 'No coinciden.';
            hayErrores = true;
        }

        if (!hayErrores) {
            // FormData captura automáticamente el 'tipo' (persona/empresa) 
            // porque tiene el atributo name="tipo" en el HTML.
            const formData = new FormData(formulario);
            
            fetch('/registro', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = data.redirect;
                } else {
                    // Si el servidor dice que el email ya existe, por ejemplo:
                    alert(data.message);
                }
            })
            .catch(err => {
                console.error("Error en la petición:", err);
                alert("Ocurrió un error en el servidor.");
            });
        }
    });
});