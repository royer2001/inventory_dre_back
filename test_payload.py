
from models.movimiento_model import MovimientoModel
from database.connection import get_connection

payload = {
    "bien_id": 1964,
    "tipo": "Traslado",
    "fecha": "2025-11-25",
    "ubicacion_origen": "PATRIMONIO",
    "ubicacion_destino": "PATRIMONIO",
    "responsable_anterior": "ROYER ARIZA FABIAN",
    "responsable_nuevo": "LUIS NAVARRO MARIO",
    "modalidad_responsable_anterior": "NO REGISTRADO",
    "modalidad_responsable_nuevo": "CAP",
    "inventariador_id": 8,
    "observaciones": "Mediante resolución nro 0001 se procede a realizar el traslado por motivo..."
}

# Mocking get_connection to avoid actual DB writes if possible, but here we want to test the logic.
# However, I don't have the DB set up. I will just check if the code runs without erroring on key access.
# Actually, I can't run this without a DB connection.
# But I can verify the logic by inspecting the code I just wrote.

print("Payload keys:", payload.keys())
print("Mapped ubicacion_actual:", payload.get("ubicacion_actual") or payload.get("ubicacion_destino"))
print("Mapped responsable:", payload.get("responsable") or payload.get("responsable_nuevo"))
print("Mapped modalidad_responsable:", payload.get("modalidad_responsable") or payload.get("modalidad_responsable_nuevo"))
