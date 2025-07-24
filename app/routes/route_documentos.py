from flask import Blueprint, render_template, redirect, url_for, request,jsonify
from app.formularios.Documentos.formDocumentos import Documentos
from app.modelos.QueryDocumento import QueryDocumentos
from flask_login import current_user,login_required
from app.utilidades import utilidades
import os
import uuid
import locale
from datetime import datetime


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
	oficina=current_user.id_oficina
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

	nombre_unico=''
	if archivo:
		try:
			extension = os.path.splitext(archivo.filename)[1]
			nombre_unico = f"{uuid.uuid4().hex}{extension}"
			ruta = os.path.join('app', 'static', 'uploads', nombre_unico)		
			archivo.save(ruta)			
		except Exception as e:
			raise e
	sqlInsertAdjunto="INSERT INTO Adjunto(url_archivo) OUTPUT INSERTED.Id_Adjunto VALUES(?)"
	idAdjunto=objConsulta.InsertDataIdentity(sqlInsertAdjunto,(nombre_unico,))	
	codigodocumento=0
	oficinas_codigo=[]
	
	for codOf in codigooficina:
		numeracion=0
		numeracion=getnumeracion(idoficinaorigen,tflujo)
		codigoSeguimiento=codigoseguimiento()		
		sqlInsert=f"""INSERT INTO DOCUMENTO(Titulo,Id_TipoDocumento,Estado,Prioridad,Fecha_Creacion,CodigoSeguimiento,Contenido,Emisor,
		Id_Adjunto,Id_Oficina_Origen,Id_Oficina_Destino,Asunto) OUTPUT INSERTED.Id_Documento VALUES(?,?,1,?,CONVERT(DATE,GETDATE()),?,?,?,?,?,?,?)"""
		params=(titulo,tipodocumento,prioridad,codigoSeguimiento,descripcion,emisor,idAdjunto,idoficinaorigen,codOf,asunto)
		nro_insertdoc=objConsulta.InsertDataIdentity(sqlInsert,params)

		codigodocumento=nro_insertdoc
		sqlInsertMovimiento=f"""
		INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,Id_Oficina_Destino,Id_Archivo,numeroIngreso,numeroEgreso,Tipo_Flujo)
		OUTPUT INSERTED.Id_Movimiento VALUES(?,?,GETDATE(),?,?,?,?,?,?,?,?)
		"""
		paramsMovimiento=(nro_insertdoc,idusuario,1,'',idoficinaorigen,codOf,idAdjunto,0,numeracion,tflujo)
		nro_movimiento=objConsulta.InsertDataIdentity(sqlInsertMovimiento,paramsMovimiento)

		#llenando la lista de oficinas y seguimiento
		rows_oficinas_consulta=objConsulta.ConsultaMainDocParams("SELECT * FROM Oficina WHERE Id_Oficina=?",(codOf,))
		oficinas_codigo.append((rows_oficinas_consulta[0].nombre_oficina,codigoSeguimiento))

	#generar ticket
	SQL_DOCUMENTOS="""SELECT  CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) As emisor,D.Asunto,P.Dni,D.Fecha_Creacion,TD.Nombre_TipoDocumento,TP.Nombre_Prioridad FROM DOCUMENTO AS D INNER JOIN Oficina AS O ON D.Id_Oficina_Destino=O.Id_Oficina INNER JOIN 
	Tipo_Documento AS TD ON D.Id_TipoDocumento=TD.Id_TipoDocumento INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad=TP.Id_TiposPrioridad
	INNER JOIN PERSONA AS P ON D.Emisor=P.Dni WHERE D.Id_Documento=?"""
	rows_consulta_documento=objConsulta.ConsultaMainDocParams(SQL_DOCUMENTOS,(codigodocumento,))
	utilidades.generarTicket(rows_consulta_documento,oficinas_codigo,'app/static/ticket/doc.pdf')


	return[nro_movimiento]

@documento_bp.route('/docin')
def ingresoDocumento():	
	params=(current_user.id_oficina,)
	rows=consultaDocumentosEntrada(params)
	#bloque para llenar la otra tabla
	params_recepcionados=('Ingreso',current_user.id_oficina,2,5)
	rows_recepcionadas=ConsultaDocumentos(params_recepcionados)	
	return render_template('/documentos/doc_ingreso.html',datos=rows,datos_recepcion=rows_recepcionadas,info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina})

@documento_bp.route('/docseg')
def segDocumento():	
	return render_template('/documentos/doc_seguimiento.html',info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina})

@documento_bp.route('/followrequest',methods=['POST'])
def followS():
	objConsulta=QueryDocumentos()
	codigo=request.form.get('codigo')
	sql="""SELECT M.Fecha_Movimiento,A.Nombre_Accion,M.Id_Oficina_Origen,M.Id_Oficina_Destino,U.Nombre_Usuario,M.comentarios FROM MOVIMIENTO AS M INNER JOIN DOCUMENTO AS D ON M.Id_Documento=D.Id_Documento INNER JOIN ACCIONES
	AS A ON M.Id_Accion=A.Id_Accion INNER JOIN Estado_Doc AS E ON D.Estado=E.Id_EstadoDoc
	INNER JOIN USUARIO AS U ON M.Id_Usuario=U.Id_Usuario WHERE D.CodigoSeguimiento=? ORDER BY M.Fecha_Movimiento DESC"""
	rows_result=objConsulta.ConsultaMainDocParams(sql,(codigo,))
	datos=[]
	for val in rows_result:
		destino=None
		sql_ofi="SELECT * FROM Oficina WHERE Id_Oficina=?"
		rows_origen=objConsulta.ConsultaMainDocParams(sql_ofi,(val.Id_Oficina_Origen,))
		if val.Id_Oficina_Destino:
			rows_destino=objConsulta.ConsultaMainDocParams(sql_ofi,(val.Id_Oficina_Destino,))
			destino=rows_destino[0].nombre_oficina
		locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
		fecha = datetime.strptime(str(val.Fecha_Movimiento), '%Y-%m-%d %H:%M:%S.%f')
		fecha_formateada = fecha.strftime('%A %d de %B de %Y, %H:%M:%S')		

		datos.append({'fecha':fecha_formateada,'accion':val.Nombre_Accion,'origen':rows_origen[0].nombre_oficina,'destino':destino ,'usuario':val.Nombre_Usuario,'comentario':val.comentarios})

	return jsonify({'datos':datos})

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
	
	sql_acciones="""SELECT * FROM ACCIONES WHERE Nombre_Accion NOT IN('Registro','Recepción','Subsanación')
	ORDER BY Nombre_Accion"""

	row_Acciones=objConsulta.ConsultaMainDoc(sql_acciones)
	datos_Acciones=[{'Id_Accion':val.Id_Accion,'Nombre_Accion':val.Nombre_Accion} for val in row_Acciones]

	datos_retornar=jsonify({'acciones':datos_Acciones})
	return datos_retornar

@documento_bp.route('/confirmaraccion',methods=['POST'])
def actualizacionaccion():
	objConsulta=QueryDocumentos()
	accion=request.form.get('accion')
	comentario=request.form.get('comentario')
	idmovimiento=request.form.get('idmovimiento')
	codigoOficina=request.form.get('codigoOf')
	sql="""SELECT * FROM MOVIMIENTO WHERE Id_Movimiento=?"""
	rows_Anterior=objConsulta.ConsultaMainDocParams(sql,(idmovimiento,))

	#insertar accion
	sql_insertar="""INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,
	Id_Oficina_Destino,numeroIngreso,numeroEgreso,Tipo_Flujo) OUTPUT INSERTED.Id_Movimiento
	VALUES(?,?,GETDATE(),?,?,?,?,?,?,?)"""
	#(accion,estado)
	pares=[(1,1),(2,2),(3,3),(4,4),(5,5),(7,6),(8,7),(12,7)]
	selected=None
	for index,val in enumerate(pares):		
		if val[0]==int(accion):
			selected=index
			break			

	params=None	

	if selected!=None:
		if int(accion)==3:
			numeracion=0
			numeracion=getnumeracion(current_user.id_oficina,'Egreso')
			for val in rows_Anterior:			
				params=(val.Id_Documento,val.Id_Usuario,pares[selected][0],comentario,current_user.id_oficina,codigoOficina,0,numeracion,'Egreso')
		elif int(accion)==4:
			for val in rows_Anterior:
				params=(val.Id_Documento,val.Id_Usuario,pares[selected][0],comentario,current_user.id_oficina,val.Id_Oficina_Origen,0,0,'Interno')
		elif int(accion) in (7,8,12):
			for val in rows_Anterior:
				params=(val.Id_Documento,val.Id_Usuario,pares[selected][0],comentario,current_user.id_oficina,None,0,0,'Interno')

	
	idmovimiento=objConsulta.InsertDataIdentity(sql_insertar,params)

	indicador=0
	if idmovimiento:
		sql_documento="UPDATE DOCUMENTO SET Estado=? WHERE Id_Documento=?"
		parametros=(pares[selected][1],rows_Anterior[0].Id_Documento)
		indicador=objConsulta.InsertDataGeneral(sql_documento,parametros)


	return [indicador]


@documento_bp.route('/outdoc')
def salidasdoc():
	objConsulta=QueryDocumentos()
	sql="""WITH UltimosMovimientos AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS fila FROM MOVIMIENTO 
    WHERE Tipo_Flujo = ? AND Id_Oficina_Origen = ?)
	SELECT 
    FORMAT(M.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,
    CONCAT(P.Nombre, ' ', P.ApellidoPaterno, ' ', P.ApellidoMaterno) AS NEmisor,TD.Nombre_TipoDocumento,D.Asunto,O.nombre_oficina,
    TP.Nombre_Prioridad,A.url_archivo,D.Titulo,M.Id_Movimiento,ED.Nombre_estado FROM UltimosMovimientos M INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento
	INNER JOIN PERSONA P ON D.Emisor = P.Dni INNER JOIN Tipos_Prioridad TP ON D.Prioridad = TP.Id_TiposPrioridad
	INNER JOIN Tipo_Documento TD ON D.Id_TipoDocumento = TD.Id_TipoDocumento INNER JOIN Oficina O ON M.Id_Oficina_Destino = O.Id_Oficina
	INNER JOIN Adjunto A ON D.Id_Adjunto = A.Id_Adjunto INNER JOIN Estado_Doc AS ED ON D.Estado=ED.Id_EstadoDoc WHERE M.fila = 1 AND M.Id_Accion = ?"""
	rows_resultados=objConsulta.ConsultaMainDocParams(sql,('Egreso',current_user.id_oficina,3))


	return render_template('/documentos/doc_salida.html',datos=rows_resultados)

@documento_bp.route('/revertirdoc',methods=['POST'])
def revertirdoc():
	objConsulta=QueryDocumentos()
	idmovimiento=request.form.get('idmovimiento')
	sql_query="SELECT * FROM MOVIMIENTO WHERE Id_Movimiento=?"
	rows_consulta=objConsulta.ConsultaMainDocParams(sql_query,(idmovimiento,))

	sqlupdate="UPDATE DOCUMENTO SET Estado=? WHERE Id_Documento=?"
	numero_actualizacion=objConsulta.InsertDataGeneral(sqlupdate,(2,rows_consulta[0].Id_Documento))

	nro_Eliminacion=0
	if numero_actualizacion:
		sql_Eliminar="DELETE FROM MOVIMIENTO WHERE Id_Movimiento=?"
		nro_Eliminacion=objConsulta.InsertDataGeneral(sql_Eliminar,(idmovimiento,))
	return [nro_Eliminacion]

@documento_bp.route('/docobservados')
def docObservados():
	objConsulta=QueryDocumentos()
	sql_observados="""WITH ULTIMOSMOVIMIENTOS AS ( SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento 
					DESC) AS fila FROM MOVIMIENTO)	SELECT UM.Fecha_Movimiento,UM.comentarios,D.Asunto,D.Titulo,UM.Id_Movimiento FROM 
					ULTIMOSMOVIMIENTOS AS UM INNER JOIN DOCUMENTO AS D ON UM.Id_Documento=D.Id_Documento WHERE UM.fila=1 AND 
					UM.Id_Accion=? AND UM.Id_Oficina_Destino=?"""
	params=(4,current_user.id_oficina)

	rows=objConsulta.ConsultaMainDocParams(sql_observados,params)	
	return render_template('/documentos/doc_observados.html',datos=rows,info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina})

@documento_bp.route('/subsanacion',methods=['POST'])
def SubsanarDoc():
	objConsulta=QueryDocumentos()
	archivo = request.files.get('adjunto')
	idmovimiento=request.form.get('idmovimientooculto')
	sql_consulta="""SELECT M.*,D.Id_Documento FROM MOVIMIENTO AS M INNER JOIN DOCUMENTO AS D ON M.Id_Documento=D.Id_Documento WHERE
	 M.Id_Movimiento=?"""
	rows_doc=objConsulta.ConsultaMainDocParams(sql_consulta,(idmovimiento,))	
	controlador=0
	if archivo:
		try:
			extension = os.path.splitext(archivo.filename)[1]
			nombre_unico = f"{uuid.uuid4().hex}{extension}"
			ruta = os.path.join('app', 'static', 'uploads', nombre_unico)		
			archivo.save(ruta)
			sqlInsertAdjunto="INSERT INTO Adjunto(url_archivo) OUTPUT INSERTED.Id_Adjunto VALUES(?)"
			idAdjunto=objConsulta.InsertDataIdentity(sqlInsertAdjunto,(nombre_unico,))

			#modificamos documento
			sql_update="UPDATE DOCUMENTO SET Id_Adjunto=?,Estado=? WHERE Id_Documento=?"			
			nros=objConsulta.InsertDataGeneral(sql_update,(idAdjunto,5,rows_doc[0].Id_Documento))
			if nros:
				sql_insert="""INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,
				Id_Oficina_Destino,numeroIngreso,numeroEgreso,Tipo_Flujo) OUTPUT INSERTED.Id_Movimiento
				VALUES(?,?,GETDATE(),?,?,?,?,?,?,?)"""
				params=(rows_doc[0].Id_Documento,current_user.id,5,'',current_user.id_oficina,rows_doc[0].Id_Oficina_Origen,0,0,'Interno')
				controlador=objConsulta.InsertDataIdentity(sql_insert,params)

		except Exception as e:
			print(e)
	print('controlador',controlador)
	return [controlador]
def getnumeracion(oficina,tipoflujo):
	objConsulta=QueryDocumentos()	
	#numero de ingreso y egreso
	sql=None
	if tipoflujo=='Egreso':
		sql="SELECT * FROM MOVIMIENTO WHERE Id_Oficina_Origen=? AND Tipo_Flujo=? AND Year(Fecha_Movimiento)=Year(GETDATE())"
	else:
		sql="SELECT * FROM MOVIMIENTO WHERE Id_Oficina_Destino=? AND Tipo_Flujo=? AND Year(Fecha_Movimiento)=Year(GETDATE())"
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
	WHERE M.fila = 1 AND D.Estado IN (?,?);"""
	rows=objConsulta.ConsultaMainDocParams(sql,params)
	return rows
def consultaDocumentosEntrada(params):
	objConsulta=QueryDocumentos()
	sql="""WITH UltimosMovimientos AS ( SELECT *,ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS fila
    FROM MOVIMIENTO)
	SELECT FORMAT(M.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,
       CONCAT(P.Nombre, ' ', P.ApellidoPaterno, ' ', P.ApellidoMaterno) AS NEmisor,
       TD.Nombre_TipoDocumento,
       D.Asunto,
       O.nombre_oficina,
       TP.Nombre_Prioridad,
       A.url_archivo,
       D.Titulo,
       M.Id_Movimiento
	FROM UltimosMovimientos M
	INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento
	INNER JOIN PERSONA AS P ON D.Emisor = P.Dni
	INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad = TP.Id_TiposPrioridad
	INNER JOIN Tipo_Documento AS TD ON D.Id_TipoDocumento = TD.Id_TipoDocumento
	INNER JOIN Oficina AS O ON M.Id_Oficina_Origen = O.Id_Oficina
	INNER JOIN Adjunto AS A ON D.Id_Adjunto = A.Id_Adjunto
	WHERE M.fila = 1 AND M.Tipo_Flujo = 'Egreso'  AND M.Id_Oficina_Destino = ?  AND D.Estado IN (1, 3)"""
	rows=objConsulta.ConsultaMainDocParams(sql,params)
	return rows



	

