"""
Script para analizar y corregir manualmente los nombres ambiguos
"""
from dotenv import load_dotenv
load_dotenv()

from database.connection import get_connection
import csv

# Correcciones manuales para los nombres ambiguos
# Formato: ID -> nuevo_nombre_normalizado
CORRECCIONES_MANUALES = {
    # ID 26: ATENCIA ARBI JIM CLAVER -> JIM CLAVER ATENCIA ARBI
    26: "JIM CLAVER ATENCIA ARBI",
    
    # ID 57: AVILA ROJAS ETHEL JESUS -> ETHEL JESUS AVILA ROJAS
    57: "ETHEL JESUS AVILA ROJAS",
    
    # ID 58: BURGA SAAVEDRA FERNANDO JHON -> FERNANDO JHON BURGA SAAVEDRA
    58: "FERNANDO JHON BURGA SAAVEDRA",
    
    # ID 28: CABRERA SUAREZ EVELYN -> EVELYN CABRERA SUAREZ
    28: "EVELYN CABRERA SUAREZ",
    
    # ID 29: CAJA LEON COTRINA FLAVIO -> FLAVIO CAJA LEON COTRINA (parece error, posible duplicado)
    29: "FLAVIO CAJA LEON COTRINA",
    
    # ID 103: CAJAS ATACHAGUA MAGNA FIORELLA -> MAGNA FIORELLA CAJAS ATACHAGUA
    103: "MAGNA FIORELLA CAJAS ATACHAGUA",
    
    # ID 95: CANDY LINO MUNGUIA -> Ya está correcto (CANDY es nombre)
    95: "CANDY LINO MUNGUIA",
    
    # ID 50: CHAMORRO VISCAYA DORIS MIRYAM -> DORIS MIRYAM CHAMORRO VISCAYA
    50: "DORIS MIRYAM CHAMORRO VISCAYA",
    
    # ID 33: CHÁVEZ VIN CARLOS GROVER -> CARLOS GROVER CHÁVEZ VIN
    33: "CARLOS GROVER CHÁVEZ VIN",
    
    # ID 37: COOKLEY A. ALBORNOZ ROSAS -> Mantener (nombre extranjero)
    37: "COOKLEY A. ALBORNOZ ROSAS",
    
    # ID 39: CORONEL ALVAREZ RONALD -> RONALD CORONEL ALVAREZ
    39: "RONALD CORONEL ALVAREZ",
    
    # ID 144: CORONEL ALVAREZ RONALD ORBAL -> RONALD ORBAL CORONEL ALVAREZ
    144: "RONALD ORBAL CORONEL ALVAREZ",
    
    # ID 73: COTRINA TARAZONA ISOLINA DORIS -> ISOLINA DORIS COTRINA TARAZONA
    73: "ISOLINA DORIS COTRINA TARAZONA",
    
    # ID 53: COZ FELIX ELIZABETH -> ELIZABETH COZ FELIX
    53: "ELIZABETH COZ FELIX",
    
    # ID 36: CUEVA DIAZ CINTIA YULEISI -> CINTIA YULEISI CUEVA DIAZ
    36: "CINTIA YULEISI CUEVA DIAZ",
    
    # ID 48: CUEVA GALIANO MARCIA REGINA -> MARCIA REGINA CUEVA GALIANO
    48: "MARCIA REGINA CUEVA GALIANO",
    
    # ID 49: EDWIN HUAYNATE ORTEGA -> Ya está correcto (EDWIN es nombre)
    49: "EDWIN HUAYNATE ORTEGA",
    
    # ID 55: ERICK PATRICK CRUZ MEJIA -> Ya está correcto (ERICK es nombre)
    55: "ERICK PATRICK CRUZ MEJIA",
    
    # ID 124: FIGUEROA SÁNCHEZ JIM JAMES -> JIM JAMES FIGUEROA SÁNCHEZ
    124: "JIM JAMES FIGUEROA SÁNCHEZ",
    
    # ID 159: FIORELLA VARA LUCAS -> Ya está correcto (FIORELLA es nombre)
    159: "FIORELLA VARA LUCAS",
    
    # ID 102: GAYOSO RAMOS MADELIN -> MADELIN GAYOSO RAMOS
    102: "MADELIN GAYOSO RAMOS",
    
    # ID 66: GONZLAES SANTIAGO JOCSAN ELIAS -> JOCSAN ELIAS GONZALES SANTIAGO (corregido typo)
    66: "JOCSAN ELIAS GONZALES SANTIAGO",
    
    # ID 85: HEYDY BERONICA AVELINO MARTIN -> Ya está correcto (HEYDY es nombre)
    85: "HEYDY BERONICA AVELINO MARTIN",
    
    # ID 27: HIDALGO CONCEPCIÓN BERSY ALEJANDRINA -> BERSY ALEJANDRINA HIDALGO CONCEPCIÓN
    27: "BERSY ALEJANDRINA HIDALGO CONCEPCIÓN",
    
    # ID 46: HIDALGO HUAMAN WILSON SAUL -> WILSON SAUL HIDALGO HUAMAN
    46: "WILSON SAUL HIDALGO HUAMAN",
    
    # ID 68: HOUSEN ELVIS VEGA ESPINOZA -> HOUSEN ELVIS VEGA ESPINOZA (nombre compuesto)
    68: "HOUSEN ELVIS VEGA ESPINOZA",
    
    # ID 70: HUAYNATE ORTEGA EDWIN -> EDWIN HUAYNATE ORTEGA
    70: "EDWIN HUAYNATE ORTEGA",
    
    # ID 92: JAIME DIMAS CESPEDES ROLDAN -> Ya está correcto (JAIME es nombre)
    92: "JAIME DIMAS CESPEDES ROLDAN",
    
    # ID 135: JESSENIA DEL PILAR BERNA VENTURA -> Ya está correcto (JESSENIA es nombre)
    135: "JESSENIA DEL PILAR BERNA VENTURA",
    
    # ID 51: JIM CLAVER ATENCIA ARBI -> Ya está correcto (JIM es nombre)
    51: "JIM CLAVER ATENCIA ARBI",
    
    # ID 65: JOCSAN ELIAS GONZALES SANTIAGO -> Ya está correcto (JOCSAN es nombre)
    65: "JOCSAN ELIAS GONZALES SANTIAGO",
    
    # ID 31: LOPEZ LLANOS CAMILO FRANKLIN -> CAMILO FRANKLIN LOPEZ LLANOS
    31: "CAMILO FRANKLIN LOPEZ LLANOS",
    
    # ID 136: LUREN PINEDA CORDOVA -> LUREN PINEDA CORDOVA (LUREN es nombre)
    136: "LUREN PINEDA CORDOVA",
    
    # ID 148: NOLASCO MAGARIÑO SHEYLA MYRELLA -> SHEYLA MYRELLA NOLASCO MAGARIÑO
    148: "SHEYLA MYRELLA NOLASCO MAGARIÑO",
    
    # ID 127: OLINDA FALCON OSORIO -> Ya está correcto (OLINDA es nombre)
    127: "OLINDA FALCON OSORIO",
    
    # ID 23: ORTIZ VARGAS ANGELICA TARCILA -> ANGELICA TARCILA ORTIZ VARGAS
    23: "ANGELICA TARCILA ORTIZ VARGAS",
    
    # ID 78: PANDURO CONTRERAS JUDITH MARGARITA -> JUDITH MARGARITA PANDURO CONTRERAS
    78: "JUDITH MARGARITA PANDURO CONTRERAS",
    
    # ID 83: PAULINA MARGOT BENDEZU ROMERO -> Ya está correcto (PAULINA es nombre)
    83: "PAULINA MARGOT BENDEZU ROMERO",
    
    # ID 9: SUAREZ GONZALES GOMER JAFET -> GOMER JAFET SUAREZ GONZALES
    9: "GOMER JAFET SUAREZ GONZALES",
}

def obtener_ambiguos():
    """Obtiene los registros ambiguos de la base de datos"""
    conn = get_connection()
    
    ids_ambiguos = list(CORRECCIONES_MANUALES.keys())
    
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, nombre_original, nombre_normalizado
            FROM responsables
            WHERE id IN %s
            ORDER BY id ASC
        """, (tuple(ids_ambiguos),))
        registros = cursor.fetchall()
    
    conn.close()
    return registros

def mostrar_propuestas():
    """Muestra las propuestas de corrección"""
    registros = obtener_ambiguos()
    
    print("=" * 90)
    print("📋 PROPUESTAS DE CORRECCIÓN PARA NOMBRES AMBIGUOS")
    print("=" * 90 + "\n")
    
    cambios = 0
    sin_cambios = 0
    
    for reg in registros:
        id_reg = reg['id']
        actual = reg['nombre_normalizado']
        propuesto = CORRECCIONES_MANUALES.get(id_reg, actual)
        
        if actual != propuesto:
            cambios += 1
            print(f"ID {id_reg:3d}: ⚠️  CAMBIO")
            print(f"   Original: '{reg['nombre_original']}'")
            print(f"   Actual:   '{actual}'")
            print(f"   Nuevo:    '{propuesto}'")
            print()
        else:
            sin_cambios += 1
            print(f"ID {id_reg:3d}: ✓ SIN CAMBIO - '{actual}'")
    
    print("\n" + "=" * 90)
    print(f"RESUMEN: {cambios} cambios propuestos, {sin_cambios} sin cambios")
    print("=" * 90)
    
    return cambios

def aplicar_correcciones():
    """Aplica las correcciones manuales"""
    conn = get_connection()
    
    print("\n🔧 APLICANDO CORRECCIONES MANUALES...")
    
    aplicados = 0
    errores = 0
    
    with conn.cursor() as cursor:
        for id_reg, nuevo_nombre in CORRECCIONES_MANUALES.items():
            # Verificar si hay cambio real
            cursor.execute(
                "SELECT nombre_normalizado FROM responsables WHERE id = %s",
                (id_reg,)
            )
            resultado = cursor.fetchone()
            
            if resultado and resultado['nombre_normalizado'] != nuevo_nombre:
                try:
                    cursor.execute("""
                        UPDATE responsables 
                        SET nombre_normalizado = %s
                        WHERE id = %s
                    """, (nuevo_nombre, id_reg))
                    aplicados += 1
                    print(f"   ✓ ID {id_reg}: '{resultado['nombre_normalizado']}' → '{nuevo_nombre}'")
                except Exception as e:
                    errores += 1
                    print(f"   ✗ Error ID {id_reg}: {e}")
        
        conn.commit()
    
    conn.close()
    
    print(f"\n✅ Correcciones aplicadas: {aplicados}")
    print(f"❌ Errores: {errores}")

def exportar_csv():
    """Exporta un CSV con los cambios propuestos"""
    registros = obtener_ambiguos()
    
    with open('correcciones_ambiguos.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Nombre Original', 'Actual', 'Propuesto', 'Cambia'])
        
        for reg in registros:
            id_reg = reg['id']
            actual = reg['nombre_normalizado']
            propuesto = CORRECCIONES_MANUALES.get(id_reg, actual)
            cambia = "SÍ" if actual != propuesto else "NO"
            
            writer.writerow([id_reg, reg['nombre_original'], actual, propuesto, cambia])
    
    print("📄 Archivo 'correcciones_ambiguos.csv' exportado")

if __name__ == "__main__":
    # 1. Mostrar propuestas
    cambios = mostrar_propuestas()
    
    if cambios > 0:
        # 2. Exportar CSV para revisión
        exportar_csv()
        
        # 3. Aplicar correcciones
        print(f"\n¿Aplicar {cambios} correcciones? (El script continuará)")
        aplicar_correcciones()
        
        # 4. Verificar
        print("\n" + "=" * 90)
        print("📋 VERIFICACIÓN FINAL")
        print("=" * 90)
        
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM responsables")
            total = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT id, nombre_normalizado 
                FROM responsables 
                ORDER BY nombre_normalizado ASC
                LIMIT 15
            """)
            muestra = cursor.fetchall()
        conn.close()
        
        print(f"Total de responsables: {total}")
        print("\nMuestra de nombres corregidos:")
        for reg in muestra:
            print(f"   ID {reg['id']:3d}: {reg['nombre_normalizado']}")
