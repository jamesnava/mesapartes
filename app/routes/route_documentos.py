from flask import Blueprint, render_template, redirect,session, url_for, request,jsonify,send_file,current_app,after_this_request
from app.formularios.Documentos.formDocumentos import Documentos
from app.modelos.QueryDocumento import QueryDocumentos
from flask_login import current_user,login_required
from app.utilidades import utilidades
import os
import tempfile
import shutil
import time
import uuid
import locale
import threading
import time
from datetime import datetime
from app.decoratos import requires_permission
from app.constanst import Permiso


documento_bp=Blueprint('documents',__name__,url_prefix='/documents')
#from app.decoratos import requires_permission


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
@requires_permission(Permiso.DOC_NUEVO)
@login_required
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
	#datos de referencia
	iddocreferencia=request.form.get('refiddoc');
	idmovimientoreferencia=request.form.get('refidmov');
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
		Id_Adjunto,Id_Oficina_Origen,Id_Oficina_Destino,Asunto,referencia_id) OUTPUT INSERTED.Id_Documento VALUES(?,?,1,?,CONVERT(DATE,GETDATE()),?,?,?,?,?,?,?,?)"""
		params=(titulo,tipodocumento,prioridad,codigoSeguimiento,descripcion,emisor,idAdjunto,idoficinaorigen,codOf,asunto,iddocreferencia)
		nro_insertdoc=objConsulta.InsertDataIdentity(sqlInsert,params)

		codigodocumento=nro_insertdoc
		sqlInsertMovimiento=f"""INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,
		Id_Oficina_Destino,Id_Archivo,numeroIngreso,numeroEgreso,Tipo_Flujo) OUTPUT INSERTED.Id_Movimiento VALUES(?,?,GETDATE(),?,?,?,?,?,?,?,?)
		"""
		paramsMovimiento=(nro_insertdoc,idusuario,1,'',idoficinaorigen,codOf,idAdjunto,0,numeracion,tflujo)
		nro_movimiento=objConsulta.InsertDataIdentity(sqlInsertMovimiento,paramsMovimiento)

		#llenando la lista de oficinas y seguimiento
		rows_oficinas_consulta=objConsulta.ConsultaMainDocParams("SELECT * FROM Oficina WHERE Id_Oficina=?",(codOf,))
		oficinas_codigo.append((rows_oficinas_consulta[0].nombre_oficina,codigoSeguimiento))

	#actualizando datos
	if len(iddocreferencia)>0:
		sql_update_doc="UPDATE DOCUMENTO SET Estado=? WHERE Id_Documento=?"
		rows_update=objConsulta.InsertDataGeneral(sql_update_doc,(1002,iddocreferencia))
		if rows_update==1:
			rows_update_movi=objConsulta.ConsultaMainDocParams("SELECT * FROM MOVIMIENTO WHERE Id_Movimiento=?",(idmovimientoreferencia,))
			sqlActualizar=f"""INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,
			numeroIngreso,numeroEgreso,Tipo_Flujo) OUTPUT INSERTED.Id_Movimiento VALUES(?,?,GETDATE(),?,?,?,?,?,?)"""
			paramactualizar=(rows_update_movi[0].Id_Documento,idusuario,1002,'Referenciado',current_user.id_oficina,0,0,'Interno')			
			nro_movi=objConsulta.InsertDataIdentity(sqlActualizar,paramactualizar)



	#generar ticket
	SQL_DOCUMENTOS="""SELECT  CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) As emisor,D.Asunto,P.Dni,D.Fecha_Creacion,TD.Nombre_TipoDocumento,TP.Nombre_Prioridad FROM DOCUMENTO AS D INNER JOIN Oficina AS O ON D.Id_Oficina_Destino=O.Id_Oficina INNER JOIN 
	Tipo_Documento AS TD ON D.Id_TipoDocumento=TD.Id_TipoDocumento INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad=TP.Id_TiposPrioridad
	INNER JOIN PERSONA AS P ON D.Emisor=P.Dni WHERE D.Id_Documento=?"""
	rows_consulta_documento=objConsulta.ConsultaMainDocParams(SQL_DOCUMENTOS,(codigodocumento,))

	nombre_pdf=f'app/static/ticket/{nro_movimiento}_doc.pdf'
	pdfname=f'{nro_movimiento}_doc.pdf'
	utilidades.generarTicket(rows_consulta_documento,oficinas_codigo,nombre_pdf)

	return jsonify({'movimiento':nro_movimiento,'direccion':url_for('documents.ver_pdfticket',nombre=pdfname)})

@documento_bp.route('/seeticketa',methods=['POST'])
@login_required
def seeTicketAtencion():
	objConsulta=QueryDocumentos()
	idmovimiento=request.form.get('idmovimiento')
	SQL_DOCUMENTOS="""SELECT TOP 1  CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) As emisor,D.Asunto,P.Dni,D.Fecha_Creacion,
	TD.Nombre_TipoDocumento,TP.Nombre_Prioridad,D.CodigoSeguimiento,O.nombre_oficina FROM DOCUMENTO AS D INNER JOIN Oficina AS O ON D.Id_Oficina_Destino=O.Id_Oficina INNER JOIN 
	Tipo_Documento AS TD ON D.Id_TipoDocumento=TD.Id_TipoDocumento INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad=TP.Id_TiposPrioridad
	INNER JOIN PERSONA AS P ON D.Emisor=P.Dni INNER JOIN MOVIMIENTO AS M ON M.Id_Documento=D.Id_Documento WHERE M.Id_Movimiento=? ORDER BY M.Id_Movimiento ASC"""

	rows_consult=objConsulta.ConsultaMainDocParams(SQL_DOCUMENTOS,(idmovimiento,))
	nombre_pdf=f'app/static/ticket/{idmovimiento}_doc.pdf'
	pdfname=f'{idmovimiento}_doc.pdf'
	utilidades.generarTicket(rows_consult,[(rows_consult[0].nombre_oficina,rows_consult[0].CodigoSeguimiento)],nombre_pdf)
	return jsonify({'direccion':url_for('documents.ver_pdfticket',nombre=pdfname)})

@documento_bp.route('/ver-pdf/<nombre>')
def ver_pdfticket(nombre):
	ruta=os.path.join(current_app.static_folder,'ticket',nombre)

	if not os.path.exists(ruta):
		return "Archivo no encontrado",404
	
	def borrar_archivo(path):
		time.sleep(5)
		try:
			os.remove(path)
		except Exception as e:
			raise e
		
	threading.Thread(target=borrar_archivo, args=(ruta,)).start()
	return send_file(ruta,mimetype="application/pdf")


@documento_bp.route('/docin')
@requires_permission(Permiso.DOC_BENTRADA)
@login_required
def ingresoDocumento():	
	params=(current_user.id_oficina,)
	rows=consultaDocumentosEntrada(params)
	#bloque para llenar la otra tabla
	params_recepcionados=('Ingreso',current_user.id_oficina,2,5)
	rows_recepcionadas=ConsultaDocumentos(params_recepcionados)	
	return render_template('/documentos/doc_ingreso.html',datos=rows,datos_recepcion=rows_recepcionadas,info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina})

@documento_bp.route('/docseg')
@requires_permission(Permiso.DOC_SEGUIMIENTO)
@login_required
def segDocumento():	
	return render_template('/documentos/doc_seguimiento.html',info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina})

@documento_bp.route('/followrequest',methods=['POST'])
@requires_permission(Permiso.DOC_SEGUIMIENTO)
@login_required
def followS():
	objConsulta=QueryDocumentos()
	codigo=request.form.get('codigo')
	#sql="""SELECT M.Fecha_Movimiento,A.Nombre_Accion,M.Id_Oficina_Origen,M.Id_Oficina_Destino,U.Nombre_Usuario,M.comentarios FROM MOVIMIENTO AS M INNER JOIN DOCUMENTO AS D ON M.Id_Documento=D.Id_Documento INNER JOIN ACCIONES
	#AS A ON M.Id_Accion=A.Id_Accion INNER JOIN Estado_Doc AS E ON D.Estado=E.Id_EstadoDoc
	#INNER JOIN USUARIO AS U ON M.Id_Usuario=U.Id_Usuario WHERE D.CodigoSeguimiento=? ORDER BY M.Fecha_Movimiento DESC"""

	sql="""WITH RECURSIVO AS (
    -- Arranca del documento con el CodigoSeguimiento que consultaste
    SELECT 
        D.Id_Documento,
        D.CodigoSeguimiento,
        D.Referencia_Id,
        1 AS Nivel
    FROM DOCUMENTO D
    WHERE D.CodigoSeguimiento =?

    UNION ALL

    -- Trae los documentos que referencian al anterior
    SELECT 
        H.Id_Documento,
        H.CodigoSeguimiento,
        H.Referencia_Id,
        R.Nivel + 1
    FROM DOCUMENTO H
    INNER JOIN RECURSIVO R ON H.Referencia_Id = R.Id_Documento
)
SELECT 
    R.Nivel,
    D.CodigoSeguimiento,
    M.Fecha_Movimiento,
    A.Nombre_Accion,
    M.Id_Oficina_Origen,
    M.Id_Oficina_Destino,
    U.Nombre_Usuario,
    M.comentarios,
    D.Titulo
FROM RECURSIVO R
INNER JOIN DOCUMENTO D ON R.Id_Documento = D.Id_Documento
INNER JOIN MOVIMIENTO M ON D.Id_Documento = M.Id_Documento
INNER JOIN ACCIONES A ON M.Id_Accion = A.Id_Accion
INNER JOIN USUARIO U ON M.Id_Usuario = U.Id_Usuario
ORDER BY R.Nivel ASC, M.Fecha_Movimiento ASC;

"""


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

		datos.append({'fecha':fecha_formateada,'accion':val.Nombre_Accion,'origen':rows_origen[0].nombre_oficina,'destino':destino ,'usuario':val.Nombre_Usuario,'comentario':val.comentarios,'documento':val.Titulo})

	return jsonify({'datos':datos})

@documento_bp.route('/recepcionardoc',methods=['POST'])
@requires_permission(Permiso.DOC_BENTRADA)
@login_required
def RecepcionDocumento():
	objConsulta=QueryDocumentos()
	idmovimiento=request.form.get('idDoc')
	oficina=request.form.get('oficina')
	usuario_id=request.form.get('idusuario')
	numeracion=getnumeracion(oficina,'Ingreso')
	
	sql="""SELECT * FROM MOVIMIENTO WHERE Id_Movimiento=?"""
	rows_Anterior=objConsulta.ConsultaMainDocParams(sql,(idmovimiento,))
	#verificamos si existe el registro
	sql_check = """SELECT TOP 1 Id_Movimiento FROM MOVIMIENTO  WHERE Id_Documento = ? AND Id_Usuario = ? AND Tipo_Flujo = 'Ingreso'
	   AND Fecha_Movimiento >= DATEADD(SECOND, -5, GETDATE())  ORDER BY Fecha_Movimiento DESC"""

	existe = objConsulta.ConsultaMainDocParams(sql_check, (rows_Anterior[0].Id_Documento, usuario_id))
	manejador=0
	if existe:
		manejador=-1
		return jsonify(manejador)

	#insertando un nuevo registro
	sqlinsert="""INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,Id_Oficina_Destino,
	Id_Archivo,numeroIngreso,numeroEgreso,Tipo_Flujo) OUTPUT INSERTED.Id_Movimiento VALUES (?,?,GETDATE(),?,?,?,?,?,?,?,?)"""
	params=(rows_Anterior[0].Id_Documento,usuario_id,2,'',rows_Anterior[0].Id_Oficina_Origen,oficina,rows_Anterior[0].Id_Archivo,numeracion,0,'Ingreso')	
	ejecutado=objConsulta.InsertDataIdentity(sqlinsert,params)
	
	
	if ejecutado!=0:
		sqlUpdate="UPDATE DOCUMENTO SET Estado=? WHERE Id_Documento=?"		
		manejador=objConsulta.InsertDataGeneral(sqlUpdate,(2,rows_Anterior[0].Id_Documento))

	return jsonify(manejador)

@documento_bp.route('/acciones',methods=['POST'])
@requires_permission(Permiso.DOC_BENTRADA)
@login_required
def accionesgenerales():
	objConsulta=QueryDocumentos()	
	
	sql_acciones="""SELECT * FROM ACCIONES WHERE Nombre_Accion NOT IN('Registro','Recepción','Subsanación','Referenciado','Anulación')
	ORDER BY Nombre_Accion"""

	row_Acciones=objConsulta.ConsultaMainDoc(sql_acciones)
	datos_Acciones=[{'Id_Accion':val.Id_Accion,'Nombre_Accion':val.Nombre_Accion} for val in row_Acciones]

	datos_retornar=jsonify({'acciones':datos_Acciones})
	return datos_retornar

@documento_bp.route('/confirmaraccion',methods=['POST'])
@requires_permission(Permiso.DOC_BENTRADA)
@login_required
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
			#verificamos
			sql=sql_check = """ SELECT TOP 1 Id_Movimiento FROM MOVIMIENTO WHERE Id_Documento = ? AND Id_Usuario = ? AND Id_Accion = ? AND Id_Oficina_Origen = ?
     		AND Id_Oficina_Destino = ? AND Tipo_Flujo = ?  AND Fecha_Movimiento >= DATEADD(SECOND, -3, GETDATE())"""

			params_check = (rows_Anterior[0].Id_Documento,current_user.id,pares[selected][0],current_user.id_oficina,codigoOficina,'Egreso')
			existe = objConsulta.ConsultaMainDocParams(sql_check, params_check)	
			if existe:
				return jsonify(0)
			numeracion=0
			numeracion=getnumeracion(current_user.id_oficina,'Egreso')	

						
			params=(rows_Anterior[0].Id_Documento,current_user.id,pares[selected][0],comentario,current_user.id_oficina,codigoOficina,0,numeracion,'Egreso')

		elif int(accion)==4:
			for val in rows_Anterior:
				params=(val.Id_Documento,current_user.id,pares[selected][0],comentario,current_user.id_oficina,val.Id_Oficina_Origen,0,0,'Interno')
		elif int(accion) in (7,8,12):			
			params=(rows_Anterior[0].Id_Documento,current_user.id,pares[selected][0],comentario,current_user.id_oficina,None,0,0,'Interno')

	
	idmovimiento=objConsulta.InsertDataIdentity(sql_insertar,params)
	indicador=0
	if idmovimiento:
		sql_documento="UPDATE DOCUMENTO SET Estado=? WHERE Id_Documento=?"
		parametros=(pares[selected][1],rows_Anterior[0].Id_Documento)
		indicador=objConsulta.InsertDataGeneral(sql_documento,parametros)

	return jsonify(indicador)


@documento_bp.route('/outdoc')
@requires_permission(Permiso.DOC_BSALIDA)
@login_required
def salidasdoc():
	objConsulta=QueryDocumentos()
	sql="""WITH UltimosMovimientos AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS fila FROM MOVIMIENTO 
    WHERE  Id_Oficina_Origen = ?)
	SELECT 
    FORMAT(M.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,
    CONCAT(P.Nombre, ' ', P.ApellidoPaterno, ' ', P.ApellidoMaterno) AS NEmisor,TD.Nombre_TipoDocumento,D.Asunto,O.nombre_oficina,
    TP.Nombre_Prioridad,A.url_archivo,D.Titulo,M.Id_Movimiento,ED.Nombre_estado FROM UltimosMovimientos M INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento
	INNER JOIN PERSONA P ON D.Emisor = P.Dni INNER JOIN Tipos_Prioridad TP ON D.Prioridad = TP.Id_TiposPrioridad
	INNER JOIN Tipo_Documento TD ON D.Id_TipoDocumento = TD.Id_TipoDocumento INNER JOIN Oficina O ON M.Id_Oficina_Destino = O.Id_Oficina
	INNER JOIN Adjunto A ON D.Id_Adjunto = A.Id_Adjunto INNER JOIN Estado_Doc AS ED ON D.Estado=ED.Id_EstadoDoc WHERE M.fila = 1 AND D.Estado = ?"""
	rows_resultados=objConsulta.ConsultaMainDocParams(sql,(current_user.id_oficina,3))


	return render_template('/documentos/doc_salida.html',datos=rows_resultados)

@documento_bp.route('/revertirdoc',methods=['POST'])
@requires_permission(Permiso.DOC_BSALIDA)
@login_required
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
	return jsonify(nro_Eliminacion)

@documento_bp.route('/docobservados')
@requires_permission(Permiso.DOC_OBSERVADOS)
@login_required
def docObservados():
	objConsulta=QueryDocumentos()
	sql_observados="""WITH ULTIMOSMOVIMIENTOS AS ( SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento 
					DESC) AS fila FROM MOVIMIENTO)	SELECT FORMAT(UM.Fecha_Movimiento,'yyyy-MM-dd HH:mm') AS Fecha_Movimiento,UM.comentarios,D.Asunto,D.Titulo,UM.Id_Movimiento FROM 
					ULTIMOSMOVIMIENTOS AS UM INNER JOIN DOCUMENTO AS D ON UM.Id_Documento=D.Id_Documento WHERE UM.fila=1 AND 
					UM.Id_Accion=? AND UM.Id_Oficina_Destino=? ORDER BY UM.Fecha_Movimiento DESC"""
	params=(4,current_user.id_oficina)

	rows=objConsulta.ConsultaMainDocParams(sql_observados,params)	
	return render_template('/documentos/doc_observados.html',datos=rows,info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina})


@documento_bp.route('/subsanacion',methods=['POST'])
@requires_permission(Permiso.DOC_OBSERVADOS)
@login_required
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
	return jsonify(controlador)

@documento_bp.route('/doc_historial')
@requires_permission(Permiso.DOC_HISTORIAL)
@login_required
def HistorialDocumentos():	
	return render_template('/documentos/doc_historial.html')

@documento_bp.route('/fillhistorico',methods=['POST'])
@requires_permission(Permiso.DOC_HISTORIAL)
@login_required
def historicoDocumento():
	objConsulta=QueryDocumentos()
	flujo=request.form.get('tipo')
	datos=[]
	if flujo=='Ingreso':
		sql="""SELECT O.nombre_oficina,M.numeroIngreso,M.numeroEgreso,D.Titulo,FORMAT(M.Fecha_Movimiento,'yyyy-MM-dd HH:mm') AS Fecha_Movimiento,U.Nombre_Usuario,M.Tipo_Flujo,D.CodigoSeguimiento  
		FROM MOVIMIENTO AS M INNER JOIN DOCUMENTO AS D ON M.Id_Documento=D.Id_Documento INNER JOIN USUARIO AS U ON		
		M.Id_Usuario=U.Id_Usuario INNER JOIN Oficina AS O ON M.Id_Oficina_Origen=O.Id_Oficina WHERE M.Id_Oficina_Destino = ? AND Tipo_Flujo = 'Ingreso' ORDER BY M.Fecha_Movimiento DESC"""
		rows_result=objConsulta.ConsultaMainDocParams(sql,(current_user.id_oficina,))
		datos=[{'codigo':val.CodigoSeguimiento,'oficina':val.nombre_oficina,'numeracion':val.numeroIngreso,'titulo':val.Titulo,'fecha':val.Fecha_Movimiento,'usuario':val.Nombre_Usuario,'flujo':val.Tipo_Flujo} for val in rows_result]

	elif flujo=='Egreso':
		sql="""SELECT M.numeroEgreso,D.Titulo,FORMAT(M.Fecha_Movimiento,'yyyy-MM-dd HH:mm') AS Fecha_Movimiento,U.Nombre_Usuario,M.Tipo_Flujo,O.nombre_oficina,D.CodigoSeguimiento  FROM MOVIMIENTO AS M INNER JOIN DOCUMENTO AS D ON
		M.Id_Documento=D.Id_Documento INNER JOIN USUARIO AS U ON M.Id_Usuario=U.Id_Usuario INNER JOIN Oficina AS O ON M.Id_Oficina_Destino=O.Id_Oficina
		WHERE M.Id_Oficina_Origen = ?  AND Tipo_Flujo = 'Egreso' ORDER BY M.Fecha_Movimiento DESC"""
		rows_result=objConsulta.ConsultaMainDocParams(sql,(current_user.id_oficina))
		datos=[{'codigo':val.CodigoSeguimiento,'oficina':val.nombre_oficina,'numeracion':val.numeroEgreso,'titulo':val.Titulo,'fecha':val.Fecha_Movimiento,'usuario':val.Nombre_Usuario,'flujo':val.Tipo_Flujo} for val in rows_result]
	
	
	return jsonify({'datos':datos})

@documento_bp.route('/filterfillhistorico',methods=['POST'])
@requires_permission(Permiso.DOC_HISTORIAL)
@login_required
def historicoFilterDocumento():
	objConsulta=QueryDocumentos()
	argumento=request.form.get('argumento')
	radio=request.form.get('radio')
	datos=[]
	if radio=='Ingreso':
		sql="""SELECT TOP 50 O.nombre_oficina,M.numeroIngreso,M.numeroEgreso,D.Titulo,FORMAT(M.Fecha_Movimiento,'yyyy-MM-dd HH:mm') 
		AS Fecha_Movimiento,U.Nombre_Usuario,M.Tipo_Flujo,D.CodigoSeguimiento  
		FROM MOVIMIENTO AS M INNER JOIN DOCUMENTO AS D ON M.Id_Documento=D.Id_Documento INNER JOIN USUARIO AS U ON		
		M.Id_Usuario=U.Id_Usuario INNER JOIN Oficina AS O ON M.Id_Oficina_Origen=O.Id_Oficina 
		WHERE M.Id_Oficina_Destino = ? AND Tipo_Flujo = 'Ingreso' AND D.Titulo LIKE ?"""
		try:
			rows_result=objConsulta.ConsultaMainDocParams(sql,(current_user.id_oficina,"%"+argumento+"%"))
			datos=[{'codigo':val.CodigoSeguimiento,'oficina':val.nombre_oficina,'numeracion':val.numeroIngreso,'titulo':val.Titulo,'fecha':val.Fecha_Movimiento,'usuario':val.Nombre_Usuario,'flujo':val.Tipo_Flujo} for val in rows_result]
		except Exception as e:
			raise e

	elif radio=='Egreso':
		sql="""SELECT TOP 50 M.numeroEgreso,D.Titulo,FORMAT(M.Fecha_Movimiento,'yyyy-MM-dd HH:mm') AS Fecha_Movimiento,U.Nombre_Usuario,M.Tipo_Flujo,O.nombre_oficina,D.CodigoSeguimiento  FROM MOVIMIENTO AS M INNER JOIN DOCUMENTO AS D ON
		M.Id_Documento=D.Id_Documento INNER JOIN USUARIO AS U ON M.Id_Usuario=U.Id_Usuario INNER JOIN Oficina AS O ON M.Id_Oficina_Destino=O.Id_Oficina
		WHERE M.Id_Oficina_Origen = ?  AND Tipo_Flujo = 'Egreso' AND D.Titulo LIKE ?"""		
		try:
			rows_result=objConsulta.ConsultaMainDocParams(sql,(current_user.id_oficina,"%"+argumento+"%"))
			datos=[{'codigo':val.CodigoSeguimiento,'oficina':val.nombre_oficina,'numeracion':val.numeroIngreso,'titulo':val.Titulo,'fecha':val.Fecha_Movimiento,'usuario':val.Nombre_Usuario,'flujo':val.Tipo_Flujo} for val in rows_result]
		except Exception as e:
			raise e
	return jsonify({'datos':datos})

@documento_bp.route('/vercomentarios',methods=['POST'])
def VerComentarios():
	objConsulta=QueryDocumentos()
	idmovimiento=request.form.get('idmovimiento')
	sql="SELECT comentarios FROM MOVIMIENTO WHERE Id_Movimiento=?"
	rows_resultado=objConsulta.ConsultaMainDocParams(sql,(idmovimiento,))
	comentario=rows_resultado[0].comentarios if rows_resultado else ''
	return jsonify({'comentarios':comentario})

@documento_bp.route('/searchdocuments',methods=['POST'])
def searchDocuments():
	valor=request.form.get('valor')
	tipo=request.form.get('tipo')

	objConsulta=QueryDocumentos()
	datos=None
	if tipo=='RECEPCION':
		
		sql="""WITH UltimosMovimientos AS ( SELECT *,ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS fila
    	FROM MOVIMIENTO) 
    	SELECT FORMAT(M.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada, CONCAT(P.Nombre, ' ', P.ApellidoPaterno, ' ', P.ApellidoMaterno) AS NEmisor,
       	TD.Nombre_TipoDocumento,D.Asunto,O.nombre_oficina,TP.Nombre_Prioridad,A.url_archivo,D.Titulo,M.Id_Movimiento
		FROM UltimosMovimientos M INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento	INNER JOIN PERSONA AS P ON D.Emisor = P.Dni
		INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad = TP.Id_TiposPrioridad INNER JOIN Tipo_Documento AS TD ON D.Id_TipoDocumento = TD.Id_TipoDocumento
		INNER JOIN Oficina AS O ON M.Id_Oficina_Origen = O.Id_Oficina 	INNER JOIN Adjunto AS A ON D.Id_Adjunto = A.Id_Adjunto
		WHERE M.fila = 1 AND M.Tipo_Flujo = 'Egreso'  AND M.Id_Oficina_Destino = ?  AND D.Estado IN (1, 3) AND D.Titulo LIKE ?"""
		params=(current_user.id_oficina,'%'+valor+'%')
		rows=objConsulta.ConsultaMainDocParams(sql,params)
		datos=[{'fecha':val.FechaFormateada,'titulo':val.Titulo,'nameemisor':val.NEmisor,'url':val.url_archivo,'tipodoc':val.Nombre_TipoDocumento,'asunto':val.Asunto,'oficina':val.nombre_oficina,'nombreprioridad':val.Nombre_Prioridad,'idmovimiento':val.Id_Movimiento} for val in rows]
	
	elif tipo=='RECEPCIONADOS':		
		sql_="""WITH UltimosMovimientos AS (	SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS fila
  		FROM MOVIMIENTO WHERE Tipo_Flujo =? AND Id_Oficina_Destino = ?)

		SELECT FORMAT(M.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,
		CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) AS NEmisor,TD.Nombre_TipoDocumento,
		D.Asunto,O.nombre_oficina,TP.Nombre_Prioridad,A.url_archivo,D.Titulo,M.Id_Movimiento,D.CodigoSeguimiento
		FROM UltimosMovimientos M
		INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento INNER JOIN PERSONA AS P ON D.Emisor=P.Dni
		INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad=TP.Id_TiposPrioridad INNER JOIN Tipo_Documento AS TD ON D.Id_TipoDocumento=TD.Id_TipoDocumento
		INNER JOIN Oficina AS O ON M.Id_Oficina_Origen=O.Id_Oficina INNER JOIN Adjunto AS A ON D.Id_Adjunto=A.Id_Adjunto
		WHERE M.fila = 1 AND D.Estado IN (?,?) AND D.Titulo LIKE ?"""
		parametros=('Ingreso',current_user.id_oficina,2,5,'%'+valor+'%')
		rowsresult=objConsulta.ConsultaMainDocParams(sql_,parametros)
		datos=[{'fecha':val.FechaFormateada,'codseg':val.CodigoSeguimiento,'titulo':val.Titulo,'nameemisor':val.NEmisor,'url':val.url_archivo,'tipodoc':val.Nombre_TipoDocumento,'asunto':val.Asunto,'oficina':val.nombre_oficina,'nombreprioridad':val.Nombre_Prioridad,'idmovimiento':val.Id_Movimiento} for val in rowsresult]	

	elif tipo=='REFERENCIA':
		sql_="""WITH UltimosMovimientos AS (	SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS fila
  		FROM MOVIMIENTO WHERE Tipo_Flujo =? AND Id_Oficina_Destino = ?)
		SELECT D.Titulo,D.Id_Documento,M.Id_Movimiento
		FROM UltimosMovimientos M
		INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento INNER JOIN PERSONA AS P ON D.Emisor=P.Dni
		INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad=TP.Id_TiposPrioridad INNER JOIN Tipo_Documento AS TD ON D.Id_TipoDocumento=TD.Id_TipoDocumento
		INNER JOIN Oficina AS O ON M.Id_Oficina_Origen=O.Id_Oficina INNER JOIN Adjunto AS A ON D.Id_Adjunto=A.Id_Adjunto
		WHERE M.fila = 1 AND D.Estado IN (?,?) AND D.Titulo LIKE ?"""
		parametros=('Ingreso',current_user.id_oficina,2,5,'%'+valor+'%')
		rowsresult=objConsulta.ConsultaMainDocParams(sql_,parametros)
		datos=[{'titulo':val.Titulo,'iddocumento':val.Id_Documento,'idmovimiento':val.Id_Movimiento} for val in rowsresult]	



	return jsonify({'tipo':tipo,'datos':datos})

@documento_bp.route('/searchobservados',methods=['POST'])
def SearchObservados():
	valor=request.form.get('valor')
	sql="""WITH ULTIMOSMOVIMIENTOS AS ( SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento 
					DESC) AS fila FROM MOVIMIENTO)	SELECT FORMAT(UM.Fecha_Movimiento,'yyyy-MM-dd HH:mm') AS Fecha_Movimiento,UM.comentarios,
					D.Asunto,D.Titulo,UM.Id_Movimiento FROM 
					ULTIMOSMOVIMIENTOS AS UM INNER JOIN DOCUMENTO AS D ON UM.Id_Documento=D.Id_Documento WHERE UM.fila=1 AND 
					UM.Id_Accion=? AND UM.Id_Oficina_Destino=? AND D.Titulo LIKE ?"""
	params=(4,current_user.id_oficina,"%"+valor+"%")	
	objConsulta=QueryDocumentos()
	datos=[]
	try:
		rows=objConsulta.ConsultaMainDocParams(sql,params)
		datos=[{'titulo':val.Titulo,'asunto':val.Asunto,'fecha':val.Fecha_Movimiento,'observacion':val.comentarios,'idmov':val.Id_Movimiento} for val in rows]
	except Exception as e:
		print(e)
	return jsonify({'datos':datos})

@documento_bp.route('/otherdocumentos')
@requires_permission(Permiso.DOC_OTHERS)
@login_required
def OtherDocuments():
	return render_template('/documentos/doc_others.html',info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina})

@documento_bp.route('/filtertypedocument',methods=['POST'])
@login_required
def FilterTypeDocument():
	seleccion=request.form.get('seleccion')
	datos=[]
	objConsulta=QueryDocumentos()
	if seleccion=='ANULADO':
		sql="""WITH ULTIMOSMOVIMIENTOS AS (SELECT *,ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS Fila FROM MOVIMIENTO)
		SELECT TOP 50 FORMAT(UM.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) AS NEmisor,
		D.Asunto,D.Titulo,UM.Id_Movimiento,D.CodigoSeguimiento,UM.comentarios,U.Nombre_Usuario
		FROM ULTIMOSMOVIMIENTOS AS UM INNER JOIN DOCUMENTO AS D ON UM.Id_Documento=D.Id_Documento INNER JOIN PERSONA AS P 
		ON D.Emisor=P.Dni INNER JOIN USUARIO AS U ON UM.Id_Usuario=U.Id_Usuario WHERE 
		UM.Fila=? AND D.Estado=? AND UM.Id_Oficina_Origen=? ORDER BY UM.Fecha_Movimiento DESC"""
		params=(1,7,current_user.id_oficina)

		try:
			rows=objConsulta.ConsultaMainDocParams(sql,params)
			datos=[{'titulo':val.Titulo,'fecha':val.FechaFormateada,'usuario':val.Nombre_Usuario,'codigo':val.CodigoSeguimiento,'detalles':val.comentarios} for val in rows]
		except Exception as e:
			print(e)

	elif seleccion=='ARCHIVADO':
		sql="""WITH ULTIMOSMOVIMIENTOS AS (SELECT *,ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS Fila FROM MOVIMIENTO)
		SELECT TOP 50 FORMAT(UM.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) AS NEmisor,
		D.Asunto,D.Titulo,UM.Id_Movimiento,D.CodigoSeguimiento,UM.comentarios,U.Nombre_Usuario
		FROM ULTIMOSMOVIMIENTOS AS UM INNER JOIN DOCUMENTO AS D ON UM.Id_Documento=D.Id_Documento INNER JOIN PERSONA AS P 
		ON D.Emisor=P.Dni INNER JOIN USUARIO AS U ON UM.Id_Usuario=U.Id_Usuario WHERE 
		UM.Fila=? AND D.Estado=? AND UM.Id_Oficina_Origen=? ORDER BY UM.Fecha_Movimiento DESC"""
		params=(1,6,current_user.id_oficina)
		try:
			rows=objConsulta.ConsultaMainDocParams(sql,params)
			datos=[{'titulo':val.Titulo,'fecha':val.FechaFormateada,'usuario':val.Nombre_Usuario,'codigo':val.CodigoSeguimiento,'detalles':val.comentarios} for val in rows]
		except Exception as e:
			print(e)	

	return jsonify({'datos':datos})

@documento_bp.route('/searchotherdocuments',methods=['POST'])
@requires_permission(Permiso.DOC_OTHERS)
@login_required
def searchftdocument():
	valor=request.form.get('valor')
	tipo=request.form.get('tipo')
	datos=[]
	objConsulta=QueryDocumentos()
	if tipo=='ANULADO':
		sql="""WITH ULTIMOSMOVIMIENTOS AS (SELECT *,ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS Fila FROM MOVIMIENTO)
		SELECT TOP 50 FORMAT(UM.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) AS NEmisor,
		D.Asunto,D.Titulo,UM.Id_Movimiento,D.CodigoSeguimiento,UM.comentarios,U.Nombre_Usuario
		FROM ULTIMOSMOVIMIENTOS AS UM INNER JOIN DOCUMENTO AS D ON UM.Id_Documento=D.Id_Documento INNER JOIN PERSONA AS P 
		ON D.Emisor=P.Dni INNER JOIN USUARIO AS U ON UM.Id_Usuario=U.Id_Usuario WHERE 
		UM.Fila=? AND D.Estado=? AND UM.Id_Oficina_Origen=? AND D.Titulo LIKE ?"""
		params=(1,7,current_user.id_oficina,'%'+valor+'%')

		try:
			rows=objConsulta.ConsultaMainDocParams(sql,params)
			datos=[{'titulo':val.Titulo,'fecha':val.FechaFormateada,'usuario':val.Nombre_Usuario,'codigo':val.CodigoSeguimiento,'detalles':val.comentarios} for val in rows]
		except Exception as e:
			print(e)

	elif tipo=='ARCHIVADO':
		sql="""WITH ULTIMOSMOVIMIENTOS AS (SELECT *,ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS Fila FROM MOVIMIENTO)
		SELECT TOP 50 FORMAT(UM.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) AS NEmisor,
		D.Asunto,D.Titulo,UM.Id_Movimiento,D.CodigoSeguimiento,UM.comentarios,U.Nombre_Usuario
		FROM ULTIMOSMOVIMIENTOS AS UM INNER JOIN DOCUMENTO AS D ON UM.Id_Documento=D.Id_Documento INNER JOIN PERSONA AS P 
		ON D.Emisor=P.Dni INNER JOIN USUARIO AS U ON UM.Id_Usuario=U.Id_Usuario WHERE 
		UM.Fila=? AND D.Estado=? AND UM.Id_Oficina_Origen=? AND D.Titulo LIKE ?"""
		params=(1,6,current_user.id_oficina,'%'+valor+'%')
		try:
			rows=objConsulta.ConsultaMainDocParams(sql,params)
			datos=[{'titulo':val.Titulo,'fecha':val.FechaFormateada,'usuario':val.Nombre_Usuario,'codigo':val.CodigoSeguimiento,'detalles':val.comentarios} for val in rows]
		except Exception as e:
			print(e)	

	return jsonify({'datos':datos})

#documentos generados
@documento_bp.route('/documents_generate')
@requires_permission(Permiso.DOC_BSALIDA)
@login_required
def documentosGenerate():
	objConsulta=QueryDocumentos()
	sql="""
	WITH UltimosMovimientos AS (
  	SELECT *,
         ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento DESC) AS fila
  	FROM MOVIMIENTO WHERE Tipo_Flujo =? AND Id_Oficina_Origen =? )

	SELECT FORMAT(M.Fecha_Movimiento, 'yyyy-MM-dd HH:mm') AS FechaFormateada,
	CONCAT(P.Nombre,' ',P.ApellidoPaterno,' ',P.ApellidoMaterno) AS NEmisor,TD.Nombre_TipoDocumento,
	D.Asunto,O.nombre_oficina,TP.Nombre_Prioridad,A.url_archivo,D.Titulo,M.Id_Movimiento,D.CodigoSeguimiento,U.Nombre_Usuario
	FROM UltimosMovimientos M
	INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento INNER JOIN PERSONA AS P ON D.Emisor=P.Dni
	INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad=TP.Id_TiposPrioridad INNER JOIN Tipo_Documento AS TD ON D.Id_TipoDocumento=TD.Id_TipoDocumento
	INNER JOIN Oficina AS O ON M.Id_Oficina_Destino=O.Id_Oficina INNER JOIN Adjunto AS A ON D.Id_Adjunto=A.Id_Adjunto
	INNER JOIN USUARIO AS U ON M.Id_Usuario=U.Id_Usuario
	WHERE M.fila = 1 AND D.Estado IN (?) ORDER BY M.Fecha_Movimiento DESC;"""
	params=('Egreso',current_user.id_oficina,1)
	rows=[]
	try:
		rows=objConsulta.ConsultaMainDocParams(sql,params)
	except Exception as e:
		raise e
	return render_template('/documentos/doc_generados.html',info={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina},rows=rows)


@documento_bp.route('/anulardocumento',methods=['POST'])
@requires_permission(Permiso.DOC_NUEVO)
@login_required
def AnularDocumento():
	objConsulta=QueryDocumentos()
	indicador=0
	idmovimiento=request.form.get('idmovimiento')
	accion=request.form.get('accion')
	comentario=request.form.get('comentario')
	sql_insertar="""INSERT INTO MOVIMIENTO(Id_Documento,Id_Usuario,Fecha_Movimiento,Id_Accion,comentarios,Id_Oficina_Origen,
	Id_Oficina_Destino,numeroIngreso,numeroEgreso,Tipo_Flujo) OUTPUT INSERTED.Id_Movimiento
	VALUES(?,?,GETDATE(),?,?,?,?,?,?,?)"""

	sql="""SELECT * FROM MOVIMIENTO WHERE Id_Movimiento=?"""
	rows_Anterior=objConsulta.ConsultaMainDocParams(sql,(idmovimiento,))
	params=(rows_Anterior[0].Id_Documento,current_user.id,12,comentario,current_user.id_oficina,None,0,0,'Interno')

	idmov=objConsulta.InsertDataIdentity(sql_insertar,params)
	
	if idmov:
		sql_documento="UPDATE DOCUMENTO SET Estado=? WHERE Id_Documento=?"
		parametros=(7,rows_Anterior[0].Id_Documento)
		indicador=objConsulta.InsertDataGeneral(sql_documento,parametros)

	return jsonify(indicador)

@documento_bp.route('/searchdocreference',methods=['POST'])
@login_required
def SearchReference():
	objConsulta=QueryDocumentos()
	valor=request.form.get('valor')
	sql=""" """
	return jsonify(0)


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
	D.Asunto,O.nombre_oficina,TP.Nombre_Prioridad,A.url_archivo,D.Titulo,M.Id_Movimiento,D.CodigoSeguimiento
	FROM UltimosMovimientos M
	INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento INNER JOIN PERSONA AS P ON D.Emisor=P.Dni
	INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad=TP.Id_TiposPrioridad INNER JOIN Tipo_Documento AS TD ON D.Id_TipoDocumento=TD.Id_TipoDocumento
	INNER JOIN Oficina AS O ON M.Id_Oficina_Origen=O.Id_Oficina INNER JOIN Adjunto AS A ON D.Id_Adjunto=A.Id_Adjunto
	WHERE M.fila = 1 AND D.Estado IN (?,?) ORDER BY M.Fecha_Movimiento DESC;"""
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
	WHERE M.fila = 1 AND M.Tipo_Flujo = 'Egreso'  AND M.Id_Oficina_Destino = ?  AND D.Estado IN (1, 3) ORDER BY M.Fecha_Movimiento DESC"""
	rows=objConsulta.ConsultaMainDocParams(sql,params)
	return rows



	

