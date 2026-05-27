document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usuarioInput = document.getElementById('usuario');

    // --- NUEVA MEJORA: LIMPIEZA EN TIEMPO REAL ---
    if (usuarioInput) {
        usuarioInput.addEventListener('input', () => {
            // Convierte a minúsculas y elimina cualquier carácter que no sea a-z o 0-9
            usuarioInput.value = usuarioInput.value.toLowerCase().replace(/[^a-z0-9]/g, '');
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // La validación del submit sigue siendo útil como doble seguridad, 
            // aunque con el 'input' de arriba, el usuario ya no podrá escribir caracteres prohibidos.
            const patron = /^[a-z0-9]+$/;
            if (!patron.test(usuarioInput.value)) {
                alert("Usuario no válido.");
                return;
            }

            const formData = new FormData(loginForm);

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    window.location.href = result.redirect;
                } else {
                    alert("Error: " + result.message);
                }
            } catch (error) {
                alert("Error de conexión.");
            }
        });
    }
});