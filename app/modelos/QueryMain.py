from app.conexion.conexion import Conexion

class QueryGeneral():
	def GetData(self,sql):
		try:
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql)
				rows=cursor.fetchall()
		except Exception as e:
			raise e
		finally:
			if rows:
				return rows
			else:
				return None

	def InsertData(self,sql,params):
		try:
			with Conexion() as con:
				cursor=con.cursor()
				cursor.execute(sql,params)
				cursor.commit()
		except Exception as e:
			raise e
		finally:
			if cursor.rowcount==1:
				return 1
			else:
				return 0

