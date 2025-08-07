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
	altura=75
	c.drawImage("app/utilidades/logo.png", 70, h - 60, width=50, height=50)
	c.drawString(20, h - altura, "Resumen del ingreso del documento")
	altura+=30
	c.drawString(20, h - altura, f"Dni Emisor: {rows[0].Dni}")
	altura+=20
	c.drawString(20, h - altura, f"Emisor: {rows[0].emisor}")
	altura+=20
	c.drawString(20, h - altura, f"Fecha: {rows[0].Fecha_Creacion}")
	altura+=20
	c.drawString(20, h - altura, f"Asunto: {rows[0].Asunto}")
	altura+=20
	c.drawString(20, h - altura, f"Tipo: {rows[0].Nombre_TipoDocumento}")
	altura+=20
	c.drawString(20, h - altura, f"Prioridad: {rows[0].Nombre_Prioridad}")
	altura+=5
	c.line(0, h-altura, w, h-altura)
	
	y=altura+20
	c.setFont("Helvetica", 10)
	for val in oficinas:
		c.drawString(10,h-y,f"Destino: {val[0].lower()}")
		c.drawString(30,h-y-15,f"Codigo Seguimiento: {val[1]}")
		y=y+25
	c.showPage()
	c.save()
