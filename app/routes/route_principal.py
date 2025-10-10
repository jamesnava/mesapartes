from flask import Blueprint, render_template,redirect,url_for,request,g,jsonify
from flask_login import current_user,login_required
from app.modelos.QueryLogin import QueryL
from app.modelos.QueryDocumento import QueryDocumentos
from app.decoratos import requires_permission
from app.constanst import Permiso
from werkzeug.security import check_password_hash, generate_password_hash

main_bp=Blueprint('main',__name__,url_prefix='/main')

@main_bp.before_request
def cargar_usuario():
	if current_user.is_authenticated:
		obj_consulta=QueryL()
		sql=f"""SELECT U.Id_Usuario,U.Nombre_Usuario,U.Contrasena,U.Id_Oficina,U.Estado,O.nombre_oficina FROM USUARIO
	 		AS U INNER JOIN Oficina AS O ON U.Id_Oficina=O.Id_Oficina WHERE U.Id_Usuario=?"""
		g.user=obj_consulta.cargarUsuario(sql,(current_user.id))


@main_bp.route("/principal")
@login_required
def principal():
	objConsulta=QueryDocumentos()
	sql="""WITH UltimosMovimientos AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento, Id_Oficina_Destino ORDER BY Fecha_Movimiento DESC ) AS fila  FROM MOVIMIENTO)
	SELECT COUNT(M.Id_Movimiento) as pendientes       
	FROM UltimosMovimientos M INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento INNER JOIN PERSONA AS P ON D.Emisor = P.Dni INNER JOIN Tipos_Prioridad AS TP ON D.Prioridad = TP.Id_TiposPrioridad
	INNER JOIN Tipo_Documento AS TD ON D.Id_TipoDocumento = TD.Id_TipoDocumento INNER JOIN Oficina AS O ON M.Id_Oficina_Origen = O.Id_Oficina
	LEFT JOIN Adjunto AS A ON D.Id_Adjunto = A.Id_Adjunto WHERE M.fila = 1
  	AND M.Tipo_Flujo = 'Egreso'
  	AND M.Id_Oficina_Destino = ?          -- tu parámetro
  	AND M.Id_Accion IN (1,3)              -- pendiente (registrado o derivado)
  	AND NOT EXISTS (                      -- <--- filtra anulados
    SELECT 1 
    FROM MOVIMIENTO M2
    WHERE M2.Id_Documento = M.Id_Documento  AND M2.Id_Accion = 12  AND M2.Fecha_Movimiento > M.Fecha_Movimiento)
	"""
	params=(current_user.id_oficina)	
	rows=objConsulta.ConsultaMainDocParams(sql,params)

	#documentos pendiente a atencion
	sql_P_Atencion="""WITH UltimosMovimientos AS (SELECT *,ROW_NUMBER() OVER (PARTITION BY Id_Documento, Id_Oficina_Destino ORDER BY Fecha_Movimiento DESC
           ) AS fila  FROM MOVIMIENTO WHERE Tipo_Flujo = ? OR Tipo_Flujo=?  -- solo movimientos de ingreso
			)
	SELECT 
    COUNT(M.Id_Movimiento) as pendientes FROM UltimosMovimientos M
	INNER JOIN DOCUMENTO D ON M.Id_Documento = D.Id_Documento
	INNER JOIN PERSONA P ON D.Emisor = P.Dni
	INNER JOIN Tipos_Prioridad TP ON D.Prioridad = TP.Id_TiposPrioridad
	INNER JOIN Tipo_Documento TD ON D.Id_TipoDocumento = TD.Id_TipoDocumento
	INNER JOIN Oficina O ON M.Id_Oficina_Origen = O.Id_Oficina
	LEFT JOIN Adjunto A ON D.Id_Adjunto = A.Id_Adjunto
	WHERE M.fila = 1  AND M.Id_Accion IN (?,?)             -- pendiente de atención (recepcionado o derivado)
  	AND M.Id_Oficina_Destino =?         -- oficina actual
  	AND NOT EXISTS ( SELECT 1  FROM MOVIMIENTO M2  WHERE M2.Id_Documento = M.Id_Documento  AND M2.Fecha_Movimiento > M.Fecha_Movimiento
    AND ( M2.Id_Oficina_Origen = M.Id_Oficina_Destino -- ya salió de la oficina
          OR (M2.Id_Accion = 7 AND M2.Id_Oficina_Origen = M.Id_Oficina_Destino) -- archivado en esta oficina
      )                      
      
  )
"""

	#observados
	sql_observado="""WITH ULTIMOSMOVIMIENTOS AS ( SELECT *, ROW_NUMBER() OVER (PARTITION BY Id_Documento ORDER BY Fecha_Movimiento 
					DESC) AS fila FROM MOVIMIENTO)	
					SELECT COUNT(*) AS observados FROM 
					ULTIMOSMOVIMIENTOS AS UM INNER JOIN DOCUMENTO AS D ON UM.Id_Documento=D.Id_Documento WHERE UM.fila=1 AND 
					UM.Id_Accion=? AND UM.Id_Oficina_Destino=?"""


					
	rows_observados=objConsulta.ConsultaMainDocParams(sql_observado,(4,current_user.id_oficina))

	paramspatencion=('Ingreso','Interno',2,5,current_user.id_oficina)

	rows_pendientesAtencion=objConsulta.ConsultaMainDocParams(sql_P_Atencion,paramspatencion)
	

	#consultado la leyenda
	sql_leyenda="SELECT * FROM Tipos_Prioridad"
	rows_prioridades=objConsulta.ConsultaMainDoc(sql_leyenda)


	pendientesRecepcion=rows[0].pendientes if rows else 0	
	pendientesAtencion=rows_pendientesAtencion[0].pendientes if rows_pendientesAtencion else 0
	observadosdoc=rows_observados[0].observados if rows_observados else 0


	return render_template('/start/main.html',usuario=current_user.username,prioridades=rows_prioridades,oficina=current_user.nombre_oficina,pendientesRecepcion=pendientesRecepcion,pendientesA=pendientesAtencion,observados=observadosdoc)

@main_bp.route("/roles")
@requires_permission(Permiso.ROL,Permiso.PERMISO)
@login_required
def rolesPermisos():
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.nombre_oficina}
	return render_template('/roles/menuroles.html',datos=datos)

@main_bp.route('/documentos')
@requires_permission(Permiso.DOCUMENTO)
@login_required
def documentos():
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.id_oficina,'nombreo':current_user.nombre_oficina}
	return render_template('/documentos/doc_principal.html',datos=datos)

@main_bp.route('/oficinap')
@requires_permission(Permiso.OFICINA)
@login_required
def oficinaplantilla():
	objConsulta=QueryDocumentos()
	sql="""SELECT O1.nombre_oficina AS OPADRE,O1.Id_Oficina CPADRE,O2.nombre_oficina as OHIJO,O2.Id_Oficina AS CHIJO
	FROM Oficina AS O1 INNER JOIN Oficina AS O2 ON O2.Id_Oficina_Padre=O1.Id_Oficina"""
	rows_consulta=objConsulta.ConsultaMainDoc(sql)
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.nombre_oficina}
	return render_template('/oficinas/Oficinas.html',info=datos,rows=rows_consulta)



@main_bp.route('/peruser')
@requires_permission(Permiso.PERSONA,Permiso.USUARIO)
@login_required
def userperson():
	datos={'usuario':current_user.username,'dni':current_user.id,'oficina':current_user.nombre_oficina}
	return render_template('/personas/peruserprincipal.html',info=datos)

@main_bp.route('/changepassword',methods=['POST'])
@login_required
def ChangePassword():
	claveactual=request.form.get('claveactual')
	clave=request.form.get('clave')
	objConsulta=QueryDocumentos()
	numero=0	
	if (check_password_hash(current_user.password,claveactual)):
		sql="UPDATE USUARIO SET Contrasena=? WHERE Id_Usuario=?"
		params=(generate_password_hash(clave),current_user.id)
		try:
			numero=objConsulta.InsertDataGeneral(sql,params)
		except Exception as e:
			numero=0
		
	else:
		numero=-1

	return jsonify(numero)

