"""
Web Scraper Optimizado para Tienda Consum
Extrae productos del HTML renderizado y navega por categorías
Requiere: pip install selenium beautifulsoup4 pandas webdriver-manager
"""

import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConsumScraperOptimizado:
    def __init__(self, headless=True):
        """Inicializa el scraper"""
        self.base_url = "https://tienda.consum.es/es"
        self.products = []
        self.driver = None
        self.headless = headless
        
        # Categorías principales de Consum
        self.categorias = [
            {'nombre': 'Despensa', 'url': f'{self.base_url}/c/despensa/2811?orderById=5&page=1'},
            {'nombre': 'Bebidas', 'url': f'{self.base_url}/c/bebidas/1690?orderById=5&page=1'},
            {'nombre': 'Frescos', 'url': f'{self.base_url}/c/frescos/2812?orderById=5&page=1'},
            {'nombre': 'Horno', 'url': f'{self.base_url}/c/horno/4108?orderById=5&page=1'},
            {'nombre': 'Platos preparados', 'url': f'{self.base_url}/c/platos-preparados/1833?orderById=5&page=1'},
            {'nombre': 'Congelados', 'url': f'{self.base_url}/c/congelados/1783?orderById=5&page=1'},
            {'nombre': 'Ecológico y saludable', 'url': f'{self.base_url}/c/ecologico-saludable/5281?orderById=5&page=1'},
            {'nombre': 'Infantil', 'url': f'{self.base_url}/c/infantil/2297?orderById=5&page=1'},
            {'nombre': 'Droguería', 'url': f'{self.base_url}/c/drogueria/1239?orderById=5&page=1'},
            {'nombre': 'Cuidado personal', 'url': f'{self.base_url}/c/cuidado/2814?orderById=5&page=1'},
            {'nombre': 'Mascotas', 'url': f'{self.base_url}/c/mascotas/2469?orderById=5&page=1'},
            {'nombre': 'Bazar', 'url': f'{self.base_url}/c/bazar/1486?orderById=5&page=1'}
        ]
        
    def setup_driver(self):
        """Configura el driver de Selenium"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✓ Driver configurado correctamente")
        except Exception as e:
            logger.error(f"Error configurando driver: {e}")
            raise
    
    def wait_for_products(self, timeout=15):
        """Espera a que los productos se carguen"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "cmp-widget-product"))
            )
            time.sleep(2)  # Espera adicional para asegurar carga completa
            return True
        except Exception as e:
            logger.warning(f"Timeout esperando productos: {e}")
            return False
    
    def extract_products_from_page(self, category_name):
        """Extrae productos de la página actual"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Buscar widgets de productos
            product_widgets = soup.find_all('cmp-widget-product')
            
            if not product_widgets:
                logger.warning(f"No se encontraron productos en {category_name}")
                return 0
            
            productos_extraidos = 0
            
            for widget in product_widgets:
                try:
                    # Extraer ID del producto
                    product_id = widget.get('id', '').replace('grid-widget-', '')
                    
                    # Buscar nombre y marca dentro de lib-product-info-name
                    name_component = widget.find('lib-product-info-name')
                    marca = ""
                    nombre = ""
                    codigo = ""
                    
                    if name_component:
                        # Marca (p con class u-size--20)
                        marca_elem = name_component.find('p', class_='u-size--20')
                        if marca_elem:
                            marca = marca_elem.get_text(strip=True)
                        
                        # Nombre (h1 con class u-title-3)
                        nombre_elem = name_component.find('h1', class_='u-title-3')
                        if nombre_elem:
                            nombre = nombre_elem.get_text(strip=True)
                        
                        # Código del producto
                        codigo_elem = name_component.find('span', string=re.compile('Código producto'))
                        if codigo_elem and codigo_elem.parent:
                            codigo_text = codigo_elem.parent.get_text(strip=True)
                            codigo_match = re.search(r':\s*(\d+)', codigo_text)
                            if codigo_match:
                                codigo = codigo_match.group(1)
                    
                    # Precio dentro de lib-product-info-price
                    precio_actual = ""
                    precio_anterior = ""
                    price_component = widget.find('lib-product-info-price')
                    
                    if price_component:
                        # Precio con oferta (tachado)
                        precio_oferta = price_component.find('span', class_='product-info-price__offer')
                        if precio_oferta:
                            precio_anterior = precio_oferta.get_text(strip=True)
                        
                        # Precio actual
                        precio_elem = price_component.find('span', class_='product-info-price__price')
                        if precio_elem:
                            precio_actual = precio_elem.get_text(strip=True)
                    
                    # URL de la imagen
                    imagen_url = ""
                    img_elem = widget.find('img', class_='image-component__image')
                    if img_elem:
                        imagen_url = img_elem.get('src', '')
                    
                    # URL del producto
                    producto_url = ""
                    link_elem = widget.find('a', class_='u-no-link')
                    if link_elem:
                        href = link_elem.get('href', '')
                        if href:
                            producto_url = f"https://tienda.consum.es{href}"
                    
                    # Información de promoción
                    promocion = ""
                    promo_component = widget.find('lib-product-info-promotions')
                    if promo_component:
                        promo_title = promo_component.find('span', class_='product-info-promotions__column--title')
                        if promo_title:
                            promocion = promo_title.get_text(strip=True)
                    
                    # Precio por unidad (ej: €/Kg)
                    precio_unidad = ""
                    precio_unidad_elem = name_component.find('p', class_='product-info-name--price') if name_component else None
                    if precio_unidad_elem:
                        precio_unidad = precio_unidad_elem.get_text(strip=True)
                    
                    # Patrocinado
                    patrocinado = bool(widget.find('div', class_='widget-product__sponsored--label'))
                    
                    if nombre or codigo:  # Solo guardar si tiene nombre o código
                        product = {
                            'codigo_producto': codigo or product_id,
                            'marca': marca,
                            'nombre': nombre,
                            'categoria': category_name,
                            'precio_actual': precio_actual,
                            'precio_anterior': precio_anterior,
                            'precio_por_unidad': precio_unidad,
                            'promocion': promocion,
                            'patrocinado': 'Sí' if patrocinado else 'No',
                            'imagen_url': imagen_url,
                            'producto_url': producto_url,
                            'fecha_extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        self.products.append(product)
                        productos_extraidos += 1
                
                except Exception as e:
                    logger.debug(f"Error parseando producto: {e}")
                    continue
            
            logger.info(f"✓ Extraídos {productos_extraidos} productos de {category_name}")
            return productos_extraidos
            
        except Exception as e:
            logger.error(f"Error extrayendo productos: {e}")
            return 0
    
    def get_total_pages(self):
        """Obtiene el número total de páginas"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Buscar el texto "de X" en el paginador
            paginator = soup.find('cmp-tol-dropdown-paginator')
            if paginator:
                span_elements = paginator.find_all('span')
                for span in span_elements:
                    text = span.get_text(strip=True)
                    if text.startswith('de '):
                        total_pages = int(text.replace('de ', ''))
                        return total_pages
            
            return 1
        except Exception as e:
            logger.warning(f"No se pudo determinar número de páginas: {e}")
            return 1
    
    def navigate_to_next_page(self, current_page):
        """Navega a la siguiente página usando la URL directamente"""
        try:
            # Obtener la URL actual
            current_url = self.driver.current_url
            
            # Construir URL de la siguiente página
            if '?' in current_url:
                # Ya tiene parámetros
                if 'page=' in current_url:
                    # Reemplazar el número de página
                    next_url = re.sub(r'page=\d+', f'page={current_page + 1}', current_url)
                else:
                    # Agregar parámetro de página
                    next_url = f"{current_url}&page={current_page + 1}"
            else:
                # No tiene parámetros
                next_url = f"{current_url}?page={current_page + 1}"
            
            logger.info(f"Navegando a: {next_url}")
            self.driver.get(next_url)
            time.sleep(3)  # Esperar a que cargue
            
            return self.wait_for_products()
            
        except Exception as e:
            logger.error(f"Error navegando a página siguiente: {e}")
            return False
    
    def scrape_category(self, categoria, max_pages=None):
        """Extrae todos los productos de una categoría"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Procesando categoría: {categoria['nombre']}")
        logger.info(f"{'='*60}")
        
        try:
            # Navegar a la categoría
            self.driver.get(categoria['url'])
            
            if not self.wait_for_products():
                logger.warning(f"No se cargaron productos en {categoria['nombre']}")
                return
            
            # Obtener número total de páginas
            total_pages = self.get_total_pages()
            pages_to_scrape = min(total_pages, max_pages) if max_pages else total_pages
            
            logger.info(f"Total de páginas detectadas: {total_pages}")
            logger.info(f"Páginas a procesar: {pages_to_scrape}")
            
            # Extraer productos de cada página
            for page_num in range(1, pages_to_scrape + 1):
                logger.info(f"Procesando página {page_num}/{pages_to_scrape}")
                
                # Extraer productos de la página actual
                productos_en_pagina = self.extract_products_from_page(categoria['nombre'])
                
                if productos_en_pagina == 0:
                    logger.warning(f"No se extrajeron productos de la página {page_num}")
                
                # Si no es la última página, navegar a la siguiente
                if page_num < pages_to_scrape:
                    if not self.navigate_to_next_page(page_num):
                        logger.warning(f"No se pudo navegar a la página {page_num + 1}")
                        break
                    
                time.sleep(1)  # Pequeña pausa entre páginas
                
        except Exception as e:
            logger.error(f"Error procesando categoría {categoria['nombre']}: {e}")
            import traceback
            traceback.print_exc()
    
    def scrape_all(self, max_categories=None, max_pages_per_category=None):
        """Ejecuta el scraping completo"""
        logger.info("=" * 70)
        logger.info("INICIANDO SCRAPING DE TIENDA CONSUM")
        logger.info("=" * 70)
        
        try:
            self.setup_driver()
            
            # Seleccionar categorías a procesar
            categorias_a_procesar = self.categorias[:max_categories] if max_categories else self.categorias
            
            for idx, categoria in enumerate(categorias_a_procesar, 1):
                logger.info(f"\n[{idx}/{len(categorias_a_procesar)}] Iniciando: {categoria['nombre']}")
                self.scrape_category(categoria, max_pages=max_pages_per_category)
                time.sleep(2)  # Pausa entre categorías
            
            logger.info("\n" + "=" * 70)
            logger.info("SCRAPING COMPLETADO")
            logger.info(f"Total productos extraídos: {len(self.products)}")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Error durante el scraping: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Driver cerrado")
    
    def save_to_csv(self, filename=None):
        """Guarda los productos en CSV"""
        if not self.products:
            logger.warning("⚠ No hay productos para guardar")
            return False
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"productos_consum_{timestamp}.csv"
        
        try:
            df = pd.DataFrame(self.products)
            
            # Ordenar por categoría y marca
            df = df.sort_values(['categoria', 'marca', 'nombre'])
            
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"\n✓ Productos guardados en: {filename}")
            logger.info(f"  Total registros: {len(self.products)}")
            
            return True
        except Exception as e:
            logger.error(f"Error guardando CSV: {e}")
            return False
    
    def get_statistics(self):
        """Muestra estadísticas del scraping"""
        if not self.products:
            logger.info("No hay productos para analizar")
            return
        
        df = pd.DataFrame(self.products)
        
        print("\n" + "=" * 70)
        print("ESTADÍSTICAS DEL SCRAPING")
        print("=" * 70)
        print(f"Total de productos: {len(df)}")
        print(f"\nProductos por categoría:")
        print(df['categoria'].value_counts().to_string())
        
        if df['marca'].notna().any():
            print(f"\nTop 10 marcas:")
            print(df['marca'].value_counts().head(10).to_string())
        
        # Productos con oferta
        productos_oferta = df[df['precio_anterior'] != ''].shape[0]
        print(f"\nProductos en oferta: {productos_oferta}")
        
        # Productos patrocinados
        patrocinados = df[df['patrocinado'] == 'Sí'].shape[0]
        print(f"Productos patrocinados: {patrocinados}")
        
        print("=" * 70)


def main():
    """Función principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║          WEB SCRAPER OPTIMIZADO TIENDA CONSUM               ║
    ║          Extrae productos de todas las categorías            ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Crear scraper (headless=True por defecto)
    scraper = ConsumScraperOptimizado(headless=True)
    
    # OPCIONES DE CONFIGURACIÓN:
    
    # Opción 1: Scraping completo (TODAS las categorías, TODAS las páginas)
    # ⚠️ ADVERTENCIA: Puede tardar HORAS y generar decenas de miles de productos
    # scraper.scrape_all()
    
    # Opción 2: Scraping de prueba (1 categoría, 3 páginas) - RECOMENDADO PARA PRUEBAS
    scraper.scrape_all(max_categories=100, max_pages_per_category=300)
    
    # Opción 3: Todas las categorías, pero máximo 10 páginas por categoría
    # scraper.scrape_all(max_pages_per_category=10)
    
    # Opción 4: Todas las categorías, todas las páginas (SCRAPING COMPLETO)
    # scraper.scrape_all()
    
    # Guardar resultados
    scraper.save_to_csv()
    
    # Mostrar estadísticas
    scraper.get_statistics()
    
    print("\n✓ Proceso completado exitosamente")


if __name__ == "__main__":
    main()