from flask import Blueprint,redirect,render_template,url_for,request,jsonify
from flask_login import current_user,login_required
from app.modelos.QueryDocumento import QueryDocumentos
from app.utilidades.utilidades import GeneracionCodigoOficina

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
def insertOficina():
	objconsulta=QueryDocumentos()
	codigo=request.form.get('codigo')
	nombre=request.form.get('nombre')
	padre=request.form.get('padre')
	responsable=request.form.get('responsable')

	sql="""INSERT INTO Oficina(Id_Oficina,nombre_oficina,Id_Oficina_Padre,Responsable) VALUES(?,?,?,?)"""
	params=(codigo,nombre,padre,responsable)
	numero=objconsulta.InsertDataGeneral(sql,params)

	return [numero]
@oficina_bp.route('/updateoficina',methods=['POST'])
def updateOficina():
	objconsulta=QueryDocumentos()
	codigo=request.form.get('codigo')
	name=request.form.get('nombre')
	responsable=request.form.get('responsable')
	padre=request.form.get('codigopadre')
	sql="""UPDATE Oficina SET nombre_oficina=?,Responsable=?,Id_Oficina_Padre=? WHERE Id_Oficina=?"""
	params=(name,responsable,padre,codigo)
	#actualiza datos
	numero=objconsulta.InsertDataGeneral(sql,params)
	return [numero]


