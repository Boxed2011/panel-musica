// -----------------------------
// Configuración
// -----------------------------
const API_URL = "https://panel-musica.onrender.com"; // Cambia esto por la URL pública de tu servicio en Render
const API_KEY = "Zyn0rX ツ 0124"; // Debe coincidir con la API_KEY_SECRETA que pusiste en panel_api.py y Render

// -----------------------------
// Elementos del DOM
// -----------------------------
const guildInput = document.getElementById("guild_id");
const userInput = document.getElementById("user_id");
const queryInput = document.getElementById("query");
const playButton = document.getElementById("play_button");
const statusBox = document.getElementById("status");

// -----------------------------
// Función para reproducir
// -----------------------------
async function reproducir() {
    const guild_id = guildInput.value.trim();
    const user_id = userInput.value.trim();
    const query = queryInput.value.trim();

    if (!guild_id || !user_id || !query) {
        statusBox.textContent = "⚠️ Completa todos los campos.";
        return;
    }

    statusBox.textContent = "🔄 Conectando al bot...";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": API_KEY
            },
            body: JSON.stringify({
                guild_id: guild_id,
                user_id: user_id,
                query: query
            })
        });

        const data = await response.json();

        if (response.ok) {
            statusBox.textContent = `✅ ${data.message}`;
        } else {
            statusBox.textContent = `❌ Error: ${data.error}`;
        }
    } catch (err) {
        console.error(err);
        statusBox.textContent = "❌ No se pudo conectar al bot.";
    }
}

// -----------------------------
// Evento del botón
// -----------------------------
playButton.addEventListener("click", reproducir);
