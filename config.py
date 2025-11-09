import os
import sys
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# --- Cargar y validar TOKEN ---
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("Error: 'TOKEN' no está definido en el archivo .env", file=sys.stderr)
    print("Por favor, copia y pega el token de tu bot en .env", file=sys.stderr)
    sys.exit(1) # Detiene el script

# --- Cargar y validar ID_DEL_SERVIDOR ---
ID_DEL_SERVIDOR_STR = os.getenv("ID_DEL_SERVIDOR")
if not ID_DEL_SERVIDOR_STR:
    print("Error: 'ID_DEL_SERVIDOR' no está definido en el archivo .env", file=sys.stderr)
    print("Por favor, copia y pega el ID de tu servidor en .env", file=sys.stderr)
    sys.exit(1)
try:
    ID_DEL_SERVIDOR = int(ID_DEL_SERVIDOR_STR)
except ValueError:
    print(f"Error: 'ID_DEL_SERVIDOR' ({ID_DEL_SERVIDOR_STR}) no es un número válido en .env", file=sys.stderr)
    sys.exit(1)

# --- Cargar y validar ID_DEL_OWNER ---
ID_DEL_OWNER_STR = os.getenv("ID_DEL_OWNER")
if not ID_DEL_OWNER_STR:
    print("Error: 'ID_DEL_OWNER' no está definido en el archivo .env", file=sys.stderr)
    print("Por favor, copia y pega tu ID de usuario en .env", file=sys.stderr)
    sys.exit(1)
try:
    ID_DEL_OWNER = int(ID_DEL_OWNER_STR)
except ValueError:
    print(f"Error: 'ID_DEL_OWNER' ({ID_DEL_OWNER_STR}) no es un número válido en .env", file=sys.stderr)
    sys.exit(1)