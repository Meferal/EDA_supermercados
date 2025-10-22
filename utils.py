import re
import pandas as pd


def parse_product_format(text):
    """
    Extrae y normaliza valores numéricos de formatos de productos.
    
    Reglas:
    - Si hay valores entre paréntesis, usar ese valor
    - Si hay dos números separados por 'x', multiplicarlos
    - Si el resultado es > 100, dividir entre 1000
    
    Args:
        text (str): Texto del formato del producto
        
    Returns:
        float: Valor numérico normalizado
    """
    if not isinstance(text, str):
        return None
    
    # Buscar números entre paréntesis
    parentesis = re.search(r'\(([0-9]+(?:[.,][0-9]+)?)\s*[a-zA-Z]*\)', text)
    if parentesis:
        valor = float(parentesis.group(1).replace(',', '.'))
        return valor / 1000 if valor > 100 else valor
    
    # Buscar patrón de multiplicación (ej: "2 x 2" o "12 latas x 330")
    multiplicacion = re.search(r'(\d+(?:[.,]\d+)?)\s*x\s*(\d+(?:[.,]\d+)?)', text, re.IGNORECASE)
    if multiplicacion:
        num1 = float(multiplicacion.group(1).replace(',', '.'))
        num2 = float(multiplicacion.group(2).replace(',', '.'))
        valor = num1 * num2
        return valor / 1000 if valor > 100 else valor
    
    # Buscar cualquier número (con opción de decimales)
    numeros = re.findall(r'\d+(?:[.,]\d+)?', text)
    if numeros:
        valor = float(numeros[0].replace(',', '.'))
        return valor / 1000 if valor > 100 else valor
    
    return None

# Aplicar a un DataFrame
# df['valor_normalizado'] = df['formato'].apply(parse_product_format)


# Método 1: Extraer la última palabra/palabras como marca
def extraer_marca_simple(nombre):
    """Extrae la última palabra como marca"""
    if pd.isna(nombre):
        return None
    return nombre.split()[-1]


# Método 2: Extraer después de palabras clave comunes
def extraer_marca_avanzada(nombre):
    """
    Extrae la marca considerando patrones comunes:
    - Después de preposiciones (de, con, sabor, etc.)
    - Última palabra si es capitalizada
    """
    if pd.isna(nombre):
        return None
    
    # Dividir en palabras
    palabras = nombre.split()
    
    # Si hay pocas palabras, tomar la última
    if len(palabras) <= 2:
        return palabras[-1]
    
    # Buscar después de palabras clave comunes
    palabras_clave = ['sabor', 'de', 'con', 'para', 'sin', 'en', 'a']
    
    # Recorrer desde el final
    for i in range(len(palabras)-1, -1, -1):
        palabra = palabras[i]
        # Si la palabra anterior es una palabra clave y esta empieza con mayúscula
        if i > 0 and palabras[i-1].lower() in palabras_clave:
            # La marca probablemente es todo lo que viene después
            return ' '.join(palabras[i:])
        # Si llegamos a una palabra que probablemente sea marca (mayúscula o final)
        if i == len(palabras)-1 or palabra[0].isupper():
            continue
    
    # Por defecto, tomar la última palabra
    return palabras[-1]


# Método 3: Usando un diccionario de marcas conocidas (RECOMENDADO)
def extraer_marca_con_diccionario(nombre, marcas_conocidas):
    """
    Busca marcas conocidas en el nombre del producto
    Este es el método más preciso si tienes un listado de marcas
    """
    if pd.isna(nombre):
        return 'Desconocida'
    
    nombre_lower = nombre.lower()
    
    # Buscar marca conocida (de más específica a menos)
    for marca in sorted(marcas_conocidas, key=len, reverse=True):
        if marca.lower() in nombre_lower:
            return marca
    
    # Si no encuentra ninguna, usar método simple
    return "Desconocida"


# Lista de marcas que aparecen en tus datos
marcas_conocidas = [
    # Marcas blancas y distribución
    'Hacendado', 'Deliplus', 'Bosque Verde',
    
    # Aguas y bebidas sin alcohol
    'Bronchales', 'Cortes', 'Bezoya', 'Nestlé Aquarel', 'Font Vella', 
    'Solán de Cabras', 'Lanjarón', 'Vichy Catalan', 'San Pellegrino',
    'La Casera', 'Fonter', 'La Casa', 'Aquarius', 'Iso drink', 'nestle'
    'Fuze Tea', 'Simon Life', 'Sunny Delight', 'Bifrutas', 'Danacol',
    
    # Refrescos y colas
    'Coca-Cola', 'Fanta', 'Sprite', 'Schweppes', 'Bitter Kas',
    
    # Bebidas energéticas
    'Monster', 'Red Bull', 'Burn', 'Enervit Sport',
    
    # Cervezas
    'Heineken', 'Amstel', 'Mahou', 'San Miguel', 'Steinburg', 
    'Voll-Damm', 'Krombacher', 'Estrella Galicia', 'El Águila', 
    'Alhambra', 'Falke', 'Turia', '1897', '1906',
    
    # Bebidas alcohólicas y licores
    'Larios', 'Beefeater', 'Seagram\'s', 'Tanqueray', 'Glivery',
    'Kingerly & Sons', 'Convidado de Baco', 'Terry', 'Cutty Sark',
    'Ballantine\'s', 'Johnnie Walker', 'J&B', 'James Webb', 
    'Grand Old Parr', 'Negrita', 'La Recompensa', 'Ron Barceló', 
    'Malibu', 'Royal Swan', 'Puente Pazos', 'Knebep', 'Cassalla Cerveró',
    'Tenis', 'Dama Mayor', 'Ricard Pastis de Marseille', 'Limiñana',
    'Franzini', 'Jägermeister', 'Del Patriarca', 'Maronti', 'Martini',
    'Aperol', 'Campari', 'Cerol',
    
    # Sidras y cavas
    'El Mayu', 'Polián', 'El Lagar', 'Cabré & Sabaté', 
    'Señorío De Requena', 'Jaume Serra', 'Anna Codorníu', 'Freixenet',
    'Viña Secret Brut',
    
    # Vinos
    'Casón Histórico', 'Don Simón', 'Marina Alta', 'Fidencio',
    'Pazo de Orantes', 'Semiluna', 'Mar de Uvas', 'Arribeño',
    'Abadía Mantrús', 'Condado de Teón', 'El Pescaito', 
    'Finca La Distinguida', 'Mig Segle', 'Corredera', 
    'Castillo de Salobreña', 'Piccolo Giovanni', 'DulZ.Ze',
    'Hypatia', 'ValdeSalud', 'Dominio de Borgia', 'Elegido',
    'Masía de Altigón', 'El Coto', 'Comportillo', 'Cune',
    'Coto de Imaz', 'Pieza Rey', 'Viña Albali', 'Pata Negra',
    'Señorío de los Llanos', '13 Hectáreas', 'Borsao', 
    'El Mandamás The Guv\'Nor', 'Davida', 'Torre Oria', 
    'Para Pecar', 'Arc de Pedra', 'Diamante', 'Ponce de Albayda',
    'Finca La Malcriada', 'Dolce Cueva', 'Arteso Clarete',
    
    # Chocolates y cacao
    'Nesquik', 'ColaCao', 'La Chocolatera', 'Valor', 'Milka', 
    'Kit-Kat', 'Huesitos', 'Meivel', 'Pintarolas',
    
    # Golosinas y caramelos
    'Halls', 'Pifarré', 'Cerdán', 'Royal Mints', 'Trolli', 'Vidal',
    'Dulciora',
    
    # Salsas y condimentos
    'Hellmann\'s', 'Ligeresa', 'Musa', 'Chovi', 'Hida', 'J-Lek',
    'Casa Juncal', 'Polasal',
    
    # Aceitunas y encurtidos
    'Huerta de Barros', 'Campo Nature', 'Olives García',
    
    # Snacks
    'Lay\'s', 'Pringles', 'Cheetos', 'Munchos', 'Anitin', 'Bachman',
    'Galbusera',
    
    # Arroces y pastas
    'La Fallera', 'Sabroz', 'Bia', 'Sabor', 'Luengo', 'Felicia',
    'Armando', 'Pagani',
    
    # Café y té
    'Dolce Gusto', 'Bonka', 'Cafés Valiente', 'Marcilla', 'Climent',
    'Nescafé', 'Campina', 'PG tips', 'Amanda', 'Tassimo',
    
    # Productos infantiles y bebé
    'Hero Solo', 'Peques 3 Puleva', 'Puleva', 'Nestlé', 'Nativa',
    'Nidina', 'Dodot', 'Nenuco',
    
    # Cereales y galletas
    'Kellogg\'s', 'Corn Flakes', 'Choco Krispies', 'Brüggen',
    'Special K', 'Nature Valley', 'Enervit Sport', 'Tosta Rica',
    'Lotus Biscoff', 'Oreo', 'Chips Ahoy',
    
    # Embutidos y carnes
    'Campofrío', 'Noel', 'La Carloteña', 'Coren', 'La Selva',
    'Schara', 'El Pozo', 'Cárnicas Gállego', 'Revilla', 'Bricio',
    'De León', 'Incarlopsa', 'Jamcal', 'Paletas Marpa', 
    'Antonio Álvarez', 'Embutidos Pajariel', 'Costa Brava',
    'El Cierzo', 'Covap', 'Andares', 'La Piara', 'L\'Illa especialidades',
    'Can Pere Joan', 'Rogusa', 'La Hacienda del ibérico', 'Juan del Roble',
    
    # Quesos
    'Zanetti', 'Punteiro', 'Holland Corona', 'Holland', 'Entrepinares',
    'Babybel', 'La vaca que ríe', 'Philadelphia', 'Burgo de Arias',
    'Marcillat', 'Liptana', 'Plaisir de Roy', 'Montesinos', 'Richesmonts',
    
    # Pescado y marisco
    'Royal Greenland', 'MareDeus', 'Nortindal', 'Fiesta', 'Camós',
    
    # Productos preparados
    'Convite', 'Jamar', 'Starlux', 'Avecrem', 'Knorr', 'Hengstenberg',
    'Danet', 'Gallina Blanca',
    
    # Higiene y cosmética
    'TRESemmé', 'O\'lysee', 'Ultrex', 'Colorcor', 'Color Sensation',
    'Color Mask', 'Nelly', 'Giorgi', 'Elnett', 'Fructis', 'Syoss',
    'Nivea', 'Nivea Men', 'Axe', 'L\'Oréal', 'Atlantia', 'Dove',
    'Facial Clean', 'Montagne Jeunesse', 'Khanya', 'Wilkinson',
    'Sanex', 'Byly', 'Tulipán Negro', 'Deonat', 'Rexona', 'Lactovit',
    'Natural Honey', 'La Toja', 'Magno', 'Heno de Pravia', 'Pantene',
    'Excellence Creme', 'Gillette', 'Elvive',
    
    # Higiene bucal
    'Colgate', 'Oral-B', 'Signal', 'Sensodyne', 'Parodontax',
    'Benfix', 'Listerine',
    
    # Higiene femenina
    'Evax', 'Ausonia', 'Carefree', 'Tampax',
    
    # Perfumería
    'S3', 'Rose Nude', 'Elección', '9.60', 'Como Tú', 'Chanson d\'Eau',
    'Ikiru', 'Vuela', 'Soplo', 'Blue Shine', 'My Soul', 'Verissime',
    'Cosmic Shine', 'Éclant', 'Monogotas', 'Boem', 'Women\'Secret',
    'Sun Med', 'Colagen', 'Vitaldin', 'Moldex', 'On',
    
    # Limpieza del hogar
    'Ariel', 'Micolor', 'Beltrán', 'Estrella', 'Orache', 'Krisul',
    'Las 3 Brujas', 'Bref', 'KH-7', 'Vitroclen', 'Pronto', 'Aladdin',
    'Finish', 'Somat', 'Alibérico', 'Fairy'
    
    # Varios
    'Roura', 'Encendido', 'Tres Estrellas', 'Clipper', 'Yak',
    'Rimmel London', 'Dulcita', 'Delikuit', 'Quartett', 'Single',
    'Natura', 'Krislin', 'IGP', 'Listo para Comer', 'Granzoo', 'Compy',
    'Nuske', 'Durex', 'Royal', 'Levital'
]


# APLICAR A TODO TU DATAFRAME
# ============================
# Para tu caso, usa:
# df['marca'] = df['nombre_producto'].apply(extraer_marca_simple)
#
# O mejor aún, crea tu lista de marcas conocidas y usa:
# df['marca'] = df['nombre_producto'].apply(
#     lambda x: extraer_marca_con_diccionario(x, marcas_conocidas)
# )


def extract_product_format(product_name):
    """
    Extrae el formato de un producto de supermercado.
    
    Parámetros:
    -----------
    product_name : str
        Nombre del producto del cual extraer el formato
        
    Retorna:
    --------
    str : El formato extraído o None si no se encuentra
    
    Ejemplos:
    ---------
    >>> extract_product_format('cerveza budweiser lager lata 33 cl')
    'lata 33 cl'
    
    >>> extract_product_format('toallitas bebe fresh aloe vera carrefour baby 6x80 uds')
    '6x80 uds'
    
    >>> extract_product_format('agua mineral bezoya 15 l')
    '15 l'
    """
    if pd.isna(product_name):
        return None
    
    product_name = str(product_name).lower()
    
    # Lista de patrones ordenados por prioridad (más específicos primero)
    patterns = [
        # Packs complejos: "pack de 12 latas de 33 cl", "mini pack 10 latas 20 cl"
        r'((?:mini\s+)?pack\s+(?:de\s+)?\d+\s+(?:latas?|botellas?|briks?|unidades?|uds?)(?:\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))?)',
        
        # Pack con cantidad y unidad: "pack de 2 unidades de 250 ml"
        r'(pack\s+de\s+\d+\s+unidades?\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))',
        
        # Pack simple: "pack de 4 bolsitas de 100 g"
        r'(pack\s+de\s+\d+\s+\w+\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg|ud|uds))',
        
        # Múltiples simples: "6x80 uds", "3x72"
        r'(\d+\s*x\s*\d+(?:\s*(?:ud|uds|unidades?))?)',
        
        # Con tipo de envase: "lata 33 cl", "botella 1 l", "brik 1 l"
        r'((?:lata|botella|brik|tarrito|bolsita|frasco|sobre|paquete)\s+(?:de\s+)?\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))',
        
        # Volumen o peso simple al final: "1 l", "500 ml", "100 g"
        r'(\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg)(?:\s|$))',
        
        # Unidades simples: "80 ud", "64 uds"
        r'(\d+\s*(?:ud|uds|unidades?)(?:\s|$))',
    ]
    
    # Buscar el primer patrón que coincida
    for pattern in patterns:
        match = re.search(pattern, product_name)
        if match:
            format_str = match.group(1).strip()
            return format_str
    
    return None


def extract_all_formats(product_name):
    """
    Extrae TODOS los formatos encontrados en un producto (puede haber varios).
    
    Parámetros:
    -----------
    product_name : str
        Nombre del producto del cual extraer los formatos
        
    Retorna:
    --------
    list : Lista con todos los formatos encontrados
    
    Ejemplo:
    --------
    >>> extract_all_formats('toallitas bebe fresh aloe vera carrefour baby 6x80 uds')
    ['6x80 uds']
    """
    if pd.isna(product_name):
        return []
    
    product_name = str(product_name).lower()
    
    # Patrón general que captura todos los formatos posibles
    pattern = r'(?:(?:mini\s+)?pack\s+(?:de\s+)?\d+\s+(?:latas?|botellas?|briks?|unidades?|uds?)(?:\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))?)|(?:pack\s+de\s+\d+\s+unidades?\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))|(?:pack\s+de\s+\d+\s+\w+\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg|ud|uds))|(?:\d+\s*x\s*\d+(?:\s*(?:ud|uds|unidades?))?)|(?:(?:lata|botella|brik|tarrito|bolsita|frasco|sobre|paquete)\s+(?:de\s+)?\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))|(?:\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))|(?:\d+\s*(?:ud|uds|unidades?))'
    
    matches = re.findall(pattern, product_name)
    return [m.strip() for m in matches] if matches else []


def categorize_format(format_str):
    """
    Categoriza un formato extraído.
    
    Parámetros:
    -----------
    format_str : str
        El formato a categorizar
        
    Retorna:
    --------
    str : La categoría del formato
    """
    if pd.isna(format_str):
        return 'sin_formato'
    
    format_str = str(format_str).lower()
    
    if 'pack' in format_str:
        return 'pack'
    elif any(word in format_str for word in ['lata', 'botella', 'brik', 'tarrito', 'bolsita', 'frasco', 'sobre']):
        return 'envase_con_cantidad'
    elif re.search(r'\d+\s*x\s*\d+', format_str):
        return 'multiple'
    elif re.search(r'\d+[\.,]?\d*\s*(l|cl|ml)', format_str):
        return 'volumen'
    elif re.search(r'\d+[\.,]?\d*\s*(g|kg)', format_str):
        return 'peso'
    elif re.search(r'\d+\s*(ud|uds|unidades?)', format_str):
        return 'unidades'
    else:
        return 'otro'


def calculate_total_quantity(format_str):
    """
    Calcula la cantidad total de un formato y la convierte a unidades estándar (ud, Kg, L).
    
    Conversiones:
    - Volumen: todo se convierte a Litros (L)
    - Peso: todo se convierte a Kilogramos (Kg)
    - Unidades: se mantienen como unidades (ud)
    
    Parámetros:
    -----------
    format_str : str
        El formato extraído del producto
        
    Retorna:
    --------
    float : La cantidad total en la unidad estándar, o None si no se puede calcular
    
    Ejemplos:
    ---------
    >>> calculate_total_quantity('80 ud')
    80.0
    
    >>> calculate_total_quantity('6x80 uds')
    480.0
    
    >>> calculate_total_quantity('pack de 3 paquetes de 80 ud')
    240.0
    
    >>> calculate_total_quantity('pack de 3 unidades de 200 ml')
    0.6
    
    >>> calculate_total_quantity('pack de 2 unidades de 235 g')
    0.47
    
    >>> calculate_total_quantity('1500 ml')
    1.5
    
    >>> calculate_total_quantity('36 cl')
    0.36
    """
    if pd.isna(format_str) or format_str == '':
        return None
    
    format_str = str(format_str).lower().strip()
    
    # Patrón 1: Packs complejos tipo "pack de X unidades de Y ml/g/l/cl/kg"
    pattern_pack_complex = r'pack\s+de\s+(\d+)\s+(?:unidades?|paquetes?|latas?|botellas?|briks?)\s+de\s+(\d+[\.,]?\d*)\s*(ml|cl|l|g|kg|ud|uds)'
    match = re.search(pattern_pack_complex, format_str)
    if match:
        multiplier = float(match.group(1))
        quantity = float(match.group(2).replace(',', '.'))
        unit = match.group(3)
        
        total = multiplier * quantity
        return convert_to_standard_unit(total, unit)
    
    # Patrón 2: Múltiples tipo "6x80 uds" o "100 x 6"
    pattern_multiple = r'(\d+)\s*x\s*(\d+)\s*(?:(ml|cl|l|g|kg|ud|uds|unidades?))?'
    match = re.search(pattern_multiple, format_str)
    if match:
        num1 = float(match.group(1))
        num2 = float(match.group(2))
        unit = match.group(3) if match.group(3) else 'l'  # Asume litros si no hay unidad
        
        total = num1 * num2
        return convert_to_standard_unit(total, unit)
    
    # Patrón 3: Pack simple tipo "pack de 12 latas de 33 cl"
    pattern_pack_simple = r'pack\s+de\s+(\d+)\s+(?:latas?|botellas?|briks?)\s+de\s+(\d+[\.,]?\d*)\s*(ml|cl|l|g|kg)'
    match = re.search(pattern_pack_simple, format_str)
    if match:
        multiplier = float(match.group(1))
        quantity = float(match.group(2).replace(',', '.'))
        unit = match.group(3)
        
        total = multiplier * quantity
        return convert_to_standard_unit(total, unit)
    
    # Patrón 4: Con envase tipo "lata 33 cl", "botella 1 l"
    pattern_container = r'(?:lata|botella|brik|tarrito|bolsita|frasco|sobre|paquete)\s+(?:de\s+)?(\d+[\.,]?\d*)\s*(ml|cl|l|g|kg)'
    match = re.search(pattern_container, format_str)
    if match:
        quantity = float(match.group(1).replace(',', '.'))
        unit = match.group(2)
        return convert_to_standard_unit(quantity, unit)
    
    # Patrón 5: Cantidad simple tipo "1500 ml", "36 cl", "80 ud"
    pattern_simple = r'(\d+[\.,]?\d*)\s*(ml|cl|l|g|kg|ud|uds|unidades?)'
    match = re.search(pattern_simple, format_str)
    if match:
        quantity = float(match.group(1).replace(',', '.'))
        unit = match.group(2)
        return convert_to_standard_unit(quantity, unit)
    
    return None


def convert_to_standard_unit(quantity, unit):
    """
    Convierte una cantidad a la unidad estándar correspondiente.
    
    Parámetros:
    -----------
    quantity : float
        La cantidad a convertir
    unit : str
        La unidad actual (ml, cl, l, g, kg, ud, uds)
        
    Retorna:
    --------
    float : La cantidad convertida a la unidad estándar
    """
    unit = unit.lower()
    
    # Conversiones de volumen a Litros
    if unit == 'ml':
        return round(quantity / 1000, 3)
    elif unit == 'cl':
        return round(quantity / 100, 3)
    elif unit == 'l':
        return round(quantity, 3)
    
    # Conversiones de peso a Kilogramos
    elif unit == 'g':
        return round(quantity / 1000, 3)
    elif unit == 'kg':
        return round(quantity, 3)
    
    # Unidades se mantienen igual
    elif unit in ['ud', 'uds', 'unidades', 'unidad']:
        return round(quantity, 0)
    
    return quantity


def get_unit_type(format_str):
    """
    Determina el tipo de unidad estándar del formato.
    
    Parámetros:
    -----------
    format_str : str
        El formato extraído del producto
        
    Retorna:
    --------
    str : 'L' para litros, 'Kg' para kilogramos, 'ud' para unidades, None si no se puede determinar
    """
    if pd.isna(format_str) or format_str == '':
        return None
    
    format_str = str(format_str).lower()
    
    # Buscar unidades de volumen
    if re.search(r'\b(ml|cl|l)\b', format_str):
        return 'L'
    
    # Buscar unidades de peso
    elif re.search(r'\b(g|kg)\b', format_str):
        return 'Kg'
    
    # Buscar unidades
    elif re.search(r'\b(ud|uds|unidades?)\b', format_str):
        return 'ud'
    
    return None


# Ejemplo de uso completo
if __name__ == "__main__":
    # Datos de ejemplo
    test_cases = [
        ('80 ud', 80.0, 'ud'),
        ('6x80 uds', 480.0, 'ud'),
        ('pack de 3 paquetes de 80 ud', 240.0, 'ud'),
        ('pack de 3 unidades de 200 ml', 0.6, 'L'),
        ('pack de 2 unidades de 235 g', 0.47, 'Kg'),
        ('pack de 2 unidades de 50 ml', 0.1, 'L'),
        ('1500 ml', 1.5, 'L'),
        ('100 x 6', 600.0, 'L'),  # Nota: este asume L por defecto
        ('36 cl', 0.36, 'L'),
        ('lata 33 cl', 0.33, 'L'),
        ('botella 1 l', 1.0, 'L'),
        ('brik 1 l', 1.0, 'L'),
        ('pack de 12 latas de 33 cl', 3.96, 'L'),
        ('800 g', 0.8, 'Kg'),
        ('1 kg', 1.0, 'Kg'),
    ]
    
    print("PRUEBAS DE LA FUNCIÓN:")
    print("="*80)
    print(f"{'Formato de entrada':<40} {'Esperado':<12} {'Calculado':<12} {'Unidad':<8} {'OK'}")
    print("="*80)
    
    for format_str, expected, expected_unit in test_cases:
        calculated = calculate_total_quantity(format_str)
        unit = get_unit_type(format_str)
        ok = "✓" if abs(calculated - expected) < 0.01 and unit == expected_unit else "✗"
        print(f"{format_str:<40} {expected:<12} {calculated:<12} {unit:<8} {ok}")
    
    print("\n" + "="*80)
    print("EJEMPLO CON DATAFRAME:")
    print("="*80)
    
    # Crear DataFrame de ejemplo
    df = pd.DataFrame({
        'producto': [
            'toallitas bebe fres aloe vera carrefour 80 ud',
            'toallitas bebe fresh aloe vera carrefour baby 6x80 uds',
            'preparado lacteo infantil de crecimiento brik 1 l',
            'cerveza budweiser lager lata 33 cl',
            'cerveza san miguel especial pack de 12 latas de 33 cl',
            'preparado lacteo infantil pack de 3 unidades de 200 ml',
            'tarrito de verduritas con pollo 235 g',
            'agua mineral bezoya 1500 ml'
        ]
    })
    
    # Extraer formato (usando la función del script anterior)
    def extract_product_format(product_name):
        if pd.isna(product_name):
            return None
        product_name = str(product_name).lower()
        patterns = [
            r'((?:mini\s+)?pack\s+(?:de\s+)?\d+\s+(?:latas?|botellas?|briks?|unidades?|uds?)(?:\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))?)',
            r'(pack\s+de\s+\d+\s+unidades?\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))',
            r'(pack\s+de\s+\d+\s+\w+\s+de\s+\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg|ud|uds))',
            r'(\d+\s*x\s*\d+(?:\s*(?:ud|uds|unidades?))?)',
            r'((?:lata|botella|brik|tarrito|bolsita|frasco|sobre|paquete)\s+(?:de\s+)?\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg))',
            r'(\d+[\.,]?\d*\s*(?:l|cl|ml|g|kg)(?:\s|$))',
            r'(\d+\s*(?:ud|uds|unidades?)(?:\s|$))',
        ]
        for pattern in patterns:
            match = re.search(pattern, product_name)
            if match:
                return match.group(1).strip()
        return None
    
    df['formato'] = df['producto'].apply(extract_product_format)
    df['cantidad_total'] = df['formato'].apply(calculate_total_quantity)
    df['unidad'] = df['formato'].apply(get_unit_type)
    
    print(df[['producto', 'formato', 'cantidad_total', 'unidad']].to_string())