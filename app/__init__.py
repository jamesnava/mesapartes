from flask import Flask
from config import Config
from flask_login import LoginManager
from app.routes.route_login import auth_bp
from app.routes.route_principal import main_bp
from app.routes.route_roles import rol_bp
from app.routes.route_documentos import documento_bp
from app.routes.route_oficina import oficina_bp
from app.routes.route_personuser import puser_bp
from app.modelos.QueryLogin import QueryL


app=Flask(__name__)
app.config.from_object(Config)
login=LoginManager()
login.init_app(app)
login.login_view='auth.inicio'

@login.user_loader
def load_user(id_user):
	obj_consulta=QueryL()
	sql=f"""SELECT * FROM USUARIO WHERE Id_Usuario=?"""	 
	user=obj_consulta.cargarUsuario(sql,(id_user,))	
	return user


app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(rol_bp)
app.register_blueprint(documento_bp)
app.register_blueprint(oficina_bp)
app.register_blueprint(puser_bp)

