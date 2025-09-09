from flask import Blueprint, render_template, redirect,request,jsonify,request
from flask_login import current_user,login_required
from app.modelos.QueryDocumento import QueryDocumentos
from werkzeug.security import generate_password_hash
from app.decoratos import requires_permission
from app.constanst import Permiso

puser_bp=Blueprint('puser',__name__,url_prefix='/puser')

@puser_bp.route('/tuser')
@requires_permission(Permiso.USUARIO)
@login_required
def templateUser():
	objConsulta=QueryDocumentos()
	sql="""SELECT P.Nombre,P.ApellidoPaterno,P.ApellidoMaterno,P.Dni,U.Nombre_Usuario,U.Id_Usuario,U.Estado,O.nombre_oficina
			FROM USUARIO as U INNER JOIN PERSONA AS P ON U.Dni=P.Dni INNER JOIN Oficina AS O ON U.Id_Oficina=O.Id_Oficina"""
	rows=objConsulta.ConsultaMainDoc(sql)
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	return render_template('/personas/usuario.html',info=datos,rows=rows)

@puser_bp.route('/tperson')
@requires_permission(Permiso.PERSONA)
@login_required
def templatePerson():
	objConsulta=QueryDocumentos()
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina}
	sql="SELECT TOP 50 * FROM PERSONA"
	rows=objConsulta.ConsultaMainDoc(sql)

	return render_template('/personas/persona.html',info=datos,rows=rows)

@puser_bp.route('/insertperson',methods=['POST'])
@requires_permission(Permiso.PERSONA)
@login_required
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

	if not (dni.isdigit() and len(dni)==8):
		return jsonify(-2)
	
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
	return jsonify(controlador)

@puser_bp.route('/updateperson',methods=['POST'])
@requires_permission(Permiso.PERSONA)
@login_required
def actualizarpersona():
	objConsulta=QueryDocumentos()
	dni=request.form.get('dni')

	sql="SELECT * FROM PERSONA WHERE Dni=?"
	rows=objConsulta.ConsultaMainDocParams(sql,(dni,))
	datos=[{'dni':val.Dni,'nombre':val.Nombre,'apellidop':val.ApellidoPaterno,'apellidom':val.ApellidoMaterno,'email':val.Email,'telefono':val.Telefono,'distrito':val.Distrito,'direccion':val.Direccion} for val in rows]
	
	return jsonify({'datos':datos})

@puser_bp.route('/saveupdate',methods=['POST'])
@requires_permission(Permiso.PERSONA)
@login_required
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
@requires_permission(Permiso.PERSONA)
@login_required
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
@requires_permission(Permiso.PERSONA)
@login_required
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
@login_required
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
@login_required
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
@login_required
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

@puser_bp.route('/insertsaveuser',methods=['POST'])
def saveUser():

	dni=request.form.get('dni')
	usuario=request.form.get('useruser')
	contrasenia= generate_password_hash(request.form.get('passworduser')) 
	oficina=request.form.get('oficina')
	rol=request.form.get('selectroluser')
	objConsulta=QueryDocumentos()
	#reestriccion
	sql="""SELECT * FROM USUARIO WHERE Dni=? OR Nombre_Usuario=? """
	rows_users=objConsulta.ConsultaMainDocParams(sql,(dni,usuario))
	controlador=None
	if rows_users:
		controlador=-1
	else:
		try:
			sql_insert="""INSERT INTO USUARIO(Nombre_Usuario,Contrasena,Id_Oficina,Id_Rol,Estado,Dni)
			VALUES(?,?,?,?,'ACTIVO',?)"""
			params=(usuario,contrasenia,oficina,rol,dni)
			controlador=objConsulta.InsertDataGeneral(sql_insert,params)
		except Exception as e:
			controlador=0
			print(e)

	return [controlador]

@puser_bp.route('/changestate',methods=['POST'])
@requires_permission(Permiso.USUARIO)
@login_required
def changeState():
	dni=request.form.get('dni')
	sql="UPDATE USUARIO SET Estado=? WHERE Dni=?"
	objConsulta=QueryDocumentos()
	controlador=None
	try:
		rows = objConsulta.ConsultaMainDocParams("SELECT Estado FROM USUARIO WHERE Dni=?",(dni,))
		if rows[0].Estado=="ACTIVO":
			controlador=objConsulta.InsertDataGeneral(sql,('INACTIVO',dni))
		else:
			controlador=objConsulta.InsertDataGeneral(sql,('ACTIVO',dni))

	except Exception as e:
		controlador=0
	return [controlador]

@puser_bp.route('/updateoficinauser',methods=['POST'])
@requires_permission(Permiso.USUARIO)
@login_required
def updateOficinaUser():
	dni=request.form.get('dni')
	codigo=request.form.get('oficina')
	objConsulta=QueryDocumentos()
	controlador=None
	try:
		controlador=objConsulta.InsertDataGeneral("UPDATE USUARIO SET Id_Oficina=? WHERE Dni=?",(codigo,dni))

	except Exception as e:
		controlador=0
		raise e
	return [controlador]

@puser_bp.route('/updatepassworduser',methods=['POST'])
@requires_permission(Permiso.USUARIO)
@login_required
def updatePasswordUser():
	dni=request.form.get('dni')
	clave=generate_password_hash(request.form.get('clave'))
	sql="UPDATE USUARIO SET Contrasena=? WHERE Dni=?"
	objConsulta=QueryDocumentos()
	controlador=None
	try:
		controlador=objConsulta.InsertDataGeneral(sql,(clave,dni))
	except Exception as e:
		controlador=0
		raise e
	return [controlador]

@puser_bp.route('/cargarperfil',methods=['POST'])
@login_required
def cargarperfil():
	sql="SELECT * FROM Roles"
	objConsulta=QueryDocumentos()
	datos=[]
	try:
		rows=objConsulta.ConsultaMainDoc(sql)
		datos=[{'id':val.Id_Rol,'nombre':val.Nombre_Rol} for val in rows]
	except Exception as e:
		raise e

	return jsonify({'datos':datos})

@puser_bp.route('/grabacambioperfil',methods=['POST'])
@login_required
def changeProfile():
	numero=0
	dni=request.form.get('dni')
	idperfil=request.form.get('rol')
	sql="UPDATE USUARIO SET Id_Rol=? WHERE Dni=?"
	objConsulta=QueryDocumentos()
	try:
		numero=objConsulta.InsertDataGeneral(sql,(idperfil,dni))
	except Exception as e:
		numero=0
	return jsonify(numero)




