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

	def InsertDataIdentity(self,sql,params):
		nuevo_id=0
		try:
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql,params)			
				nuevo_id=cursor.fetchone()[0]
				cursor.commit()
				
		except Exception as e:
			print(e)
			print(sql)
			print(params)
		finally:
			return nuevo_id

	def InsertDataGeneral(self,sql,params):
		numero=0
		try:
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql,params)			
				con.commit()
				numero=cursor.rowcount
				
		except Exception as e:
			print("Error SQL:", sql)
			print("Parámetros:", params)
			print("Mensaje:", e)
		finally:
			return numero


		
