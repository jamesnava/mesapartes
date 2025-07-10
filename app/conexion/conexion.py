import pyodbc

class Conexion(object):
	def __init__(self):
		self.servidor="localhost"
		self.baseDatos="bd_documentario"
		self.Usuario="SALA"
		self.driver='{SQL Server}'
		self.clave="HSRA.2024"
		self.conn=None

	def __enter__(self):
		try:			
			self.conn=pyodbc.connect(f"""DRIVER={self.driver};SERVER={self.servidor};DATABASE={self.baseDatos};UID={self.Usuario};PWD={self.clave}""")
			return self.conn
		except pyodbc.Error as e:
			print(f"Error al conectarse {e}")

	def __exit__(self,exc_type,exc_val,exc_tb):		
		if self.conn:
			self.conn.close()


