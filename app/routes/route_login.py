from flask import Blueprint, render_template,redirect,url_for,request
from flask_login import login_user,login_required,current_user,logout_user
from app.formularios.formlogin.form_auth import LoginForm
from app.modelos.QueryLogin import QueryL
from werkzeug.security import check_password_hash,generate_password_hash




auth_bp=Blueprint('auth',__name__,url_prefix='/auth')


@auth_bp.route('/logout')
def salir():
	logout_user()
	return redirect(url_for('auth.inicio'))

@auth_bp.route('/',methods=['POST','GET'])
def inicio():
	if current_user.is_authenticated:
		return redirect(url_for('main.principal'))
		
	mensaje=""	
	form=LoginForm()
	#consulta roles
	if request.method=='POST':
		usuario=form.usuario.data
		clave=form.clave.data
		recordar=form.recordar.data
		sql=f"""SELECT U.Id_Usuario,U.Nombre_Usuario,U.Contrasena,U.Id_Oficina,U.Estado,O.nombre_oficina FROM USUARIO
	 		AS U INNER JOIN Oficina AS O ON U.Id_Oficina=O.Id_Oficina WHERE U.Nombre_Usuario=?"""
		obj_query=QueryL()		
		user=obj_query.cargarUsuario(sql,(usuario,))
				
		if user:
			if  user.estado=='ACTIVO':
				if  (user and check_password_hash(user.password,clave)):
					login_user(user,remember=recordar)			
					next_page = request.args.get('next')			
					return redirect(next_page or url_for('main.principal'))

				else:
					mensaje="Clave o Usuario son incorrectas"
			else:
				mensaje="Usuario Inactivo"
		else:
			mensaje="Credenciales inválidos!!"		
			

	return render_template('/start/inicio.html',form=form,mensaje=mensaje)