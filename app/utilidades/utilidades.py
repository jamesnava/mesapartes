import random
import string
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def GeneracionCodigo(logintud):
	caracteres=string.ascii_letters+string.digits
	codigo=''.join(random.choice(caracteres) for i in range(logintud))
	return codigo
def GeneracionCodigoOficina(logintud):
	caracteres=string.ascii_uppercase
	codigo=''.join(random.choice(caracteres) for i in range(logintud))
	return codigo

def generarTicket(rows,oficinas,direccion):	
	w, h = 80 * mm, 200 * mm
	c = canvas.Canvas(direccion, pagesize=(w, h))

	c.drawString(20, h - 30, "Resumen del ingreso del documento")
	c.drawString(20, h - 60, f"Dni Emisor: {rows[0].Dni}")
	c.drawString(20, h - 80, f"Emisor: {rows[0].emisor}")
	c.drawString(20, h - 100, f"Fecha: {rows[0].Fecha_Creacion}")
	c.drawString(20, h - 120, f"Asunto: {rows[0].Asunto}")
	c.drawString(20, h - 140, f"Tipo: {rows[0].Nombre_TipoDocumento}")
	c.drawString(20, h - 160, f"Prioridad: {rows[0].Nombre_Prioridad}")
	c.line(0, h-165, w, h-165)
	
	y=180
	c.setFont("Helvetica", 10)
	for val in oficinas:
		c.drawString(10,h-y,f"Destino: {val[0].lower()}")
		c.drawString(30,h-y-15,f"Codigo Seguimiento: {val[1]}")
		y=y+25
	c.showPage()
	c.save()
