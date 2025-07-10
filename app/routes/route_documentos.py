from flask import Blueprint, render_template, redirect, url_for, request,jsonify
from app.formularios.Documentos.formDocumentos import Documentos
from app.modelos.QueryDocumento import QueryDocumentos
from app.utilidades import utilidades

documento_bp=Blueprint('documents',__name__,url_prefix='/documents')

@documento_bp.route('/nuevodoc',methods=['POST'])
def nuevodocumento():
	objConsulta=QueryDocumentos()
	sql="SELECT * FROM Tipo_Documento"
	rowTipodocumento=objConsulta.ConsultaMainDoc(sql)
	sqlTipoPrioridad="SELECT * FROM Tipos_Prioridad"
	rowTipoPrioridad=objConsulta.ConsultaMainDoc(sqlTipoPrioridad)

	tipodocumento=[{"id":val.Id_TipoDocumento,"nombre":val.Nombre_TipoDocumento} for val in rowTipodocumento]
	prioridad=[{"id":val.Id_TiposPrioridad,"nombre":val.Nombre_Prioridad} for val in rowTipoPrioridad]
	
	
	return jsonify({'prioridad':prioridad,'tipodocumento':tipodocumento})

@documento_bp.route('/searchkey',methods=['POST'])
def busqueda():
	valor=request.form.get('valor')
	objConsulta=QueryDocumentos()
	sql="SELECT * FROM Oficina WHERE UPPER(nombre_oficina) LIKE ? AND NOT Id_Oficina=?"
	rows=objConsulta.ConsultaMainDocParams(sql,('%'+valor.upper()+'%','AAMAA'))
	oficinas=[{'id':val.Id_Oficina,'nombre':val.nombre_oficina} for val in rows]
	return jsonify({'oficinas':oficinas})

@documento_bp.route('/tflujo',methods=['POST'])
def TFlujo():
	objConsulta=QueryDocumentos()
	tipoflujo=request.form.get('flujo')
	oficina='AAMAA'
	#numero de ingreso y egreso
	sql="SELECT * FROM MOVIMIENTO WHERE Id_Oficina_Origen=? AND Tipo_Flujo=? AND Year(Fecha_Movimiento)=Year(GETDATE())"
	params=(oficina,tipoflujo)
	rows=objConsulta.ConsultaMainDocParams(sql,params)

	numeracion=None
	if tipoflujo=='Ingreso':
		numeracion=rows[0].numeroIngreso+1 if rows else 1		
	else:
		numeracion=rows[0].numeroEgreso+1 if rows else 1	
	

	#codigo de seguimiento
	sql1="SELECT * FROM DOCUMENTO WHERE CodigoSeguimiento=?"
	
	codigo=None
	while True:
		codigo=utilidades.GeneracionCodigo(8)
		rowCodigo=objConsulta.ConsultaMainDocParams(sql,(codigo,))
		if not rowCodigo:
			break

	return jsonify({'numeracion':numeracion,'codigoS':codigo})

@documento_bp.route('/filldata',methods=['POST'])
def filldata():
	dni=request.form.get('dni')
	objConsulta=QueryDocumentos()
	sql="SELECT * FROM PERSONA WHERE DNI=?"
	row=objConsulta.ConsultaMainDocParams(sql,(dni,))
	datos=[{'nombre':val.Nombre,'apellidoP':val.ApellidoPaterno,'apellidoM':val.ApellidoMaterno} for val in row] if row else []

	return jsonify({'datos':datos})

@documento_bp.route('/insertdocument',methods=['POST'])
def insertDoc():
	tflujo=request.form.get('TFlujo')
	numeracion=request.form.get('numeracion')
	codigoSeguimiento=request.form.get('NSeguimiento')
	asunto=request.form.get('Asunto')
	tipodocumento=request.form.get('Tdoc')
	descripcion=request.form.get('descripcion')
	prioridad=request.form.get('prioridad')
	oficinas=request.form.getlist('oficinas[]')
	codigooficina=request.form.getlist('codigos[]')


	return[1]


	

