import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd

def setup_driver(headless=False):
    """Configura el driver de Selenium"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def manejar_codigo_postal(driver, codigo_postal='46001'):   # Valencia por defecto
    """Maneja el modal de código postal y espera que se cargue la tienda"""
    try:
        print("Esperando modal de código postal...")
        wait = WebDriverWait(driver, 15)
        
        # Esperar que aparezca el input
        postal_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
        )
        time.sleep(2)
        
        postal_input.clear()
        postal_input.send_keys(codigo_postal)
        print(f"✓ Código postal {codigo_postal} introducido")
        time.sleep(2)
        
        # Buscar y hacer click en el botón
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "Continuar" in btn.text or "continuar" in btn.text:
                btn.click()
                print("✓ Click en continuar")
                break
        
        # Esperar a que desaparezca el modal y se cargue el contenido
        time.sleep(5)
        
        # Esperar a que aparezcan productos
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
        print("✓ Contenido cargado")
        
        return True
        
    except Exception as e:
        print(f"Error con código postal: {e}")
        return False

def scroll_completo(driver, pausas=10):
    """Hace scroll completo para cargar todo el contenido lazy-loading"""
    print("Realizando scroll para cargar productos...")
    
    # Scroll hacia abajo poco a poco
    for i in range(pausas):
        altura_actual = driver.execute_script("return window.pageYOffset")
        altura_total = driver.execute_script("return document.body.scrollHeight")
        
        # Scroll gradual
        driver.execute_script(f"window.scrollTo(0, {altura_total * (i+1) / pausas});")
        time.sleep(1.5)
        print(f"  Scroll {i+1}/{pausas}")
    
    # Volver arriba
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    print("✓ Scroll completado")

def extraer_productos_selenium(driver):
    """Extrae productos usando Selenium directamente (no BeautifulSoup)"""
    productos = []
    
    try:
        print("Buscando productos con Selenium...")
        
        # Esperar que haya al menos un botón de producto (tarjetas clickeables)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
        
        time.sleep(3)
        
        # Buscar todos los botones que podrían ser productos
        # En SPAs de React, los productos suelen ser botones clickeables
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Total botones encontrados: {len(buttons)}")
        
        # Intentar encontrar contenedores de productos
        posibles_selectores = [
            "button[class*='product']",
            "div[class*='product']",
            "article",
            "li[class*='product']",
            "[data-test*='product']",
            "button[aria-label]"
        ]
        
        elementos_producto = []
        for selector in posibles_selectores:
            try:
                elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                if elementos and len(elementos) > 5:  # Debe haber varios productos
                    elementos_producto = elementos
                    print(f"✓ Usando selector: {selector} ({len(elementos)} elementos)")
                    break
            except:
                continue
        
        if not elementos_producto:
            print("⚠ No se encontraron productos con selectores automáticos")
            print("Intentando método alternativo...")
            
            # Método alternativo: buscar cualquier elemento con texto que parezca precio
            all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
            print(f"Elementos con '€': {len(all_elements)}")
        
        # Procesar elementos encontrados
        for idx, elemento in enumerate(elementos_producto[:100], 1):  # Limitar a 100 primeros
            try:
                # Obtener todo el texto del elemento
                texto_completo = elemento.text
                
                if not texto_completo or len(texto_completo.strip()) < 3:
                    continue
                
                # Dividir el texto en líneas
                lineas = [l.strip() for l in texto_completo.split('\n') if l.strip()]
                
                if len(lineas) < 2:  # Debe tener al menos nombre y precio
                    continue
                
                producto = {
                    'elemento_id': idx,
                    'texto_completo': texto_completo,
                    'nombre': 'N/A',
                    'precio': 'N/A',
                    'precio_unidad': 'N/A',
                    'marca': 'N/A',
                }
                
                # Intentar extraer información estructurada
                for linea in lineas:
                    if '€' in linea:
                        if 'precio' not in producto or producto['precio'] == 'N/A':
                            producto['precio'] = linea
                        elif '/' in linea or 'kg' in linea.lower() or 'ud' in linea.lower():
                            producto['precio_unidad'] = linea
                
                # El nombre suele ser la primera línea sin €
                for linea in lineas:
                    if '€' not in linea and len(linea) > 3:
                        producto['nombre'] = linea
                        break
                
                # Buscar imagen dentro del elemento
                try:
                    img = elemento.find_element(By.TAG_NAME, "img")
                    producto['imagen_url'] = img.get_attribute("src") or img.get_attribute("data-src")
                except:
                    producto['imagen_url'] = 'N/A'
                
                # Solo agregar si tiene nombre y precio
                if producto['nombre'] != 'N/A' and producto['precio'] != 'N/A':
                    productos.append(producto)
                    if idx <= 5:  # Mostrar los primeros 5 para debug
                        print(f"  Producto {idx}: {producto['nombre'][:40]} - {producto['precio']}")
                
            except Exception as e:
                continue
        
        print(f"✓ Productos extraídos: {len(productos)}")
        
    except Exception as e:
        print(f"Error extrayendo productos: {e}")
        import traceback
        traceback.print_exc()
    
    return productos

def obtener_categorias_recursivo(driver, url_base):
    """Obtiene TODAS las categorías y subcategorías de forma recursiva"""
    todas_categorias = set()
    categorias_procesadas = set()
    categorias_por_procesar = [url_base]
    
    print("Explorando estructura de categorías...")
    
    while categorias_por_procesar:
        url_actual = categorias_por_procesar.pop(0)
        
        if url_actual in categorias_procesadas:
            continue
        
        try:
            print(f"\n  Explorando: {url_actual}")
            driver.get(url_actual)
            time.sleep(4)
            
            # Buscar todos los enlaces
            enlaces = driver.find_elements(By.TAG_NAME, "a")
            
            nuevas_encontradas = 0
            for enlace in enlaces:
                try:
                    href = enlace.get_attribute("href")
                    if href and "/categories/" in href:
                        # Limpiar la URL
                        href_limpia = href.split('?')[0].split('#')[0]
                        
                        if href_limpia not in todas_categorias and href_limpia not in categorias_procesadas:
                            todas_categorias.add(href_limpia)
                            categorias_por_procesar.append(href_limpia)
                            nuevas_encontradas += 1
                except:
                    continue
            
            categorias_procesadas.add(url_actual)
            print(f"    ✓ Nuevas categorías: {nuevas_encontradas}")
            print(f"    Total acumulado: {len(todas_categorias)}")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            categorias_procesadas.add(url_actual)
            continue
    
    # Filtrar para quedarnos solo con las URLs finales (hojas del árbol)
    categorias_finales = []
    todas_categorias_list = sorted(list(todas_categorias))
    
    for cat in todas_categorias_list:
        # Verificar si es una categoría "hoja" (no tiene otras que empiecen con ella)
        es_hoja = True
        for otra_cat in todas_categorias_list:
            if otra_cat != cat and otra_cat.startswith(cat + '/'):
                es_hoja = False
                break
        
        if es_hoja:
            categorias_finales.append(cat)
    
    print(f"\n✓ Exploración completa:")
    print(f"  - Total categorías encontradas: {len(todas_categorias)}")
    print(f"  - Categorías finales (con productos): {len(categorias_finales)}")
    
    return categorias_finales

def scrape_mercadona(codigo_postal='46001', categorias_especificas=None, headless=False):
    """
    Scraping completo de Mercadona
    
    Args:
        codigo_postal: Código postal de la tienda
        categorias_especificas: Lista de URLs de categorías específicas o None para todas
        headless: Ejecutar sin interfaz gráfica
    """
    driver = setup_driver(headless=headless)
    todos_productos = []
    
    try:
        print("="*70)
        print("SCRAPING MERCADONA - SPA REACT")
        print("="*70)
        
        # Acceder a la página principal
        print(f"\n1. Accediendo a la home de Mercadona...")
        driver.get("https://tienda.mercadona.es/categories/")
        time.sleep(5)
        
        # Manejar código postal
        print(f"\n2. Configurando código postal...")
        if not manejar_codigo_postal(driver, codigo_postal):
            print("⚠ Continuando sin código postal...")
        
        # Obtener categorías
        if categorias_especificas:
            print(f"\n3. Usando categorías específicas proporcionadas...")
            categorias = categorias_especificas
        else:
            print(f"\n3. Obteniendo TODAS las categorías automáticamente...")
            categorias = obtener_todas_categorias_desde_home(driver)
        
        if len(categorias) > 0:
            print(f"\n4. Procesando {len(categorias)} categorías con productos...")
            
            # Mostrar todas las categorías que se van a procesar
            print("\n" + "="*70)
            print("CATEGORÍAS A PROCESAR:")
            print("="*70)
            for i, cat in enumerate(categorias, 1):
                nombre_cat = cat.split('/categories/')[-1]
                print(f"  {i:3d}. {nombre_cat}")
            
            print("\n" + "="*70)
            print("INICIANDO EXTRACCIÓN DE PRODUCTOS")
            print("="*70 + "\n")
            
            for idx, cat_url in enumerate(categorias, 1):
                nombre_cat = cat_url.split('/categories/')[-1]
                print(f"\n{'='*70}")
                print(f"[{idx}/{len(categorias)}] Categoría: {nombre_cat}")
                print(f"{'='*70}")
                
                try:
                    driver.get(cat_url)
                    time.sleep(5)
                    
                    scroll_completo(driver, pausas=8)
                    productos = extraer_productos_selenium(driver)
                    
                    # Agregar info de categoría
                    for p in productos:
                        p['categoria_url'] = cat_url
                        p['categoria_nombre'] = nombre_cat
                    
                    todos_productos.extend(productos)
                    print(f"✓ Productos en esta categoría: {len(productos)}")
                    print(f"✓ Total acumulado: {len(todos_productos)} productos")
                    
                except Exception as e:
                    print(f"✗ Error en categoría {nombre_cat}: {e}")
                    continue
        else:
            print("\n⚠ No se encontraron categorías para procesar")
        
    except Exception as e:
        print(f"\n✗ Error general: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print(f"\n{'='*70}")
        print(f"SCRAPING FINALIZADO")
        print(f"Total productos obtenidos: {len(todos_productos)}")
        print(f"{'='*70}\n")
    
    return todos_productos

def guardar_csv(productos, nombre_archivo='mercadona_productos_2.csv'):
    """Guarda productos en CSV"""
    if not productos:
        print("⚠ No hay productos para guardar")
        return
    
    df = pd.DataFrame(productos)
    df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    
    print(f"\n{'='*70}")
    print(f"✓ Archivo guardado: {nombre_archivo}")
    print(f"✓ Total productos: {len(productos)}")
    
    # Agrupar por categoría
    if 'categoria_nombre' in df.columns:
        print(f"\n{'='*70}")
        print("PRODUCTOS POR CATEGORÍA:")
        print('='*70)
        resumen = df.groupby('categoria_nombre').size().sort_values(ascending=False)
        for cat, count in resumen.items():
            print(f"  {cat}: {count} productos")
    
    print(f"\n{'='*70}")
    print("MUESTRA DE DATOS:")
    print('='*70)
    print(df.head(10).to_string(max_colwidth=50))
    print(f"\n{'='*70}")
    print("ESTADÍSTICAS:")
    print(f"{'='*70}")
    print(f"Productos únicos (por nombre): {df['nombre'].nunique()}")
    print(f"Productos con precio: {(df['precio'] != 'N/A').sum()}")
    print(f"Productos con imagen: {(df['imagen_url'] != 'N/A').sum()}")
    if 'categoria_nombre' in df.columns:
        print(f"Categorías diferentes: {df['categoria_nombre'].nunique()}")

if __name__ == "__main__":
    # CONFIGURACIÓN
    codigo_postal = "46001"  # Valencia - Cambia según tu ubicación
    
    print("\n" + "="*70)
    print("MERCADONA WEB SCRAPER - TODAS LAS CATEGORÍAS")
    print("="*70)
    print(f"Código postal: {codigo_postal}")
    print(f"Modo: Exploración automática desde la home")
    print("="*70 + "\n")
    
    """
    # OPCIÓN 1: Scrapear TODAS las categorías automáticamente
    productos = scrape_mercadona(
        codigo_postal=codigo_postal,
        categorias_especificas=None,  # None = buscar todas automáticamente
        headless=True  # False = ver navegador, True = más rápido
    )
    """
    
    # OPCIÓN 2: Scrapear solo categorías específicas (comenta la opción 1 y descomenta esto)
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
        # Añade más URLs aquí...
    ]
    productos = scrape_mercadona(
        codigo_postal=codigo_postal,
        categorias_especificas=categorias_manual,
        headless=True
    )
    
    if productos:
        guardar_csv(productos)
        print("\n" + "="*70)
        print("✓ ¡SCRAPING COMPLETADO EXITOSAMENTE!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("⚠ NO SE OBTUVIERON PRODUCTOS")
        print("="*70)
        print("\nPosibles causas:")
        print("  1. La página tiene protección anti-scraping")
        print("  2. La estructura HTML cambió")
        print("  3. Problemas de red o timeout")
        print("\nSugerencias:")
        print("  - Ejecuta con headless=False para ver qué ocurre")
        print("  - Aumenta los tiempos de espera (time.sleep)")
        print("  - Verifica el código postal sea válido")