from functools import wraps
from flask import redirect,url_for,flash
from flask_login import current_user
from app.modelos.QueryDocumento import QueryDocumentos

def requires_permission(*permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			if not current_user.is_authenticated:
				return redirect(url_for('auth.inicio'))
			user_permissions=get_user_permissions(current_user.id)

			if not any(p in user_permissions for p in permission):
				flash('No tiene permiso para acceder a esta pagina')
				return redirect(url_for('main.principal'))

			return f(*args,**kwargs)
		return decorated_function
	return decorator

def get_user_permissions(iduser):
	permisos=[]

	objConsulta=QueryDocumentos()
	sql_rol="""SELECT M.Nombre_Permiso FROM Roles AS R INNER JOIN ROL_PERMISO AS RP ON R.Id_Rol=RP.Id_Rol
				INNER JOIN Modulo AS M ON RP.Id_Permiso=M.Id_Permiso INNER JOIN USUARIO AS U ON U.Id_Rol=R.Id_Rol 
				WHERE U.Id_Usuario=?"""
	
	try:
		rows=objConsulta.ConsultaMainDocParams(sql_rol,(iduser))
	except Exception as e:
		raise e
	permisos=[val.Nombre_Permiso for val in rows]
	return permisos