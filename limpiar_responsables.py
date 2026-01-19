"""
Script para limpiar y estandarizar nombres de responsables
"""
import csv
import re
from collections import defaultdict

# Prefijos profesionales a eliminar
PREFIJOS = [
    r'^ABOG\.\s*',
    r'^DR\.\s*',
    r'^DRA\.\s*',
    r'^LIC\.\s*',
    r'^LIC\.ADM\.\s*',
    r'^ING\.\s*',
    r'^CPC\.\s*',
    r'^PROF\.\s*',
    r'^MG\.\s*',
    r'^PSIC\.\s*',
]

def limpiar_nombre(nombre):
    """Limpia un nombre eliminando prefijos y normalizando formato"""
    if not nombre:
        return nombre
    
    nombre_limpio = nombre.strip()
    
    # Eliminar comillas si las tiene
    nombre_limpio = nombre_limpio.strip('"')
    
    # Eliminar prefijos profesionales (case insensitive)
    for prefijo in PREFIJOS:
        nombre_limpio = re.sub(prefijo, '', nombre_limpio, flags=re.IGNORECASE)
    
    # Limpiar espacios múltiples
    nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio).strip()
    
    # Eliminar comas al inicio o final
    nombre_limpio = nombre_limpio.strip(',').strip()
    
    return nombre_limpio

def detectar_formato(nombre):
    """
    Detecta si el nombre está en formato:
    - 'APELLIDO, NOMBRE' (tiene coma)
    - 'APELLIDO NOMBRE' o 'NOMBRE APELLIDO' (sin coma, difícil distinguir)
    """
    if ',' in nombre:
        return 'CON_COMA'
    return 'SIN_COMA'

def normalizar_a_nombres_apellidos(nombre):
    """
    Normaliza al formato: NOMBRES APELLIDOS
    """
    nombre = limpiar_nombre(nombre)
    
    if not nombre:
        return nombre
    
    # Si tiene coma, asumir formato "APELLIDO, NOMBRE" y convertir a "NOMBRE APELLIDO"
    if ',' in nombre:
        partes = nombre.split(',', 1)
        apellidos = partes[0].strip()
        nombres = partes[1].strip() if len(partes) > 1 else ''
        if nombres:
            return f"{nombres} {apellidos}"
        return apellidos
    
    # Si no tiene coma, dejamos como está (ya podría estar en formato correcto)
    return nombre

def analizar_responsables():
    """Analiza y genera propuestas de limpieza"""
    
    resultados = []
    
    with open('responsables.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original = row['responsable']
            limpio = limpiar_nombre(original)
            formato = detectar_formato(original)
            
            # Detectar si es un código/entidad especial (no es nombre de persona)
            es_especial = any(keyword in original.upper() for keyword in ['PEA', 'PELA', 'PPTCD', 'DGA', 'PATRIMONIO', 'PIRDAIS'])
            
            # Generar nombre propuesto
            if es_especial:
                nombre_propuesto = original  # Mantener entidades como están
            else:
                nombre_propuesto = normalizar_a_nombres_apellidos(original)
            
            resultados.append({
                'original': original,
                'sin_prefijo': limpio,
                'formato_detectado': formato,
                'es_entidad': 'SI' if es_especial else 'NO',
                'nombre_propuesto': nombre_propuesto
            })
    
    # Guardar análisis
    with open('responsables_analisis.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['original', 'sin_prefijo', 'formato_detectado', 'es_entidad', 'nombre_propuesto']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)
    
    # Estadísticas
    con_coma = sum(1 for r in resultados if r['formato_detectado'] == 'CON_COMA')
    sin_coma = sum(1 for r in resultados if r['formato_detectado'] == 'SIN_COMA')
    entidades = sum(1 for r in resultados if r['es_entidad'] == 'SI')
    con_prefijo = sum(1 for r in resultados if r['original'] != r['sin_prefijo'])
    
    print("=" * 60)
    print("📊 ANÁLISIS DE RESPONSABLES")
    print("=" * 60)
    print(f"Total de registros: {len(resultados)}")
    print(f"Con coma (formato APELLIDO, NOMBRE): {con_coma}")
    print(f"Sin coma (requiere revisión): {sin_coma}")
    print(f"Entidades/Códigos especiales: {entidades}")
    print(f"Con prefijo profesional: {con_prefijo}")
    print("=" * 60)
    print(f"✅ Archivo generado: 'responsables_analisis.csv'")
    print("\nRevisa el archivo y edita la columna 'nombre_propuesto' con los valores correctos.")
    
    return resultados

if __name__ == "__main__":
    analizar_responsables()
