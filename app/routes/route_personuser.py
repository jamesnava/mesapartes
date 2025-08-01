from flask import Blueprint, render_template, redirect,request,jsonify,request
from flask_login import current_user,login_required
from app.modelos.QueryDocumento import QueryDocumentos

puser_bp=Blueprint('puser',__name__,url_prefix='/puser')

@puser_bp.route('/tuser')
def templateUser():
	objConsulta=QueryDocumentos()
	sql="""SELECT P.Nombre,P.ApellidoPaterno,P.ApellidoMaterno,P.Dni,U.Nombre_Usuario,U.Id_Usuario,U.Estado,O.nombre_oficina
			FROM USUARIO as U INNER JOIN PERSONA AS P ON U.Dni=P.Dni INNER JOIN Oficina AS O ON U.Id_Oficina=O.Id_Oficina"""
	rows=objConsulta.ConsultaMainDoc(sql)
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	return render_template('/personas/usuario.html',info=datos,rows=rows)

@puser_bp.route('/tperson')
def templatePerson():
	objConsulta=QueryDocumentos()
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	sql="SELECT TOP 50 * FROM PERSONA"
	rows=objConsulta.ConsultaMainDoc(sql)

	return render_template('/personas/persona.html',info=datos,rows=rows)

@puser_bp.route('/insertperson',methods=['POST'])
def insertperson():
	objConsulta=QueryDocumentos()
	dni=request.form.get('dnip')
	nombre=request.form.get('nombrep')	
	apellidop=request.form.get('apellidopp')
	apellidom=request.form.get('apellidomp')
	email=request.form.get('emailp')
	telefono=request.form.get('telefonop')
	distrito=request.form.get('distritop')
	direccion=request.form.get('direccionp')
	sql="""INSERT INTO PERSONA(Dni,Nombre,ApellidoPaterno,ApellidoMaterno,Email,Telefono,Distrito,Direccion) VALUES(?,?,?,?,?,?,?,?)"""

	#comprobar si existe
	sql_confirmar="SELECT * FROM PERSONA WHERE Dni=?"
	controlador=0
	rows_corroborar=objConsulta.ConsultaMainDocParams(sql_confirmar,(dni,))
	if rows_corroborar:
		controlador=-1
	else:
		params=(dni,nombre,apellidop,apellidom,email,telefono,distrito,direccion)
		controlador=objConsulta.InsertDataGeneral(sql,params)
	return [controlador]

@puser_bp.route('/updateperson',methods=['POST'])
def actualizarpersona():
	objConsulta=QueryDocumentos()
	dni=request.form.get('dni')

	sql="SELECT * FROM PERSONA WHERE Dni=?"
	rows=objConsulta.ConsultaMainDocParams(sql,(dni,))
	datos=[{'dni':val.Dni,'nombre':val.Nombre,'apellidop':val.ApellidoPaterno,'apellidom':val.ApellidoMaterno,'email':val.Email,'telefono':val.Telefono,'distrito':val.Distrito,'direccion':val.Direccion} for val in rows]
	
	return jsonify({'datos':datos})

@puser_bp.route('/saveupdate',methods=['POST'])
def saveupdatepersona():
	objConsulta=QueryDocumentos()	
	nombre=request.form.get('nombrepe')
	dni=request.form.get('dnipe')
	apellidop=request.form.get('apellidoppe')
	apellidom=request.form.get('apellidompe')
	email=request.form.get('emailpe')
	telefono=request.form.get('telefonope')
	distrito=request.form.get('distritope')
	direccion=request.form.get('direccionpe')
	sql="""UPDATE PERSONA SET Nombre=?,ApellidoPaterno=?,ApellidoMaterno=?,Email=?,Telefono=?,Distrito=?,Direccion=? WHERE Dni=?"""
	params=(nombre,apellidop,apellidom,email,telefono,distrito,direccion,dni)
	numero=objConsulta.InsertDataGeneral(sql,params)
	return [numero]

@puser_bp.route('/deleteperson',methods=['POST'])
def deleteperson():
	numero=0
	try:
		objConsulta=QueryDocumentos()
		dni=request.form.get('dni')
		sql="DELETE FROM PERSONA WHERE Dni=?"
		numero=objConsulta.InsertDataGeneral(sql,(dni))
	except Exception as e:
		raise e	
	return [numero]

@puser_bp.route('/searchperson',methods=['POST'])
def searchperson():
	objConsulta=QueryDocumentos()
	valor=request.form.get('datos')

	sql="SELECT * FROM PERSONA WHERE Dni LIKE ? OR Nombre LIKE ?"
	params=("%"+valor+"%","%"+valor+"%")
	datos=None
	try:
		rows=objConsulta.ConsultaMainDocParams(sql,params)
		datos=[{'dni':val.Dni,'nombre':val.Nombre,'apellidop':val.ApellidoPaterno,'apellidom':val.ApellidoMaterno,'email':val.Email,'telefono':val.Telefono,'distrito':val.Distrito,'direccion':val.Direccion} for val in rows]
		
	except Exception as e:
		raise e
	return jsonify({'datos':datos})

@puser_bp.route('/searchpersonwithoutuser',methods=['POST'])
def searchpersonwithoutuser():
	objConsulta=QueryDocumentos()
	datos=request.form.get('datos')
	sql="""SELECT P.Dni,P.Nombre,P.ApellidoPaterno,P.ApellidoMaterno FROM 
	PERSONA AS P LEFT JOIN USUARIO AS U ON P.Dni=U.Dni WHERE U.Id_Usuario IS NULL AND P.Dni LIKE ? OR P.ApellidoPaterno LIKE ? """
	params=("%"+datos+"%","%"+datos+"%")
	datos=None
	try:
		rows=objConsulta.ConsultaMainDocParams(sql,params)
		datos=[{'dni':val.Dni,'datos':val.Nombre+" "+val.ApellidoPaterno+" "+val.ApellidoMaterno} for val in rows]

	except Exception as e:
		raise e
	return jsonify({'datos':datos})

@puser_bp.route('/searchoficinauser',methods=['POST'])
def searchoficinauser():
	objConsulta=QueryDocumentos()
	parametro=request.form.get('datos')
	sql="SELECT Id_Oficina,nombre_oficina FROM Oficina WHERE nombre_oficina LIKE ?"
	params=("%"+parametro+"%",)
	datos=None
	try:
		rows=objConsulta.ConsultaMainDocParams(sql,params)
		datos=[{'codigo':val.Id_Oficina,'nombre':val.nombre_oficina} for val in rows]

	except Exception as e:
		raise e

	return jsonify({'datos':datos})

@puser_bp.route('/loadroluser',methods=['POST'])
def loadRolUser():
	objConsulta=QueryDocumentos()
	sql="SELECT * FROM Roles"
	datos=None
	try:
		rows=objConsulta.ConsultaMainDoc(sql)
		datos=[{'idrol':val.Id_Rol,'nombre':val.Nombre_Rol} for val in rows]
	except Exception as e:
		raise e
	return jsonify({'datos':datos})






	



