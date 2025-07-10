from flask import Blueprint, render_template, redirect, url_for, request
from app.modelos.QueryMain import QueryGeneral

rol_bp=Blueprint('rol',__name__,url_prefix='/rol')

@rol_bp.route('/listrol')
def rol():
	return render_template('/roles/rol.html')

@rol_bp.route('/listmodulo')
def modulo():
	objectQuery=QueryGeneral()
	sql="SELECT * FROM Modulo"
	rows=objectQuery.GetData(sql)	
	return render_template('/roles/modulo.html',datos=rows)

@rol_bp.route('/insertmodulo',methods=['POST'])
def insertModulo():
	objectQuery=QueryGeneral()	
	denominacion=request.form.get('denominacion')
	tabla=request.form.get('tabla')
	if tabla=='modulo':	
		sql="INSERT INTO Modulo(Nombre_Permiso) VALUES(?)"
		nro=objectQuery.InsertData(sql,(denominacion,))
	return [nro]
