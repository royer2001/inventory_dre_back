"""
Script para exportar la columna 'responsable' de la tabla movimientos a CSV
"""
import csv
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from database.connection import get_connection

def export_responsables():
    conn = get_connection()
    
    with conn.cursor() as cursor:
        # Obtener todos los responsables únicos de la tabla movimientos
        cursor.execute("""
            SELECT DISTINCT responsable 
            FROM movimientos 
            WHERE responsable IS NOT NULL 
            AND responsable != ''
            ORDER BY responsable ASC
        """)
        result = cursor.fetchall()
    
    conn.close()
    
    # Exportar a CSV
    output_file = 'responsables.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['responsable'])  # Header
        for row in result:
            writer.writerow([row['responsable']])
    
    print(f"✅ Exportados {len(result)} responsables únicos a '{output_file}'")
    return output_file

if __name__ == "__main__":
    export_responsables()
