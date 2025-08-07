from app.conexion.conexion import Conexion

class QueryGeneral():
	def GetData(self,sql):
		rows=[]
		try:
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql)
				rows=cursor.fetchall()
		except Exception as e:
			raise e
		finally:
			return rows

	def GetDataParams(self,sql,params):
		rows=[]
		try:
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql,params)
				rows=cursor.fetchall()
		except Exception as e:
			raise e
		finally:
			return rows

	def InsertData(self,sql,params):
		numero=0		
		try:
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql,params)
				con.commit()
				numero=cursor.rowcount
		except Exception as e:
			numero=0
		finally:			
			return numero
		

