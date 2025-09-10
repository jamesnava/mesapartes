from flask import Blueprint,redirect,render_template,url_for,jsonify
from app.grafico.dash_reporte import grafico_documentos_por_oficina
from app.modelos.QueryDocumento import QueryDocumentos


reporte_bp=Blueprint('reports',__name__,url_prefix="/reports")

@reporte_bp.route('/ReporteMain')
def reporteMain():
	objConsulta=QueryDocumentos()
	'''documento generados'''
	sql_documentosgenerados="""SELECT O.nombre_oficina,COUNT(*) AS CANTIDAD FROM DOCUMENTO D INNER JOIN Oficina O ON D.Id_Oficina_Origen=O.Id_Oficina 
								GROUP BY O.nombre_oficina"""
	rows_docgenerados=objConsulta.ConsultaMainDoc(sql_documentosgenerados)
	oficinas=[]
	cantidad=[]
	for val in rows_docgenerados:
		oficinas.append(val.nombre_oficina)
		cantidad.append(val.CANTIDAD)
	grafico1=grafico_documentos_por_oficina({'Oficina':oficinas,'Cantidad':cantidad})

	'''documentos recepcionados'''
	sql_documentosrecepcionados="""SELECT O.nombre_oficina,COUNT(*) AS CANTIDAD FROM MOVIMIENTO M INNER JOIN DOCUMENTO D ON M.Id_Documento=D.Id_Documento
							INNER JOIN Oficina O ON M.Id_Oficina_Destino=O.Id_Oficina
							WHERE M.Tipo_Flujo='Ingreso' GROUP BY O.nombre_oficina"""
	rows_docrecepcionados=objConsulta.ConsultaMainDoc(sql_documentosrecepcionados)
	oficinasr=[]
	cantidadr=[]
	for val in rows_docrecepcionados:
		oficinasr.append(val.nombre_oficina)
		cantidadr.append(val.CANTIDAD)
	recepcionados=grafico_documentos_por_oficina({'Oficina':oficinasr,'Cantidad':cantidadr})



	return render_template('reportes/reportesprincipal.html',grafico1=grafico1,docrecepcionados=recepcionados)

