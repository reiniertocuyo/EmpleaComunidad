// Esperamos a que el HTML esté totalmente cargado
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            // 1. EVITAR QUE LA PAGINA SE RECARGUE
            e.preventDefault();

            // 2. RECOGER LOS DATOS DEL FORMULARIO
            const formData = new FormData(loginForm);

            // 3. ENVIAR LOS DATOS A FLASK POR "DETRÁS" (AJAX)
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    // Si Flask dice que todo está bien, vamos al dashboard
                    window.location.href = result.redirect;
                } else {
                    // SI HAY ERROR: Mostramos el mensaje emergente del navegador
                    // Puedes cambiar alert() por algo más bonito luego
                    alert("Error de inicio de sesión: " + result.message);
                }
            } catch (error) {
                alert("Ocurrió un error en la conexión.");
            }
        });
    }
});