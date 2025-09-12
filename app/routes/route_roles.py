from flask import Blueprint, render_template, redirect, url_for, request,jsonify
from flask_login import current_user,login_required
from app.modelos.QueryMain import QueryGeneral

rol_bp=Blueprint('rol',__name__,url_prefix='/rol')

@rol_bp.route('/listrol')
def rol():
	objConsulta=QueryGeneral()
	sql="SELECT * FROM Roles"
	sqlmodulo="SELECT * FROM Modulo"
	try:
		rows=objConsulta.GetData(sql)
		rows_modulo=objConsulta.GetData(sqlmodulo)
	except Exception as e:
		raise e	
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	return render_template('/roles/rol.html',info=datos,rows=rows,modulo=rows_modulo)

@rol_bp.route('/listmodulo')
def modulo():
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	objectQuery=QueryGeneral()
	sql="SELECT * FROM Modulo"
	rows=objectQuery.GetData(sql)	
	return render_template('/roles/modulo.html',datos=rows,info=datos)

@rol_bp.route('/insertmodulo',methods=['POST'])
def insertModulo():	
	objectQuery=QueryGeneral()	
	denominacion=request.form.get('denominacion')	
	sql="INSERT INTO Modulo(Nombre_Permiso) VALUES(?)"
	nro=None
	try:
		nro=objectQuery.InsertData(sql,(denominacion,))
	except Exception as e:
		nro=0	
	
	return jsonify(nro)
@rol_bp.route('/delmodulo',methods=['POST'])
def deleteModulo():
	objectQuery=QueryGeneral()
	codigo=request.form.get('codigo')
	sql="DELETE FROM Modulo WHERE Id_Permiso=?"
	controlador=None
	try:
		controlador=objectQuery.InsertData(sql,(codigo,))
	except Exception as e:
		controlador=0

	return jsonify(controlador)

@rol_bp.route('/queryperfildetalle',methods=['POST'])
def consultaperfildetalle():
	rows=[]
	valor=request.form.get('valor')
	sql="SELECT * FROM ROL_PERMISO AS RP INNER JOIN Modulo AS M ON RP.Id_Permiso=M.Id_Permiso WHERE RP.Id_Rol=?"
	objectQuery=QueryGeneral()
	try:
		rows=objectQuery.GetDataParams(sql,(valor,))
	except Exception as e:
		raise e
	datos=[{'id':val.Id_Rol,'idpermiso':val.Id_Permiso,'permiso':val.Nombre_Permiso} for val in rows]
	return jsonify({'datos':datos})

@rol_bp.route('/createperfil',methods=['POST'])
def createprofile():
	datos = request.get_json()
	idrol=datos.get('idrol')
	modulos=datos.get('perfil')
	
	sql="INSERT INTO ROL_PERMISO(Id_Rol,Id_Permiso) VALUES(?,?)"
	sql_del="DELETE FROM ROL_PERMISO WHERE Id_Rol=?"
	objConsulta=QueryGeneral()
	controlador=0
	try:
		nro=objConsulta.InsertData(sql_del,(idrol,))
		for val in modulos:
			objConsulta.InsertData(sql,(idrol,val['id']))
		controlador=1
	except Exception as e:
		controlador=0
		raise e
		
	return jsonify(controlador)
@rol_bp.route('/insertpermiso',methods=['POST'])
def insertpermiso():
	numero=0
	denominacion=request.form.get('denominacion')
	sql="INSERT INTO Roles(Nombre_Rol) VALUES(?)"
	objectQuery=QueryGeneral()
	try:
		numero=objectQuery.InsertData(sql,(denominacion,))
	except Exception as e:
		numero=0
	return jsonify(numero)



