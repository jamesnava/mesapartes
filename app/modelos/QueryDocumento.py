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

	def ConsultaMainDocParamsCon(self,con,sql,params):
		
		try:
			row=[]			
			cursor=con.cursor()
			cursor.execute(sql,params)
			row=cursor.fetchone()
			cursor.close()
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
			print(sql)
			print(e)			
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

	def updatetable(self,con,sql,params):
		cursor=con.cursor()
		try:
			cursor.execute(sql,params)
		except Exception as e:
			print("eror del insert",e)
			raise
		finally:
			cursor.close()
		
		
		


		
