import requests
import csv

# 1. La lista de URLs proporcionada por el usuario
categorias_manual = [
    "https://tienda.mercadona.es/categories/112",
    "https://tienda.mercadona.es/categories/115",
    "https://tienda.mercadona.es/categories/116",
    "https://tienda.mercadona.es/categories/117",
    "https://tienda.mercadona.es/categories/156",
    "https://tienda.mercadona.es/categories/163",
    "https://tienda.mercadona.es/categories/158",
    "https://tienda.mercadona.es/categories/159",
    "https://tienda.mercadona.es/categories/161",
    "https://tienda.mercadona.es/categories/162",
    "https://tienda.mercadona.es/categories/135",
    "https://tienda.mercadona.es/categories/133",
    "https://tienda.mercadona.es/categories/132",
    "https://tienda.mercadona.es/categories/118",
    "https://tienda.mercadona.es/categories/121",
    "https://tienda.mercadona.es/categories/120",
    "https://tienda.mercadona.es/categories/89",
    "https://tienda.mercadona.es/categories/95",
    "https://tienda.mercadona.es/categories/92",
    "https://tienda.mercadona.es/categories/97",
    "https://tienda.mercadona.es/categories/90",
    "https://tienda.mercadona.es/categories/833",
    "https://tienda.mercadona.es/categories/216",
    "https://tienda.mercadona.es/categories/219",
    "https://tienda.mercadona.es/categories/218",
    "https://tienda.mercadona.es/categories/217",
    "https://tienda.mercadona.es/categories/164",
    "https://tienda.mercadona.es/categories/166",
    "https://tienda.mercadona.es/categories/181",
    "https://tienda.mercadona.es/categories/174",
    "https://tienda.mercadona.es/categories/168",
    "https://tienda.mercadona.es/categories/170",
    "https://tienda.mercadona.es/categories/173",
    "https://tienda.mercadona.es/categories/171",
    "https://tienda.mercadona.es/categories/169",
    "https://tienda.mercadona.es/categories/86",
    "https://tienda.mercadona.es/categories/81",
    "https://tienda.mercadona.es/categories/83",
    "https://tienda.mercadona.es/categories/84",
    "https://tienda.mercadona.es/categories/88",
    "https://tienda.mercadona.es/categories/46",
    "https://tienda.mercadona.es/categories/38",
    "https://tienda.mercadona.es/categories/47",
    "https://tienda.mercadona.es/categories/37",
    "https://tienda.mercadona.es/categories/42",
    "https://tienda.mercadona.es/categories/43",
    "https://tienda.mercadona.es/categories/44",
    "https://tienda.mercadona.es/categories/40",
    "https://tienda.mercadona.es/categories/45",
    "https://tienda.mercadona.es/categories/78",
    "https://tienda.mercadona.es/categories/80",
    "https://tienda.mercadona.es/categories/79",
    "https://tienda.mercadona.es/categories/48",
    "https://tienda.mercadona.es/categories/52",
    "https://tienda.mercadona.es/categories/49",
    "https://tienda.mercadona.es/categories/51",
    "https://tienda.mercadona.es/categories/50",
    "https://tienda.mercadona.es/categories/58",
    "https://tienda.mercadona.es/categories/54",
    "https://tienda.mercadona.es/categories/56",
    "https://tienda.mercadona.es/categories/53",
    "https://tienda.mercadona.es/categories/147",
    "https://tienda.mercadona.es/categories/148",
    "https://tienda.mercadona.es/categories/154",
    "https://tienda.mercadona.es/categories/155",
    "https://tienda.mercadona.es/categories/150",
    "https://tienda.mercadona.es/categories/149",
    "https://tienda.mercadona.es/categories/151",
    "https://tienda.mercadona.es/categories/884",
    "https://tienda.mercadona.es/categories/152",
    "https://tienda.mercadona.es/categories/145",
    "https://tienda.mercadona.es/categories/122",
    "https://tienda.mercadona.es/categories/123",
    "https://tienda.mercadona.es/categories/127",
    "https://tienda.mercadona.es/categories/130",
    "https://tienda.mercadona.es/categories/129",
    "https://tienda.mercadona.es/categories/126",
    "https://tienda.mercadona.es/categories/201",
    "https://tienda.mercadona.es/categories/199",
    "https://tienda.mercadona.es/categories/203",
    "https://tienda.mercadona.es/categories/202",
    "https://tienda.mercadona.es/categories/192",
    "https://tienda.mercadona.es/categories/189",
    "https://tienda.mercadona.es/categories/185",
    "https://tienda.mercadona.es/categories/191",
    "https://tienda.mercadona.es/categories/188",
    "https://tienda.mercadona.es/categories/187",
    "https://tienda.mercadona.es/categories/186",
    "https://tienda.mercadona.es/categories/190",
    "https://tienda.mercadona.es/categories/194",
    "https://tienda.mercadona.es/categories/196",
    "https://tienda.mercadona.es/categories/198",
    "https://tienda.mercadona.es/categories/213",
    "https://tienda.mercadona.es/categories/214",
    "https://tienda.mercadona.es/categories/27",
    "https://tienda.mercadona.es/categories/28",
    "https://tienda.mercadona.es/categories/29",
    "https://tienda.mercadona.es/categories/77",
    "https://tienda.mercadona.es/categories/72",
    "https://tienda.mercadona.es/categories/75",
    "https://tienda.mercadona.es/categories/226",
    "https://tienda.mercadona.es/categories/237",
    "https://tienda.mercadona.es/categories/241",
    "https://tienda.mercadona.es/categories/234",
    "https://tienda.mercadona.es/categories/235",
    "https://tienda.mercadona.es/categories/233",
    "https://tienda.mercadona.es/categories/231",
    "https://tienda.mercadona.es/categories/230",
    "https://tienda.mercadona.es/categories/232",
    "https://tienda.mercadona.es/categories/229",
    "https://tienda.mercadona.es/categories/243",
    "https://tienda.mercadona.es/categories/238",
    "https://tienda.mercadona.es/categories/239",
    "https://tienda.mercadona.es/categories/244",
    "https://tienda.mercadona.es/categories/206",
    "https://tienda.mercadona.es/categories/207",
    "https://tienda.mercadona.es/categories/208",
    "https://tienda.mercadona.es/categories/210",
    "https://tienda.mercadona.es/categories/212",
    "https://tienda.mercadona.es/categories/32",
    "https://tienda.mercadona.es/categories/34",
    "https://tienda.mercadona.es/categories/31",
    "https://tienda.mercadona.es/categories/36",
    "https://tienda.mercadona.es/categories/222",
    "https://tienda.mercadona.es/categories/221",
    "https://tienda.mercadona.es/categories/225",
    "https://tienda.mercadona.es/categories/65",
    "https://tienda.mercadona.es/categories/66",
    "https://tienda.mercadona.es/categories/69",
    "https://tienda.mercadona.es/categories/59",
    "https://tienda.mercadona.es/categories/60",
    "https://tienda.mercadona.es/categories/62",
    "https://tienda.mercadona.es/categories/64",
    "https://tienda.mercadona.es/categories/68",
    "https://tienda.mercadona.es/categories/71",
    "https://tienda.mercadona.es/categories/897",
    "https://tienda.mercadona.es/categories/138",
    "https://tienda.mercadona.es/categories/140",
    "https://tienda.mercadona.es/categories/142",
    "https://tienda.mercadona.es/categories/105",
    "https://tienda.mercadona.es/categories/110",
    "https://tienda.mercadona.es/categories/111",
    "https://tienda.mercadona.es/categories/106",
    "https://tienda.mercadona.es/categories/103",
    "https://tienda.mercadona.es/categories/109",
    "https://tienda.mercadona.es/categories/108",
    "https://tienda.mercadona.es/categories/104",
    "https://tienda.mercadona.es/categories/107",
    "https://tienda.mercadona.es/categories/99",
    "https://tienda.mercadona.es/categories/100",
    "https://tienda.mercadona.es/categories/143",
    "https://tienda.mercadona.es/categories/98",
]

# 2. Esta es la API que usa la web de Mercadona para construir su menú
API_URL = "https://tienda.mercadona.es/api/categories/"

# 3. Nombre del archivo CSV de salida
CSV_FILENAME = 'mercadona_categorias_grupos.csv'

# 4. Simular ser un navegador para evitar bloqueos
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_category_map():
    """
    Hace una sola llamada a la API de Mercadona y devuelve un diccionario
    mapeando cada ID de subcategoría a su nombre y al nombre de su grupo padre.
    """
    print(f"Contactando la API de Mercadona en: {API_URL}")
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()  # Lanza un error si la petición falla
        data = response.json()
        
        print("API contactada. Creando mapa de categorías...")
        category_map = {}
        
        # 'results' es la lista de "Grupos Principales"
        for parent_group in data.get('results', []):
            parent_name = parent_group.get('name', 'Sin Grupo')
            
            # 'categories' es la lista de "Categorías Individuales"
            for child_category in parent_group.get('categories', []):
                child_id = str(child_category.get('id'))
                child_name = child_category.get('name', 'Sin Nombre')
                
                # Guardamos la info usando el ID como clave
                category_map[child_id] = {
                    'parent': parent_name,
                    'name': child_name
                }
        
        print(f"Mapa creado con {len(category_map)} categorías individuales.")
        return category_map

    except requests.exceptions.RequestException as e:
        print(f"ERROR: No se pudo conectar a la API. {e}")
        return None
    except Exception as e:
        print(f"ERROR: No se pudo procesar el JSON de la API. {e}")
        return None

def main():
    # 1. Obtener el mapa de categorías desde la API
    id_map = get_category_map()
    
    if id_map is None:
        print("No se pudo generar el mapa de categorías. Abortando.")
        return

    # 2. Abrir el archivo CSV para escribir
    print(f"Escribiendo datos en '{CSV_FILENAME}'...")
    try:
        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # 3. Crear el escritor CSV y escribir la cabecera
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['URL', 'GrupoPrincipal', 'NombreCategoria'])
            
            # 4. Iterar sobre la lista de URLs manual
            for url in categorias_manual:
                # 5. Extraer el ID de la URL
                # "https://tienda.mercadona.es/categories/112" -> "112"
                cat_id = url.split('/')[-1]
                
                # 6. Buscar el ID en nuestro mapa
                if cat_id in id_map:
                    info = id_map[cat_id]
                    # Escribir la fila completa
                    csv_writer.writerow([
                        url, 
                        info['parent'], 
                        info['name']
                    ])
                else:
                    # Si por alguna razón una URL de tu lista no está en la API
                    print(f"  [ATENCIÓN] El ID {cat_id} de la URL {url} no se encontró en la API.")
                    csv_writer.writerow([url, 'ERROR', 'ID no encontrado en API'])

        print(f"\n¡Proceso completado! Los datos están en '{CSV_FILENAME}'.")
    
    except IOError as e:
        print(f"ERROR: No se pudo escribir en el archivo CSV. {e}")

# Ejecutar el script
if __name__ == "__main__":
    main()