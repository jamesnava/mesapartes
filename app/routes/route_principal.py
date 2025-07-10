from flask import Blueprint, render_template,redirect,url_for,request,g
from flask_login import current_user,login_required
from app.modelos.QueryLogin import QueryL

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
	return render_template('/start/main.html')

@main_bp.route("/roles")
@login_required
def rolesPermisos():
	return render_template('/roles/menuroles.html')

@main_bp.route('/documentos')
def documentos():
	return render_template('/documentos/doc_principal.html')

