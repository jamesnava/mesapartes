from flask import Blueprint,redirect,render_template,url_for,request,jsonify
from flask_login import current_user,login_required
from app.modelos.QueryDocumento import QueryDocumentos
from app.utilidades.utilidades import GeneracionCodigoOficina
from app.decoratos import requires_permission
from app.constanst import Permiso

oficina_bp=Blueprint('office',__name__,url_prefix='/office')

@oficina_bp.route('/mainoficina')
def oficinaprincipal():
	return render_template('/oficinas/Oficinas.html')

@oficina_bp.route('/gencodigo',methods=['POST'])
def genCodigo():
	objconsulta=QueryDocumentos()
	codigo=None
	while True:
		codigo=GeneracionCodigoOficina(5)
		rows=objconsulta.ConsultaMainDocParams("SELECT * FROM Oficina WHERE Id_Oficina=?",(codigo,))
		if not rows:
			break
	return [codigo]

@oficina_bp.route('/searchkey',methods=['POST'])
def searchResponsable():
	objconsulta=QueryDocumentos()
	valor=request.form.get('valor')
	rows=objconsulta.ConsultaMainDocParams("SELECT * FROM PERSONA WHERE Nombre LIKE ?",('%'+valor+'%',))
	datos=[{'dni':val.Dni,'datos':val.Nombre+" "+val.ApellidoPaterno+" "+val.ApellidoMaterno} for val in rows]	
	return jsonify({'responsable':datos})

@oficina_bp.route('/insertoficina',methods=['POST'])
@login_required
def insertOficina():
	objconsulta=QueryDocumentos()
	codigo=request.form.get('codigo')
	nombre=request.form.get('nombre')
	padre=request.form.get('padre')
	responsable=request.form.get('responsable')

	sql="""INSERT INTO Oficina(Id_Oficina,nombre_oficina,Id_Oficina_Padre,Responsable) VALUES(?,?,?,?)"""
	params=(codigo,nombre,padre,responsable)
	numero=0
	try:
		numero=objconsulta.InsertDataGeneral(sql,params)
	except Exception as e:
		raise e
	
	return jsonify(numero)

@oficina_bp.route('/updateoficina',methods=['POST'])
@login_required
def updateOficina():
	objconsulta=QueryDocumentos()
	codigo=request.form.get('codigo')
	name=request.form.get('nombre')
	responsable=request.form.get('responsable')
	padre=request.form.get('codigopadre')
	sql="""UPDATE Oficina SET nombre_oficina=?,Responsable=?,Id_Oficina_Padre=? WHERE Id_Oficina=?"""
	params=(name,responsable,padre,codigo)

	numero=0
	#actualiza datos
	try:
		numero=objconsulta.InsertDataGeneral(sql,params)
	except Exception as e:
		print(e)
	
	return jsonify(numero)

@oficina_bp.route('/fillupdateoffice',methods=['POST'])
@requires_permission(Permiso.OFICINA)
@login_required
def fillDataOffice():
	codigo=request.form.get('codigo')
	objConsulta=QueryDocumentos()
	sql="""SELECT O2.Id_Oficina,O2.nombre_oficina,P.Dni,P.Nombre,P.ApellidoPaterno,P.ApellidoMaterno FROM Oficina AS O INNER JOIN Oficina AS O2 ON O.Id_Oficina_Padre=O2.Id_Oficina 
	INNER JOIN PERSONA AS P ON O.Responsable=P.Dni WHERE O.Id_Oficina=?"""
	datos=[]
	try:
		rows=objConsulta.ConsultaMainDocParams(sql,(codigo,))
		datos={'codigopadre':rows[0].Id_Oficina,'nombrepadre':rows[0].nombre_oficina,'dni':rows[0].Dni,'datospersonales':rows[0].Nombre+' '+rows[0].ApellidoPaterno+' '+rows[0].ApellidoMaterno}
	except Exception as e:
		raise e
	return jsonify(datos)


