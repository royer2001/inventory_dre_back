"""
Script de prueba para los endpoints de códigos de barras
"""
import requests
import json

BASE_URL = "http://localhost:5000/barcode"

def test_get_offices():
    """Prueba obtener lista de oficinas"""
    print("\n1. Probando GET /barcode/offices...")
    response = requests.get(f"{BASE_URL}/offices")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Oficinas encontradas: {len(data.get('offices', []))}")
    if data.get('offices'):
        print(f"Primeras 3: {data['offices'][:3]}")
    return data

def test_get_bienes():
    """Prueba obtener bienes"""
    print("\n2. Probando GET /barcode/bienes...")
    response = requests.get(f"{BASE_URL}/bienes?per_page=5")
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"Bienes encontrados: {len(data.get('data', []))}")
        print(f"Total en BD: {data.get('pagination', {}).get('total', 0)}")
        if data.get('data'):
            print(f"Primer bien: {data['data'][0]['codigo_completo']}")
    return data

def test_generate_pdf_filter():
    """Prueba generar PDF por filtro"""
    print("\n3. Probando POST /barcode/generate/filter...")
    payload = {
        "office": "",  # Vacío = todas las oficinas
        "search": ""   # Vacío = sin búsqueda
    }
    
    print("⚠️  Nota: Este endpoint descarga un PDF. Requiere bienes en la BD.")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    # Descomenta la siguiente línea para probar la descarga
    # response = requests.post(f"{BASE_URL}/generate/filter", json=payload)
    # with open("test_output.pdf", "wb") as f:
    #     f.write(response.content)
    # print("PDF guardado como test_output.pdf")

def test_generate_pdf_selection():
    """Prueba generar PDF por selección"""
    print("\n4. Probando POST /barcode/generate/selection...")
    
    # Primero obtenemos algunos bienes
    response = requests.get(f"{BASE_URL}/bienes?per_page=3")
    data = response.json()
    
    if not data.get('data'):
        print("❌ No hay bienes para seleccionar")
        return
    
    # Preparar payload
    bienes_selection = []
    for bien in data['data'][:2]:  # Tomar solo 2 para prueba
        bienes_selection.append({
            "codigo": bien['codigo_completo'],
            "detalle_bien": bien['detalle_bien'],
            "tipo_registro": bien['tipo_registro'],
            "oficina": bien['oficina']
        })
    
    payload = {"bienes": bienes_selection}
    print(f"Generando PDF con {len(bienes_selection)} bienes...")
    
    # Descomenta para descargar
    # response = requests.post(f"{BASE_URL}/generate/selection", json=payload)
    # with open("test_selection.pdf", "wb") as f:
    #     f.write(response.content)
    # print("PDF guardado como test_selection.pdf")

def test_generate_pdf_offices():
    """Prueba generar PDF por oficinas"""
    print("\n5. Probando POST /barcode/generate/offices...")
    
    # Obtener oficinas
    response = requests.get(f"{BASE_URL}/offices")
    data = response.json()
    
    if not data.get('offices'):
        print("❌ No hay oficinas disponibles")
        return
    
    # Tomar las primeras 2 oficinas
    selected_offices = data['offices'][:2]
    payload = {"offices": selected_offices}
    
    print(f"Generando PDF para oficinas: {selected_offices}")
    
    # Descomenta para descargar
    # response = requests.post(f"{BASE_URL}/generate/offices", json=payload)
    # with open("test_offices.pdf", "wb") as f:
    #     f.write(response.content)
    # print("PDF guardado como test_offices.pdf")

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE ENDPOINTS DE CÓDIGOS DE BARRAS")
    print("=" * 60)
    
    try:
        # Pruebas básicas (GET)
        test_get_offices()
        test_get_bienes()
        
        # Pruebas de generación (comentadas por defecto)
        test_generate_pdf_filter()
        test_generate_pdf_selection()
        test_generate_pdf_offices()
        
        print("\n" + "=" * 60)
        print("✅ Pruebas completadas")
        print("=" * 60)
        print("\n💡 Para probar la generación de PDFs, descomenta las líneas")
        print("   correspondientes en el script.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor Flask")
        print("   Asegúrate de que Flask esté corriendo en http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
