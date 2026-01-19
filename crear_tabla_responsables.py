"""
Script para modificar la tabla 'responsables' existente y agregar los datos normalizados
"""
import csv
import re
from dotenv import load_dotenv

load_dotenv()

from database.connection import get_connection

# Prefijos profesionales a eliminar
PREFIJOS = [
    r'^ABOG\.\s*',
    r'^DR\.\s*',
    r'^DRA\.\s*',
    r'^LIC\.\s*',
    r'^LIC\.ADM\.\s*',
    r'^ADM\.\s*',
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
    nombre_limpio = nombre_limpio.strip('"')
    
    # Eliminar prefijos profesionales (case insensitive)
    for prefijo in PREFIJOS:
        nombre_limpio = re.sub(prefijo, '', nombre_limpio, flags=re.IGNORECASE)
    
    # Limpiar espacios múltiples
    nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio).strip()
    nombre_limpio = nombre_limpio.strip(',').strip()
    
    # Eliminar puntos finales
    nombre_limpio = nombre_limpio.rstrip('.')
    
    return nombre_limpio

def normalizar_a_nombres_apellidos(nombre):
    """Normaliza al formato: NOMBRES APELLIDOS"""
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
    
    return nombre

def es_entidad_especial(nombre):
    """Detecta si es un código/entidad especial (no es nombre de persona)"""
    keywords = ['PEA', 'PELA', 'PPTCD', 'DGA', 'PATRIMONIO', 'PIRDAIS', 'COORDINADORA']
    return any(keyword in nombre.upper() for keyword in keywords)

def modificar_estructura_tabla():
    """Modifica la estructura de la tabla responsables"""
    conn = get_connection()
    
    print("🔧 Modificando estructura de la tabla 'responsables'...")
    
    with conn.cursor() as cursor:
        # Desactivar comprobación de claves foráneas temporalmente
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 1. Vaciar la tabla
        cursor.execute("DELETE FROM responsables")
        print("   ✓ Tabla vaciada")
        
        # 2. Eliminar columnas que no se necesitan
        columnas_a_eliminar = ['nombre', 'cargo', 'centro_costo', 'correo', 'telefono']
        
        for col in columnas_a_eliminar:
            try:
                cursor.execute(f"ALTER TABLE responsables DROP COLUMN {col}")
                print(f"   ✓ Columna '{col}' eliminada")
            except Exception as e:
                if "check that column/key exists" in str(e) or "Unknown column" in str(e):
                    print(f"   ⚠ Columna '{col}' no existe, saltando...")
                else:
                    print(f"   ❌ Error eliminando '{col}': {e}")
        
        conn.commit()
        
        # 3. Agregar nuevas columnas
        nuevas_columnas = [
            ("nombre_original", "VARCHAR(255) NOT NULL"),
            ("nombre_normalizado", "VARCHAR(255) NOT NULL"),
        ]
        
        for col_name, col_def in nuevas_columnas:
            try:
                cursor.execute(f"ALTER TABLE responsables ADD COLUMN {col_name} {col_def}")
                print(f"   ✓ Columna '{col_name}' agregada")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"   ⚠ Columna '{col_name}' ya existe")
                else:
                    print(f"   ❌ Error agregando '{col_name}': {e}")
        
        # 4. Agregar índice único para nombre_original
        try:
            cursor.execute("ALTER TABLE responsables ADD UNIQUE INDEX idx_nombre_original (nombre_original)")
            print("   ✓ Índice único agregado para 'nombre_original'")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print("   ⚠ Índice ya existe")
            else:
                print(f"   ⚠ Índice: {e}")
        
        # 5. Agregar índice para nombre_normalizado
        try:
            cursor.execute("ALTER TABLE responsables ADD INDEX idx_nombre_normalizado (nombre_normalizado)")
            print("   ✓ Índice agregado para 'nombre_normalizado'")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print("   ⚠ Índice ya existe")
            else:
                print(f"   ⚠ Índice: {e}")
        
        conn.commit()
        
        # Reactivar comprobación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    conn.close()
    print("✅ Estructura de tabla modificada exitosamente\n")

def verificar_estructura():
    """Verifica la estructura final de la tabla"""
    conn = get_connection()
    
    with conn.cursor() as cursor:
        cursor.execute("DESCRIBE responsables")
        columnas = cursor.fetchall()
    
    conn.close()
    
    print("📋 Estructura actual de la tabla 'responsables':")
    for col in columnas:
        print(f"   - {col['Field']}: {col['Type']} (NULL: {col['Null']}, Key: {col['Key']})")
    print()
    
    return columnas

def insertar_responsables():
    """Lee los responsables únicos de movimientos e inserta en la tabla"""
    conn = get_connection()
    
    # Obtener todos los responsables únicos de la tabla movimientos
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT responsable 
            FROM movimientos 
            WHERE responsable IS NOT NULL 
            AND responsable != ''
            ORDER BY responsable ASC
        """)
        responsables_originales = [row['responsable'] for row in cursor.fetchall()]
    
    print(f"📋 Se encontraron {len(responsables_originales)} responsables únicos en movimientos")
    
    # Procesar y agrupar por nombre normalizado para detectar duplicados
    mapeo = {}  # nombre_normalizado -> [nombres_originales]
    
    for original in responsables_originales:
        es_entidad = es_entidad_especial(original)
        
        if es_entidad:
            normalizado = limpiar_nombre(original)  # Solo limpiar, no invertir
        else:
            normalizado = normalizar_a_nombres_apellidos(original)
        
        if normalizado not in mapeo:
            mapeo[normalizado] = []
        mapeo[normalizado].append(original)
    
    # Detectar duplicados potenciales
    duplicados = {k: v for k, v in mapeo.items() if len(v) > 1}
    
    if duplicados:
        print("\n⚠️  DUPLICADOS POTENCIALES DETECTADOS:")
        for nombre_norm, originales in duplicados.items():
            print(f"   '{nombre_norm}' <- {originales}")
    
    # Insertar en la tabla
    insertados = 0
    errores = 0
    
    with conn.cursor() as cursor:
        for original in responsables_originales:
            es_entidad = es_entidad_especial(original)
            
            if es_entidad:
                normalizado = limpiar_nombre(original)
            else:
                normalizado = normalizar_a_nombres_apellidos(original)
            
            try:
                cursor.execute("""
                    INSERT INTO responsables (nombre_original, nombre_normalizado, activo)
                    VALUES (%s, %s, TRUE)
                """, (original, normalizado))
                insertados += 1
                    
            except Exception as e:
                errores += 1
                print(f"❌ Error insertando '{original}': {e}")
        
        conn.commit()
    
    conn.close()
    
    print(f"\n✅ Inserción completada:")
    print(f"   - Insertados: {insertados}")
    print(f"   - Errores: {errores}")
    print(f"   - Duplicados potenciales (mismo nombre normalizado): {len(duplicados)}")
    
    return mapeo, duplicados

def mostrar_resumen():
    """Muestra un resumen de la tabla"""
    conn = get_connection()
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM responsables")
        total = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT nombre_normalizado, COUNT(*) as cantidad 
            FROM responsables 
            GROUP BY nombre_normalizado 
            HAVING cantidad > 1
            ORDER BY cantidad DESC
        """)
        nombres_duplicados = cursor.fetchall()
        
        # Mostrar algunos ejemplos
        cursor.execute("SELECT nombre_original, nombre_normalizado FROM responsables LIMIT 10")
        ejemplos = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LA TABLA 'responsables'")
    print("=" * 60)
    print(f"Total de registros: {total}")
    
    if nombres_duplicados:
        print(f"\n⚠️  Nombres normalizados con múltiples originales ({len(nombres_duplicados)}):")
        for row in nombres_duplicados[:10]:
            print(f"   '{row['nombre_normalizado']}' -> {row['cantidad']} variantes")
    
    print("\n� Ejemplos de normalización:")
    for row in ejemplos:
        print(f"   '{row['nombre_original']}' -> '{row['nombre_normalizado']}'")

def exportar_mapeo(duplicados):
    """Exporta el mapeo a CSV para referencia"""
    conn = get_connection()
    
    with open('responsables_mapeo_final.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'nombre_original', 'nombre_normalizado', 'tiene_duplicados'])
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre_original, nombre_normalizado FROM responsables ORDER BY nombre_normalizado")
            for row in cursor.fetchall():
                tiene_dup = 'SI' if row['nombre_normalizado'] in duplicados else 'NO'
                writer.writerow([row['id'], row['nombre_original'], row['nombre_normalizado'], tiene_dup])
    
    conn.close()
    print(f"\n📄 Archivo de mapeo exportado: 'responsables_mapeo_final.csv'")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MODIFICACIÓN DE TABLA 'responsables'")
    print("=" * 60 + "\n")
    
    # 1. Modificar estructura
    modificar_estructura_tabla()
    
    # 2. Verificar estructura
    verificar_estructura()
    
    # 3. Insertar datos
    mapeo, duplicados = insertar_responsables()
    
    # 4. Mostrar resumen
    mostrar_resumen()
    
    # 5. Exportar mapeo
    exportar_mapeo(duplicados)
