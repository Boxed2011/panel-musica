// Cambia esto a la URL de tu app en Render
const BOT_API_URL = "https://tu-app.onrender.com";
const API_KEY = "Zyn0rX ツ 0124";

const playButton = document.getElementById('play-button');
const guildIdInput = document.getElementById('guild-id');
const userIdInput = document.getElementById('user-id');
const songQueryInput = document.getElementById('song-query');
const statusElement = document.getElementById('status');

playButton.addEventListener('click', async () => {
    const guildId = guildIdInput.value;
    const userId = userIdInput.value;
    const query = songQueryInput.value;

    if (!guildId || !userId || !query) {
        statusElement.textContent = "Error: Rellena todos los campos.";
        return;
    }
    statusElement.textContent = "Enviando orden...";
    try {
        const response = await fetch(`${BOT_API_URL}/play`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': API_KEY },
            body: JSON.stringify({ guild_id: guildId, user_id: userId, query: query })
        });
        const result = await response.json();
        if (response.ok) {
            statusElement.textContent = `Éxito: ${result.message}`;
        } else {
            statusElement.textContent = `Error: ${result.error || 'Error desconocido'}`;
        }
    } catch (error) {
        statusElement.textContent = "Error: No se pudo conectar al bot.";
    }
});
