from flask import Blueprint, render_template,redirect,url_for,request,g,jsonify
from flask_login import current_user,login_required
from app.modelos.QueryLogin import QueryL
from app.modelos.QueryDocumento import QueryDocumentos
from app.decoratos import requires_permission
from app.constanst import Permiso
from werkzeug.security import check_password_hash, generate_password_hash

main_bp=Blueprint('main',__name__,url_prefix='/main')

@main_bp.before_request
def cargar_usuario():
	if current_user.is_authenticated:
		obj_consulta=QueryL()
		sql=f"""SELECT * FROM USUARIO WHERE Id_Usuario=?"""
		g.user=obj_consulta.cargarUsuario(sql,(current_user.id))


@main_bp.route("/principal")
@login_required
def principal():		
	return render_template('/start/main.html',usuario=current_user.username)

@main_bp.route("/roles")
@requires_permission(Permiso.ROL,Permiso.PERMISO)
@login_required
def rolesPermisos():
	return render_template('/roles/menuroles.html')

@main_bp.route('/documentos')
@requires_permission(Permiso.DOCUMENTO)
@login_required
def documentos():
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	return render_template('/documentos/doc_principal.html',datos=datos)

@main_bp.route('/oficinap')
@requires_permission(Permiso.OFICINA)
@login_required
def oficinaplantilla():
	objConsulta=QueryDocumentos()
	sql="SELECT * FROM Oficina"
	rows_consulta=objConsulta.ConsultaMainDoc(sql)
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	return render_template('/oficinas/Oficinas.html',info=datos,rows=rows_consulta)

@main_bp.route('/peruser')
@requires_permission(Permiso.PERSONA,Permiso.USUARIO)
@login_required
def userperson():
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	return render_template('/personas/peruserprincipal.html',info=datos)

@main_bp.route('/changepassword',methods=['POST'])
@login_required
def ChangePassword():
	claveactual=request.form.get('claveactual')
	clave=request.form.get('clave')
	objConsulta=QueryDocumentos()
	numero=0	
	if (check_password_hash(current_user.password,claveactual)):
		sql="UPDATE USUARIO SET Contrasena=? WHERE Id_Usuario=?"
		params=(generate_password_hash(clave),current_user.id)
		try:
			numero=objConsulta.InsertDataGeneral(sql,params)
		except Exception as e:
			numero=0
		
	else:
		numero=-1

	return jsonify(numero)

