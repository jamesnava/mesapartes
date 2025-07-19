from flask import Blueprint, render_template, redirect, url_for, request,jsonify
from app.formularios.Documentos.formDocumentos import Documentos
from app.modelos.QueryDocumento import QueryDocumentos
from flask_login import current_user,login_required
from app.utilidades import utilidades
import os
import uuid

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
	rows=objConsulta.ConsultaMainDocParams(sql,('%'+valor.upper()+'%',current_user.id_oficina))
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
		codigo=utilidades.GeneracionCodigo(6)
		rowCodigo=objConsulta.ConsultaMainDocParams(sql1,(codigo,))
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
	nro_movimiento=0
	objConsulta=QueryDocumentos()
	tflujo='Egreso'
	titulo=request.form.get('titulodoc')	
	asunto=request.form.get('Asunto')
	tipodocumento=request.form.get('Tdoc')
	descripcion=request.form.get('descripcion')
	prioridad=request.form.get('prioridad')
	emisor=request.form.get('Emisor')
	oficinas=request.form.getlist('oficinas[]')
	codigooficina=request.form.getlist('codigos[]')
	archivo = request.files.get('adjunto')
	idusuario=request.form.get('idusuario')
	idoficinaorigen=request.form.get('idoficinaorigen')
	idAdjunto=0	


	if archivo:
		try:
			extension = os.path.splitext(archivo.filename)[1]
			nombre_unico = f"{uuid.uuid4().hex}{extension}"
			ruta = os.path.join('app', 'static', 'uploads', nombre_unico)		
			archivo.save(ruta)
			sqlInsertAdjunto="INSERT INTO Adjunto(url_archivo) OUTPUT INSERTED.Id_Adjunto VALUES(?)"
			idAdjunto=objConsulta.InsertDataIdentity(sqlInsertAdjunto,(nombre_unico,))	
		except Exception as e:
			raise e
	
	for codOf in codigooficina:
		numeracion=0
		numeracion=getnumeracion(idoficinaorigen,tflujo)
		codigoSeguimiento=codigoseguimiento()		
		sqlInsert=f"""INSERT INTO DOCUMENTO(Titulo,Id_TipoDocumento,Estado,Prioridad,Fecha_Creacion,CodigoSeguimiento,Contenido,Emisor,
		Id_Adjunto,Id_Oficina_Origen,Id_Oficina_Destino) OUTPUT INSERTED.Id_Documento VALUES(?,?,1,?,CONVERT(DATE,GETDATE()),?,?,?,?,?,?)"""
		params=(titulo,tipodocumento,prioridad,codigoSeguimiento,descripcion,emisor,idAdjunto,idoficinaorigen,codOf)
		nro_insertdoc=objConsulta.InsertDataIdentity(sqlInsert,params)

		sqlInsertMovimiento=f"""
		INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,Id_Oficina_Destino,Id_Archivo,numeroIngreso,numeroEgreso,Tipo_Flujo)
		OUTPUT INSERTED.Id_Movimiento VALUES(?,?,GETDATE(),?,?,?,?,?,?,?,?)
		"""
		paramsMovimiento=(nro_insertdoc,idusuario,1,'',idoficinaorigen,codOf,idAdjunto,0,numeracion,tflujo)

		nro_movimiento=objConsulta.InsertDataIdentity(sqlInsertMovimiento,paramsMovimiento)


	return[nro_movimiento]

@documento_bp.route('/docin')
def ingresoDocumento():	
	params=('Egreso',current_user.id_oficina,1)
	rows=ConsultaDocumentos(params)
	#bloque para llenar la otra tabla
	params_recepcionados=('Ingreso',current_user.id_oficina,2)
	rows_recepcionadas=ConsultaDocumentos(params_recepcionados)	
	return render_template('/documentos/doc_ingreso.html',datos=rows,datos_recepcion=rows_recepcionadas,info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina})

@documento_bp.route('/recepcionardoc',methods=['POST'])
def RecepcionDocumento():
	objConsulta=QueryDocumentos()
	idmovimiento=request.form.get('idDoc')
	oficina=request.form.get('oficina')
	usuario_id=request.form.get('idusuario')
	numeracion=getnumeracion(oficina,'Ingreso')

	sql="""SELECT * FROM MOVIMIENTO WHERE Id_Movimiento=?"""
	rows_Anterior=objConsulta.ConsultaMainDocParams(sql,(idmovimiento,))	
	#insertando un nuevo registro
	sqlinsert="""INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,Id_Oficina_Destino,
	Id_Archivo,numeroIngreso,numeroEgreso,Tipo_Flujo) OUTPUT INSERTED.Id_Movimiento VALUES (?,?,GETDATE(),?,?,?,?,?,?,?,?)"""
	params=(rows_Anterior[0].Id_Documento,usuario_id,2,'',rows_Anterior[0].Id_Oficina_Origen,oficina,rows_Anterior[0].Id_Archivo,numeracion,0,'Ingreso')	
	ejecutado=objConsulta.InsertDataIdentity(sqlinsert,params)
	
	manejador=0
	if ejecutado!=0:
		sqlUpdate="UPDATE DOCUMENTO SET Estado=? WHERE Id_Documento=?"		
		manejador=objConsulta.InsertDataGeneral(sqlUpdate,(2,rows_Anterior[0].Id_Documento))

	return [manejador]

@documento_bp.route('/acciones',methods=['POST'])
def accionesgenerales():
	objConsulta=QueryDocumentos()
	
	
	sql_acciones="""SELECT * FROM ACCIONES WHERE Nombre_Accion NOT IN('Registro','Recepción')"""

	row_Acciones=objConsulta.ConsultaMainDoc(sql_acciones)
	datos_Acciones=[{'Id_Accion':val.Id_Accion,'Nombre_Accion':val.Nombre_Accion} for val in row_Acciones]

	datos_retornar=jsonify({'acciones':datos_Acciones})
	return datos_retornar

@documento_bp.route('/confirmaraccion',methods=['POST'])
def actualizacionaccion():
	accion=request.form.get('accion')
	comentario=request.form.get('comentario')
	idmovimiento=request.form.get('idmovimiento')
	codigoOficina=request.form.get('codigoOf')
	print(accion,comentario,idmovimiento,codigoOficina)
	return [0]

def getnumeracion(oficina,tipoflujo):
	objConsulta=QueryDocumentos()	
	#numero de ingreso y egreso
	sql="SELECT * FROM MOVIMIENTO WHERE Id_Oficina_Origen=? AND Tipo_Flujo=? AND Year(Fecha_Movimiento)=Year(GETDATE())"
	params=(oficina,tipoflujo)
	rows=objConsulta.ConsultaMainDocParams(sql,params)

	numeracion=None
	if tipoflujo=='Ingreso':		
		numeracion=max(row.numeroIngreso for row in rows)+1 if rows else 1		
	else:
		numeracion=max(row.numeroEgreso for row in rows)+1 if rows else 1	
	return numeracion
	
def codigoseguimiento():
	objConsulta=QueryDocumentos()	
	sql1="SELECT * FROM DOCUMENTO WHERE CodigoSeguimiento=?"
	
	codigo=None
	while True:
		codigo=utilidades.GeneracionCodigo(6)
		rowCodigo=objConsulta.ConsultaMainDocParams(sql1,(codigo,))
		if not rowCodigo:
			break

	return codigo

def ConsultaDocumentos(params):
	objConsulta=QueryDocumentos()
	sql="""WITH UltimosMovimientos AS (
  	SELECT *,
         ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS fila
  	FROM MOVIMIENTO WHERE Tipo_Flujo =? AND Id_Oficina_Destino = ?)

	SELECT FORMAT(M.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,
	CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) AS NEmisor,TD.Nombre_TipoDocumento,
	D.Asunto,O.nombre_oficina,TP.Nombre_Prioridad,A.url_archivo,D.Titulo,M.Id_Movimiento
	FROM UltimosMovimientos M
	INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento INNER JOIN PERSONA AS P ON D.Emisor=P.Dni
	INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad=TP.Id_TiposPrioridad INNER JOIN Tipo_Documento AS TD ON D.Id_TipoDocumento=TD.Id_TipoDocumento
	INNER JOIN Oficina AS O ON M.Id_Oficina_Origen=O.Id_Oficina INNER JOIN Adjunto AS A ON D.Id_Adjunto=A.Id_Adjunto
	WHERE M.fila = 1 AND D.Estado = ?;"""
	rows=objConsulta.ConsultaMainDocParams(sql,params)
	return rows



	

