"""
Script para agregar la columna responsable_id a la tabla movimientos
"""
from dotenv import load_dotenv
load_dotenv()

from database.connection import get_connection

def agregar_columna_responsable_id():
    """Agrega la columna responsable_id a la tabla movimientos"""
    conn = get_connection()
    
    print("🔧 Agregando columna 'responsable_id' a la tabla 'movimientos'...")
    
    with conn.cursor() as cursor:
        # 1. Agregar la columna responsable_id
        try:
            cursor.execute("""
                ALTER TABLE movimientos 
                ADD COLUMN responsable_id INT NULL 
                AFTER responsable
            """)
            print("   ✓ Columna 'responsable_id' agregada")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("   ⚠ Columna 'responsable_id' ya existe")
            else:
                print(f"   ❌ Error: {e}")
                return
        
        # 2. Agregar la clave foránea
        try:
            cursor.execute("""
                ALTER TABLE movimientos 
                ADD CONSTRAINT fk_movimientos_responsable 
                FOREIGN KEY (responsable_id) 
                REFERENCES responsables(id) 
                ON DELETE SET NULL 
                ON UPDATE CASCADE
            """)
            print("   ✓ Clave foránea 'fk_movimientos_responsable' agregada")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("   ⚠ Clave foránea ya existe")
            else:
                print(f"   ⚠ FK: {e}")
        
        # 3. Agregar índice para mejor rendimiento
        try:
            cursor.execute("""
                ALTER TABLE movimientos 
                ADD INDEX idx_responsable_id (responsable_id)
            """)
            print("   ✓ Índice 'idx_responsable_id' agregado")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print("   ⚠ Índice ya existe")
            else:
                print(f"   ⚠ Índice: {e}")
        
        conn.commit()
    
    conn.close()
    print("✅ Modificación de tabla 'movimientos' completada\n")

def verificar_estructura():
    """Verifica la estructura final de la tabla"""
    conn = get_connection()
    
    with conn.cursor() as cursor:
        cursor.execute("DESCRIBE movimientos")
        columnas = cursor.fetchall()
    
    conn.close()
    
    print("📋 Estructura actual de la tabla 'movimientos':")
    for col in columnas:
        print(f"   - {col['Field']}: {col['Type']} (NULL: {col['Null']}, Key: {col['Key']})")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MODIFICACIÓN DE TABLA 'movimientos'")
    print("=" * 60 + "\n")
    
    agregar_columna_responsable_id()
    verificar_estructura()
