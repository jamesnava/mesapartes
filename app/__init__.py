from flask import Flask,redirect,url_for
from config import Config
from flask_login import LoginManager,current_user
from app.routes.route_login import auth_bp
from app.routes.route_principal import main_bp
from app.routes.route_roles import rol_bp
from app.routes.route_documentos import documento_bp
from app.routes.route_oficina import oficina_bp
from app.routes.route_personuser import puser_bp
from app.routes.route_reporte import reporte_bp
from app.modelos.QueryLogin import QueryL
from app.modelos.QueryDocumento import QueryDocumentos
#from app.grafico.dash_reporte import init_dashboard


app=Flask(__name__)
app.config.from_object(Config)
login=LoginManager()
login.init_app(app)
login.login_view='auth.inicio'


@login.user_loader
def load_user(id_user):
	obj_consulta=QueryL()
	sql=f"""SELECT U.Id_Usuario,U.Nombre_Usuario,U.Contrasena,U.Id_Oficina,U.Estado,O.nombre_oficina FROM USUARIO
	 AS U INNER JOIN Oficina AS O ON U.Id_Oficina=O.Id_Oficina WHERE U.Id_Usuario=?"""	 
	user=obj_consulta.cargarUsuario(sql,(id_user,))	
	return user


@app.context_processor
def inject_menue():
	permisos=[]

	objConsulta=QueryDocumentos()
	sql_rol="""SELECT M.Nombre_Permiso FROM Roles AS R INNER JOIN ROL_PERMISO AS RP ON R.Id_Rol=RP.Id_Rol
				INNER JOIN Modulo AS M ON RP.Id_Permiso=M.Id_Permiso INNER JOIN USUARIO AS U ON U.Id_Rol=R.Id_Rol 
				WHERE U.Id_Usuario=?"""
	if current_user.is_authenticated:
		try:
			rows=objConsulta.ConsultaMainDocParams(sql_rol,(current_user.id))
		except Exception as e:
			raise e
		permisos=[val.Nombre_Permiso for val in rows]
		
	
	return dict(permisos=permisos)


app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(rol_bp)
app.register_blueprint(documento_bp)
app.register_blueprint(oficina_bp)
app.register_blueprint(puser_bp)
app.register_blueprint(reporte_bp)

#registrando dashboard
#init_dashboard(app)

