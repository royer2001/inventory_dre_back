"""
Script para analizar y normalizar nombres al formato "NOMBRES APELLIDOS"
Detecta nombres que podrían estar en formato "APELLIDOS NOMBRES" y los corrige
"""
from dotenv import load_dotenv
load_dotenv()

from database.connection import get_connection
import re

# Lista de nombres comunes en español/Perú para detectar el inicio del nombre
NOMBRES_COMUNES = {
    # Nombres masculinos
    'ALDO', 'ALBERTO', 'ALEJANDRO', 'ALFONSO', 'ALFREDO', 'AMADEO', 'ANDRES', 'ANGEL', 
    'ANTONIO', 'ARMANDO', 'ARTURO', 'ANTHONY', 'CARLOS', 'CESAR', 'CLAUDIO', 'CRISTIAN',
    'DANIEL', 'DAVID', 'DIEGO', 'DOMINGO', 'EDGAR', 'EDUARDO', 'EDGARDO', 'EDIMIR', 'ELMER',
    'ENRIQUE', 'ERNESTO', 'FABIAN', 'FELIPE', 'FERNANDO', 'FLAVIO', 'FRANCISCO', 'FREDDY',
    'GABRIEL', 'GERMAN', 'GREGORIO', 'GUILLERMO', 'GUSTAVO', 'HECTOR', 'HUGO', 'IGNACIO',
    'IVAN', 'JAVIER', 'JESUS', 'JHONNY', 'JHONN', 'JIMY', 'JORGE', 'JOSE', 'JUAN', 'JULIO',
    'KENNETH', 'LEONCIO', 'LIBORIO', 'LIVIO', 'LORENZO', 'LUIS', 'MANUEL', 'MARCO', 'MARIO',
    'MARTIN', 'MIGUEL', 'NEYDER', 'OSCAR', 'OSMIDER', 'PABLO', 'PEDRO', 'PERCY', 'RAFAEL',
    'RAUL', 'REY', 'RICARDO', 'ROBERTO', 'ROMER', 'RUFO', 'SANTIAGO', 'SEGUNDO', 'SENOVIO',
    'WILLIAM', 'VICTOR',
    # Nombres femeninos
    'ADRIANA', 'ALEJANDRA', 'ALICIA', 'ANA', 'ANDREA', 'ANGELA', 'BEATRIZ', 'BERTHA', 'BLANCA',
    'CARMEN', 'CAROLINA', 'CECILIA', 'CLAUDIA', 'CINTHIA', 'CONSUELO', 'DELFINA', 'DIANA',
    'ELIZABETH', 'ELIZABETT', 'ELVA', 'ERIKA', 'ESPERANZA', 'FLOR', 'GABRIELA', 'GLADIS', 
    'GLADYS', 'GENOVEVA', 'HELLEN', 'INDARA', 'IRMA', 'ISABEL', 'IVONNE', 'JUDITH', 'JUANA',
    'JULIA', 'KAREN', 'LENA', 'LILY', 'LIUCARMEL', 'LIZ', 'LOURDES', 'LUCIA', 'LUZ', 'MAGALY',
    'MARIA', 'MARÍA', 'MARIBEL', 'MARLENY', 'MARTHA', 'MELBA', 'MILAGROS', 'NANCY', 'NELLY',
    'OLIVIA', 'OLGA', 'PATRICIA', 'PILAR', 'POLINARIA', 'ROCIO', 'ROSA', 'ROSSY', 'RUBI',
    'RUTH', 'SANDRA', 'SECI', 'SILVIA', 'SOFIA', 'SONIA', 'SUSAN', 'TANIA', 'TERESA', 
    'VANESSA', 'VERONICA', 'VIOLETA', 'WENDY', 'YAKELIN', 'YENNY', 'YULIANA', 'YSABEL'
}

# Apellidos comunes que NO deben confundirse con nombres
APELLIDOS_COMUNES = {
    'AGUI', 'AGUIRRE', 'ALVARADO', 'ALVAREZ', 'ANAYA', 'APAZA', 'ARBI', 'ARMANDINA',
    'ATENCIA', 'BARRUETA', 'BENANCIO', 'BERRIOS', 'BRAVO', 'CABELLO', 'CABRERA', 'CACHAY',
    'CAJALEON', 'CAJALEÓN', 'CANO', 'CANCHUMANTA', 'CAPIA', 'CHAHUA', 'CHAUPIS', 'CHUQUIYAURI',
    'CIERTO', 'COPELLO', 'CORDOVA', 'COTRINA', 'CRUZ', 'CUELLO', 'DIAZ', 'DURAND', 'ESPINOZA',
    'EUGENIO', 'FALCON', 'FERNANDEZ', 'FERRER', 'FIGUEREDO', 'GARCIA', 'GARAY', 'GASPAR',
    'GOMEZ', 'GONZALES', 'GOÑE', 'HERRERA', 'HUAMAN', 'HUAYANAY', 'HURTADO', 'IBAÑEZ', 
    'IBA\u00d1EZ', 'INGA', 'JANAMPA', 'JARA', 'LAZARO', 'LÁZARO', 'LOPEZ', 'LOZANO', 'LUGO',
    'LUNA', 'MANZANO', 'MELGAREJO', 'MEZA', 'MONTOL', 'MUNGUIA', 'NEGRETE', 'NIETO', 
    'ORTEGA', 'PAJUELO', 'PEÑA', 'POLO', 'PONCE', 'QUESADA', 'QUINTANA', 'QUISPE', 'RAMIREZ',
    'RAMOS', 'REMIGIO', 'RENGIFO', 'REYES', 'REYMUNDEZ', 'RIOS', 'RIVERA', 'RODRIGUEZ',
    'ROMAN', 'ROQUE', 'ROSAS', 'RUBIO', 'SALAZAR', 'SALDIVAR', 'SALVADOR', 'SANCHEZ', 
    'SÁNCHEZ', 'SARMIENTO', 'SERNA', 'SILVA', 'SIMON', 'SINCHE', 'SOLIS', 'SUAREZ', 'TACUCHE',
    'TAPIA', 'TARAZONA', 'TOLENTNO', 'TORRES', 'TREJO', 'VALDERRAMA', 'VARGAS', 'VELASQUE',
    'VENANCIO', 'VERA', 'VILLAFLORE', 'VILLAVICENCIO', 'VISAG', 'VIVAS', 'ZELAYA'
}

def detectar_formato(nombre):
    """
    Detecta si un nombre está en formato APELLIDOS NOMBRES o NOMBRES APELLIDOS
    Retorna: ('APELLIDOS_NOMBRES', 'NOMBRES_APELLIDOS', 'AMBIGUO', 'ESPECIAL')
    """
    partes = nombre.split()
    
    if len(partes) < 2:
        return 'ESPECIAL', None
    
    # Verificar si es una entidad especial (no persona)
    keywords_especiales = ['PEA', 'PELA', 'PPTCD', 'DGA', 'PATRIMONIO', 'PIRDAIS', 'COORDINADORA']
    if any(kw in nombre for kw in keywords_especiales):
        return 'ESPECIAL', None
    
    primera = partes[0].upper()
    segunda = partes[1].upper() if len(partes) > 1 else ''
    
    # Si la primera palabra es un nombre común, probablemente está en formato NOMBRES APELLIDOS
    if primera in NOMBRES_COMUNES:
        return 'NOMBRES_APELLIDOS', None
    
    # Si la primera palabra es un apellido conocido y hay un nombre después
    if primera in APELLIDOS_COMUNES:
        # Buscar dónde empieza el nombre
        for i, parte in enumerate(partes):
            if parte.upper() in NOMBRES_COMUNES:
                # Encontramos el nombre, todo antes son apellidos
                apellidos = ' '.join(partes[:i])
                nombres = ' '.join(partes[i:])
                return 'APELLIDOS_NOMBRES', f"{nombres} {apellidos}"
    
    # Si la segunda palabra parece apellido y la primera no es nombre conocido
    if segunda in APELLIDOS_COMUNES and primera not in NOMBRES_COMUNES:
        # Buscar dónde empieza el nombre
        for i, parte in enumerate(partes):
            if parte.upper() in NOMBRES_COMUNES:
                apellidos = ' '.join(partes[:i])
                nombres = ' '.join(partes[i:])
                return 'APELLIDOS_NOMBRES', f"{nombres} {apellidos}"
    
    return 'AMBIGUO', None

def analizar_nombres():
    """Analiza todos los nombres normalizados y detecta su formato"""
    conn = get_connection()
    
    print("=" * 80)
    print("📊 ANÁLISIS DE FORMATO DE NOMBRES EN TABLA 'responsables'")
    print("=" * 80 + "\n")
    
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, nombre_original, nombre_normalizado
            FROM responsables
            ORDER BY nombre_normalizado ASC
        """)
        registros = cursor.fetchall()
    
    conn.close()
    
    formatos = {
        'NOMBRES_APELLIDOS': [],
        'APELLIDOS_NOMBRES': [],
        'AMBIGUO': [],
        'ESPECIAL': []
    }
    
    for reg in registros:
        formato, sugerencia = detectar_formato(reg['nombre_normalizado'])
        formatos[formato].append({
            'id': reg['id'],
            'nombre_original': reg['nombre_original'],
            'nombre_normalizado': reg['nombre_normalizado'],
            'sugerencia': sugerencia
        })
    
    # Mostrar resultados por categoría
    print(f"✅ FORMATO CORRECTO (NOMBRES APELLIDOS): {len(formatos['NOMBRES_APELLIDOS'])} registros")
    print("-" * 80)
    for item in formatos['NOMBRES_APELLIDOS'][:5]:
        print(f"   ID {item['id']:3d}: {item['nombre_normalizado']}")
    if len(formatos['NOMBRES_APELLIDOS']) > 5:
        print(f"   ... y {len(formatos['NOMBRES_APELLIDOS']) - 5} más")
    
    print(f"\n⚠️  REQUIERE INVERSIÓN (APELLIDOS NOMBRES → NOMBRES APELLIDOS): {len(formatos['APELLIDOS_NOMBRES'])} registros")
    print("-" * 80)
    for item in formatos['APELLIDOS_NOMBRES']:
        print(f"   ID {item['id']:3d}: '{item['nombre_normalizado']}'")
        print(f"          → '{item['sugerencia']}'")
    
    print(f"\n❓ AMBIGUOS (requiere revisión manual): {len(formatos['AMBIGUO'])} registros")
    print("-" * 80)
    for item in formatos['AMBIGUO']:
        print(f"   ID {item['id']:3d}: {item['nombre_normalizado']}")
    
    print(f"\n🏢 ENTIDADES ESPECIALES (no personas): {len(formatos['ESPECIAL'])} registros")
    print("-" * 80)
    for item in formatos['ESPECIAL']:
        print(f"   ID {item['id']:3d}: {item['nombre_normalizado']}")
    
    print("\n" + "=" * 80)
    print("RESUMEN:")
    print(f"  - Formato correcto: {len(formatos['NOMBRES_APELLIDOS'])}")
    print(f"  - Requieren inversión: {len(formatos['APELLIDOS_NOMBRES'])}")
    print(f"  - Ambiguos: {len(formatos['AMBIGUO'])}")
    print(f"  - Especiales: {len(formatos['ESPECIAL'])}")
    print("=" * 80)
    
    return formatos

def aplicar_correcciones(formatos):
    """Aplica las correcciones de formato a los nombres que lo requieren"""
    items_a_corregir = formatos['APELLIDOS_NOMBRES']
    
    if not items_a_corregir:
        print("\n✅ No hay nombres que corregir automáticamente.")
        return
    
    conn = get_connection()
    
    print(f"\n🔧 APLICANDO CORRECCIONES ({len(items_a_corregir)} registros)...")
    
    corregidos = 0
    errores = 0
    
    with conn.cursor() as cursor:
        for item in items_a_corregir:
            try:
                cursor.execute("""
                    UPDATE responsables 
                    SET nombre_normalizado = %s
                    WHERE id = %s
                """, (item['sugerencia'], item['id']))
                corregidos += 1
                print(f"   ✓ ID {item['id']}: '{item['nombre_normalizado']}' → '{item['sugerencia']}'")
            except Exception as e:
                errores += 1
                print(f"   ✗ Error ID {item['id']}: {e}")
        
        conn.commit()
    
    conn.close()
    
    print(f"\n✅ Correcciones aplicadas: {corregidos}")
    print(f"❌ Errores: {errores}")

if __name__ == "__main__":
    # 1. Analizar nombres
    formatos = analizar_nombres()
    
    # 2. Preguntar si aplicar correcciones
    items_corregir = formatos['APELLIDOS_NOMBRES']
    if items_corregir:
        print(f"\n¿Aplicar {len(items_corregir)} correcciones automáticas? (El script continuará)")
        aplicar_correcciones(formatos)
        
        # 3. Mostrar estado final
        print("\n" + "=" * 80)
        print("📋 VERIFICACIÓN FINAL")
        print("=" * 80)
        analizar_nombres()
