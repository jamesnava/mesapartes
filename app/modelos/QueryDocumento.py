from app.conexion.conexion import Conexion

class QueryDocumentos():
	def ConsultaMainDoc(self,sql):
		try:
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql)
				row=cursor.fetchall()
		except Exception as e:
			print(e)
		finally:
			return row

	def ConsultaMainDocParams(self,sql,params):
		try:
			row=[]
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql,params)
				row=cursor.fetchall()
		except Exception as e:
			print(e)
		finally:
			return row
