from app.conexion.conexion import Conexion
from app.modelos.userModel import User

class QueryL(object):

	def cargarUsuario(self,query,params):
		try:
			#obj_user=User()
			
			with Conexion() as con:				
				cursor=con.cursor()
				cursor.execute(query,params)
				rows=cursor.fetchone()
		except Exception as e:
			print(e)

		finally:
			if rows:
				return User(rows[0],rows[1],rows[2],rows[3])
			else:
				return None