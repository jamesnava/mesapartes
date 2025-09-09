from flask import Blueprint,redirect,render_template,url_for,jsonify
from app.grafico.dash_reporte import grafico_documentos_por_oficina


reporte_bp=Blueprint('reports',__name__,url_prefix="/reports")

@reporte_bp.route('/ReporteMain')
def reporteMain():
	grafico1=grafico_documentos_por_oficina()
	return render_template('reportes/reportesprincipal.html',grafico1=grafico1)

