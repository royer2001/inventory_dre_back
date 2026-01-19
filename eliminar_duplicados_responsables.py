"""
Script para analizar y eliminar duplicados en la tabla responsables
"""
from dotenv import load_dotenv
load_dotenv()

from database.connection import get_connection

def analizar_duplicados():
    """Analiza los duplicados en la tabla responsables"""
    conn = get_connection()
    
    print("=" * 70)
    print("📊 ANÁLISIS DE DUPLICADOS EN TABLA 'responsables'")
    print("=" * 70 + "\n")
    
    with conn.cursor() as cursor:
        # Obtener todos los nombres normalizados que tienen duplicados
        cursor.execute("""
            SELECT nombre_normalizado, COUNT(*) as cantidad
            FROM responsables
            GROUP BY nombre_normalizado
            HAVING COUNT(*) > 1
            ORDER BY cantidad DESC, nombre_normalizado ASC
        """)
        duplicados = cursor.fetchall()
        
        print(f"Se encontraron {len(duplicados)} nombres normalizados con duplicados:\n")
        
        total_duplicados = 0
        detalles = []
        
        for dup in duplicados:
            nombre_norm = dup['nombre_normalizado']
            cantidad = dup['cantidad']
            total_duplicados += (cantidad - 1)  # -1 porque uno se queda
            
            # Obtener los registros duplicados
            cursor.execute("""
                SELECT id, nombre_original, nombre_normalizado
                FROM responsables
                WHERE nombre_normalizado = %s
                ORDER BY id ASC
            """, (nombre_norm,))
            registros = cursor.fetchall()
            
            detalles.append({
                'nombre_normalizado': nombre_norm,
                'cantidad': cantidad,
                'registros': registros,
                'mantener_id': registros[0]['id'],  # Mantener el primero (ID más bajo)
                'eliminar_ids': [r['id'] for r in registros[1:]]  # Eliminar los demás
            })
            
            print(f"📌 '{nombre_norm}' ({cantidad} registros):")
            for reg in registros:
                marca = "✓ MANTENER" if reg['id'] == registros[0]['id'] else "✗ ELIMINAR"
                print(f"   ID {reg['id']:3d}: '{reg['nombre_original']}' [{marca}]")
            print()
    
    conn.close()
    
    print("-" * 70)
    print(f"RESUMEN:")
    print(f"  - Nombres normalizados duplicados: {len(duplicados)}")
    print(f"  - Registros a eliminar: {total_duplicados}")
    print("-" * 70)
    
    return detalles

def eliminar_duplicados(detalles):
    """Elimina los registros duplicados manteniendo el de ID más bajo"""
    if not detalles:
        print("\n✅ No hay duplicados que eliminar.")
        return
    
    conn = get_connection()
    
    print("\n🗑️  ELIMINANDO DUPLICADOS...")
    
    eliminados = 0
    errores = 0
    
    with conn.cursor() as cursor:
        for det in detalles:
            for id_eliminar in det['eliminar_ids']:
                try:
                    cursor.execute("DELETE FROM responsables WHERE id = %s", (id_eliminar,))
                    eliminados += 1
                    print(f"   ✓ Eliminado ID {id_eliminar}: '{det['nombre_normalizado']}'")
                except Exception as e:
                    errores += 1
                    print(f"   ✗ Error eliminando ID {id_eliminar}: {e}")
        
        conn.commit()
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO DE ELIMINACIÓN")
    print("=" * 70)
    print(f"  - Registros eliminados: {eliminados}")
    print(f"  - Errores: {errores}")

def verificar_resultado():
    """Verifica el estado final de la tabla"""
    conn = get_connection()
    
    with conn.cursor() as cursor:
        # Total de registros
        cursor.execute("SELECT COUNT(*) as total FROM responsables")
        total = cursor.fetchone()['total']
        
        # Verificar si quedan duplicados
        cursor.execute("""
            SELECT COUNT(*) as duplicados FROM (
                SELECT nombre_normalizado
                FROM responsables
                GROUP BY nombre_normalizado
                HAVING COUNT(*) > 1
            ) as dup
        """)
        duplicados_restantes = cursor.fetchone()['duplicados']
        
        # Muestra algunos registros
        cursor.execute("""
            SELECT id, nombre_original, nombre_normalizado 
            FROM responsables 
            ORDER BY nombre_normalizado ASC
            LIMIT 10
        """)
        muestra = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("📋 ESTADO FINAL DE LA TABLA 'responsables'")
    print("=" * 70)
    print(f"  - Total de registros: {total}")
    print(f"  - Duplicados restantes: {duplicados_restantes}")
    
    if duplicados_restantes == 0:
        print("\n✅ ¡Todos los duplicados han sido eliminados!")
    
    print("\n📝 Muestra de registros:")
    for reg in muestra:
        print(f"   ID {reg['id']:3d}: {reg['nombre_normalizado']}")

if __name__ == "__main__":
    # 1. Analizar duplicados
    detalles = analizar_duplicados()
    
    if detalles:
        # 2. Preguntar confirmación (para script interactivo)
        print("\n¿Proceder con la eliminación? (El script continuará automáticamente)")
        
        # 3. Eliminar duplicados
        eliminar_duplicados(detalles)
        
        # 4. Verificar resultado
        verificar_resultado()
    else:
        print("\n✅ No hay duplicados en la tabla.")
