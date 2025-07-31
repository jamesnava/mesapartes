from flask import Blueprint, render_template,redirect,url_for,request,g
from flask_login import current_user,login_required
from app.modelos.QueryLogin import QueryL
from app.modelos.QueryDocumento import QueryDocumentos

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
@login_required
def rolesPermisos():
	return render_template('/roles/menuroles.html')

@main_bp.route('/documentos')
def documentos():
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	return render_template('/documentos/doc_principal.html',datos=datos)

@main_bp.route('/oficinap')
def oficinaplantilla():
	objConsulta=QueryDocumentos()
	sql="SELECT * FROM Oficina"
	rows_consulta=objConsulta.ConsultaMainDoc(sql)

	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	return render_template('/oficinas/Oficinas.html',info=datos,rows=rows_consulta)

