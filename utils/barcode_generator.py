from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
import platform
import os

# Configuración
OUTPUT_DIR = "assets/generated_barcodes"
DPI = 300
CM_TO_INCH = 1 / 2.54
WIDTH_CM, HEIGHT_CM = 5.94, 3
TARGET_WIDTH = int(WIDTH_CM * CM_TO_INCH * DPI)
TARGET_HEIGHT = int(HEIGHT_CM * CM_TO_INCH * DPI)
BORDER_RADIUS = 35
BORDER_WIDTH = 3
BORDER_COLOR = "black"
MARGIN = 6
LOGO_RATIO_W = 0.22
LOGO_RATIO_H = 0.32


def get_font(size: int = 25, bold: bool = False):
    """
    Retorna una fuente TrueType compatible según el sistema operativo.
    """
    system = platform.system()

    font_map = {
        "Windows": {
            False: "arial.ttf",
            True: "arialbd.ttf"
        },
        "Linux": {
            False: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            True: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        },
        "Darwin": {
            False: "/System/Library/Fonts/SFNS.ttf",
            True: "/System/Library/Fonts/SFNSRounded-Bold.ttf"
        }
    }

    paths = font_map.get(system, font_map["Linux"])
    font_path = paths[bold]

    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    """Divide el texto en múltiples líneas sin que exceda el ancho máximo."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test_line = f"{current} {word}".strip()
        width = draw.textlength(test_line, font=font)
        if width <= max_width:
            current = test_line
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    return lines


def _create_canvas():
    """Crea el canvas base con borde redondeado."""
    img = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [MARGIN, MARGIN, TARGET_WIDTH - MARGIN, TARGET_HEIGHT - MARGIN],
        radius=BORDER_RADIUS,
        outline=BORDER_COLOR,
        width=BORDER_WIDTH,
    )

    return img, draw


def _generate_base_barcode(codigo: str):
    """Genera el código de barras base."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    sanitized = codigo.replace('/', '_').replace('\\', '_')
    tmp_path = os.path.join(OUTPUT_DIR, f"{sanitized}_temp")
    
    writer = ImageWriter()
    writer.dpi = 600
    writer.module_width = 0.30
    writer.write_text = False
    writer.quiet_zone = 1

    Code128(codigo, writer=writer).save(tmp_path)

    img = Image.open(tmp_path + ".png").convert("RGB")
    os.remove(tmp_path + ".png")
    return img


def _resize_barcode(img):
    """Redimensiona el código de barras si es necesario."""
    max_w = int(TARGET_WIDTH * 0.95)
    max_h = int(TARGET_HEIGHT * 0.55)

    if img.width > max_w or img.height > max_h:
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return img


def _draw_centered_text(draw, text, y, font):
    """Dibuja texto centrado y retorna la siguiente posición Y."""
    text_w = draw.textlength(text, font=font)
    draw.text(((TARGET_WIDTH - text_w) / 2, y), text, fill="black", font=font)
    return y + int(font.size * 1.2)


def _add_logo(canvas_img, logo_path: str):
    """Añade el logo en la esquina inferior izquierda."""
    if not os.path.exists(logo_path):
        return

    logo = Image.open(logo_path).convert("RGBA")

    max_w = int(TARGET_WIDTH * LOGO_RATIO_W)
    max_h = int(TARGET_HEIGHT * LOGO_RATIO_H)

    w, h = logo.size
    scale = min(max_w / w, max_h / h)

    new_w = int(w * scale)
    new_h = int(h * scale)

    logo = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)

    x = int(TARGET_WIDTH * 0.05)
    y = int(TARGET_HEIGHT * 0.9) - logo.height

    canvas_img.paste(logo, (x, y), logo)


def _generate_separator_image(office_name: str):
    """Genera imagen separadora para cambio de oficina."""
    img, draw = _create_canvas()
    
    draw.rectangle(
        [MARGIN, MARGIN, TARGET_WIDTH - MARGIN, TARGET_HEIGHT - MARGIN], 
        outline="black", 
        width=10
    )
    
    font_office = get_font(size=35, bold=True)
    
    lines = wrap_text(draw, f"ÁREA:\n{office_name}", font_office, TARGET_WIDTH * 0.8)
    
    total_text_height = len(lines) * font_office.size * 1.2
    start_y = (TARGET_HEIGHT - total_text_height) / 2
    
    y = start_y
    for line in lines:
        y = _draw_centered_text(draw, line, y, font_office)
        
    buffer = BytesIO()
    img.save(buffer, format="PNG", dpi=(DPI, DPI))
    buffer.seek(0)
    return ImageReader(buffer)


def generate_barcode(codigo: str, title: str = "", logo_path: str = None, 
                      detalle_bien: str = "", save_file: bool = False, 
                      tipo_registro: str = ""):
    """
    Genera una etiqueta de código de barras individual.
    
    Args:
        codigo: Código a generar
        title: Título superior
        logo_path: Ruta del logo
        detalle_bien: Detalle del bien
        save_file: Si True, guarda en disco. Si False, retorna ImageReader
        tipo_registro: Tipo de registro (SIGA/SOBRANTE)
    
    Returns:
        Ruta del archivo o ImageReader
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Canvas base
    canvas_img, draw = _create_canvas()

    # Generar barcode
    barcode_img = _resize_barcode(_generate_base_barcode(codigo))

    # Fuentes
    font_title = get_font(size=25)
    font_detalle = get_font(size=23, bold=True)
    font_oficina = get_font(size=18)

    # Textos
    y = 20
    if title:
        y = _draw_centered_text(draw, title, y, font_title)

    if detalle_bien:
        lines = wrap_text(draw, detalle_bien, font_detalle, TARGET_WIDTH * 0.9)[:2]
        for line in lines:
            y = _draw_centered_text(draw, line, y, font_detalle)

    y += 10
    y = _draw_centered_text(
        draw, "ÁREA / OFICINA: _______________________________________________", y, font_oficina)
    y += 10

    # Pegar barcode
    x = (TARGET_WIDTH - barcode_img.width) // 2
    canvas_img.paste(barcode_img, (x, y + 5))

    # Logo
    if logo_path and os.path.exists(logo_path):
        _add_logo(canvas_img, logo_path)

    # Tipo de registro
    if tipo_registro:
        font_tipo = get_font(size=32, bold=True)
        text_w = draw.textlength(tipo_registro, font=font_tipo)
        x_tipo = TARGET_WIDTH - text_w - 30
        y_tipo = TARGET_HEIGHT - font_tipo.size - 30
        draw.text((x_tipo, y_tipo), tipo_registro, fill="black", font=font_tipo)

    # Guardar o retornar
    if not save_file:
        buffer = BytesIO()
        canvas_img.save(buffer, format="PNG", dpi=(DPI, DPI))
        buffer.seek(0)
        return ImageReader(buffer)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, f"{codigo}.png")
    canvas_img.save(file_path, dpi=(DPI, DPI))
    return file_path


def generate_barcodes_pdf(records, output_filename="codigos_barras.pdf", 
                          progress_callback=None, selected_office=""):
    """
    Genera un PDF con múltiples códigos de barras organizados en formato A4 landscape.
    
    Args:
        records: Lista de tuplas (codigo, detalle_bien, tipo_registro, oficina)
        output_filename: Nombre del archivo de salida
        progress_callback: Función callback(current, total) para progreso
        selected_office: Oficina seleccionada (para el nombre del archivo)
    
    Returns:
        Ruta del archivo PDF generado
    """
    output_dir = "assets/generated_barcodes"
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre del archivo
    if selected_office:
        output_filename = f"codigos_barras_{selected_office}.pdf"
    
    output_pdf = os.path.join(output_dir, output_filename)

    pdf = canvas.Canvas(output_pdf, pagesize=landscape(A4))
    page_width, page_height = landscape(A4)

    cm = 28.35
    cols = 5
    rows = 7

    # Márgenes
    PAGE_MARGIN_X = cm * 0.5
    PAGE_MARGIN_Y = cm * 0.5
    GAP_X = 6
    GAP_Y = 6

    # Área imprimible
    usable_w = page_width - (PAGE_MARGIN_X * 2)
    usable_h = page_height - (PAGE_MARGIN_Y * 2)

    # Tamaño de etiquetas
    label_width = (usable_w - (GAP_X * (cols - 1))) / cols
    label_height = (usable_h - (GAP_Y * (rows - 1))) / rows

    # Posiciones iniciales
    x_start = PAGE_MARGIN_X
    y_start = page_height - PAGE_MARGIN_Y - label_height
    x, y = x_start, y_start

    # Configurar líneas de corte
    pdf.setStrokeColorRGB(0.6, 0.6, 0.6)
    pdf.setLineWidth(0.8)
    pdf.setDash(3, 2)

    # Procesar registros con separadores
    processed_items = []
    last_office = None
    
    for record in records:
        if len(record) == 4:
            codigo, detalle_bien, tipo_registro, oficina = record
        else:
            codigo, detalle_bien, tipo_registro = record
            oficina = "DESCONOCIDO"

        # Insertar separador si cambia la oficina
        if last_office != oficina:
            processed_items.append({"type": "separator", "office": oficina})
        
        processed_items.append({
            "type": "barcode",
            "codigo": codigo,
            "detalle_bien": detalle_bien,
            "tipo_registro": tipo_registro,
            "oficina": oficina
        })
        last_office = oficina

    # Logo path (ajustar según tu estructura)
    logo_path = "utils/logo.png"
    if not os.path.exists(logo_path):
        logo_path = None

    # Generar etiquetas
    for i, item in enumerate(processed_items, 1):
        if item["type"] == "separator":
            img = _generate_separator_image(item["office"])
        else:
            img = generate_barcode(
                item['codigo'],
                title="INVENTARIO DRE HUÁNUCO - 2025",
                detalle_bien=item['detalle_bien'],
                logo_path=logo_path,
                tipo_registro=item['tipo_registro']
            )

        # Dibujar la etiqueta
        pdf.drawImage(img, x, y, width=label_width, height=label_height)

        # Líneas de corte
        col_actual = (i - 1) % cols + 1
        if col_actual < cols:
            line_x = x + label_width + GAP_X / 2
            pdf.line(line_x, y, line_x, y + label_height)

        row_actual = ((i - 1) // cols) % rows + 1
        if row_actual < rows and i + cols <= len(processed_items):
            line_y = y - GAP_Y / 2
            pdf.line(x, line_y, x + label_width, line_y)

        if progress_callback:
            progress_callback(i, len(processed_items))

        # Avance
        x += label_width + GAP_X

        # Salto de fila
        if i % cols == 0:
            x = x_start
            y -= label_height + GAP_Y

        # Nueva página
        if i % (cols * rows) == 0 and i < len(processed_items):
            pdf.showPage()
            pdf.setStrokeColorRGB(0.6, 0.6, 0.6)
            pdf.setLineWidth(0.8)
            pdf.setDash(3, 2)
            x, y = x_start, page_height - PAGE_MARGIN_Y - label_height

    pdf.save()
    return output_pdf
