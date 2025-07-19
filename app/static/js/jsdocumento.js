$(document).ready(function(){
$('#cargarPlantilla').on('click',function(){
	//cargar numeracion
	tflujo='Ingreso';
	$.ajax({
		type:'POST',
		url:'/documents/tflujo',
		data:{flujo:tflujo},
		success:function(response){
			$('#numeracion').val("");
			$('#numeracion').val(response.numeracion);
			$('#numeracion').attr("readonly",true);

			$('#NSeguimiento').val("");
			$('#NSeguimiento').val(response.codigoS);
			$('#NSeguimiento').attr("readonly",true);
		}
	});
	
	$.ajax({
		url:'/documents/nuevodoc',
		type:'POST',		
		success:function(response){
			$('#Tdoc').empty()
			$('#prioridad').empty()
			$.each(response.prioridad,function(index,nombre){
				$('#prioridad').append(`<option value=${nombre.id}>${nombre.nombre}</option>`)
			});
			$.each(response.tipodocumento,function(index,nombre){
				$('#Tdoc').append(`<option value=${nombre.id}>${nombre.nombre}</option>`)
			});
			
		}
	});
});

$('#destino').on('keyup',function(){
	valor=$('#destino').val();
	$.ajax({
		url:'/documents/searchkey',
		type:'POST',
		data:{valor:valor},
		success:function(response){
			var resultadosHtml='';
			$.each(response.oficinas,function(index,oficinas){
				resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${oficinas.id}>${oficinas.nombre} </p>`;
			});
			$('#iddivdestino').show()
			$('#iddivdestino').html(resultadosHtml);
		}
	});
});

$('#iddivdestino').on('click','p',function(){
	const id=$(this).data('id');
	const nombre=$(this).text();
	let duplicado=false;
	$('#tableoficinas tbody tr').each(function() {
    const idActual = $(this).find('td:first').text();
    if (idActual == id) {
      duplicado = true;
      return false; // salir del bucle
    }
  });
	
	if(!duplicado){
	const nuevafila=`<tr>
	<td>${id}</td>
	<td>${nombre}</td>
	<td><button class="btn btn-sm btn-danger eliminaroficinas">Quitar</button></td></td>
	</tr>`

	$('#tableoficinas tbody').append(nuevafila);
	$('#iddivdestino').hide()
	$('#destino').val("");
}
else{
	mostrarMensaje('warning', 'Esta oficina ya ha sido agregada');
}
});

$('#tableoficinas').on('click','.eliminaroficinas',function(){
	$(this).closest('tr').remove();
});




$('#oficinaDestino').on('keyup',function(){
	valor=$(this).val();
	$.ajax({
		url:'/documents/searchkey',
		type:'POST',
		data:{valor:valor},
		success:function(response){
			var resultadosHtml='';
			$.each(response.oficinas,function(index,oficinas){
				resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${oficinas.id}>${oficinas.nombre} </p>`;
			});
			$('#iddivdestinoD').show()
			$('#iddivdestinoD').html(resultadosHtml);
		}
	});
});

$('#iddivdestinoD').on('click','p',function(){
	const id=$(this).data('id');
	const nombre=$(this).text();	

// Verificar si ya existe alguna fila en la tabla
	const totalFilas = $('#tableoficinasD tbody tr').length;

	if (totalFilas > 0) {
  	mostrarMensaje('warning', 'Solo puedes agregar una oficina destino');
  	return;
							}

// Si no hay filas, agregamos la nueva
	const nuevafila = `<tr>
  <td>${id}</td>
  <td>${nombre}</td>
  <td><button class="btn btn-sm btn-danger quitaroficina">Quitar</button></td>
	</tr>`;

	$('#tableoficinasD tbody').append(nuevafila);
	$('#iddivdestinoD').hide();
	$('#oficinaDestino').val("");
});


$('#tableoficinasD').on('click','.quitaroficina',function(){
	$(this).closest('tr').remove();
});




$('#Emisor').on('keydown',function(event){

	if(event.key=='Enter'){
	event.preventDefault(); 
	dni=$('#Emisor').val()
	$.ajax({
		type:'POST',
		url:'/documents/filldata',
		data:{dni:dni},
		success:function(response){			
			if (response.datos.length!=0){
				$('#DEmisor').val('')
				emisor=response.datos[0]['nombre']+' '+response.datos[0]['apellidoP']+' '+response.datos[0]['apellidoM'];
				$('#DEmisor').val(emisor);
			}
			else{
				mostrarMensaje('error','Datos no encontrados');
			}

		}
	});
}

});

$('#grabardoc').on('click',function(){

	const formData=new FormData($('#formulariodocumento')[0]);
	let totalFilas = 0;
	//recorremos la tabla
	$('#tableoficinas tbody tr').each(function(index,fila){

		const codigo=$(fila).find('td:eq(0)').text().trim();
		const oficina=$(fila).find('td:eq(1)').text().trim();	    
            
    formData.append('codigos[]', codigo);
    formData.append('oficinas[]', oficina);  	

	});

	idusuario=$('#usuario_id').val()
	oficina=$('#oficina').val()

	formData.append('idusuario',idusuario)
	formData.append('idoficinaorigen',oficina)

	$.ajax({
		url:'/documents/insertdocument',
		type:'POST',
		data:formData,
		contentType:false,
		processData:false,
		success: function(response){
			if (response!=0){
				mostrarMensaje('success','Exitoso!');
				location.reload(true);
			}
			else{
				mostrarMensaje('error','Ocurrio Algo!');
				location.reload(true);
			}

		}
	});

});

$('.ver-pdf').on('click',function(){
	const url=$(this).data('url');
	$('#visorPDF').attr('src', "/static/uploads/"+url);
  $('#verpdf').modal('show');
});

$('.acciones').on('click',function(){

	$.ajax({
		url:'/documents/acciones',
		type:'POST',
		
		success:function(response){
			$.each(response.acciones,function(index,acciones){
				$('#tipoAccion').append(`<option value=${acciones.Id_Accion}>${acciones.Nombre_Accion}</option>`);
			});
		}
	});
	$('#veracciones').modal('show');
});

$('#tipoAccion').on('change',function(){
	const accion=$(this).val();
	if (accion==3){
		$('#panelDerivar').show();
	}
	else{
		$('#panelDerivar').hide();

	}
});

$('.recepcionardoc').on('click',function(){
	const id=$(this).data('idmovimiento');
	const oficina=$('#oficina').val();
	const idusuario=$('#usuario_id').val();
	$.ajax({
		url:'/documents/recepcionardoc',
		type:'POST',
		data:{'idDoc':id,'oficina':oficina,'idusuario':idusuario},
		success:function(response){
			if (response!=0){
				location.reload(true);
				mostrarMensaje('success','Recepcionado');
			}
			else{
				mostrarMensaje('error','Error!!');
			}
		}
	});

});

$('#btnConfirmarAccion').on('click',function(){
	accion=$('#tipoAccion').val();
	comentario=$('#comentarioAccion').val();
	idmovimiento=$('#idmov').val();
	const codigo = $('#tableoficinasD tbody tr:first td:first').text();
	$.ajax({
			url:'/documents/confirmaraccion',
			type:'POST',
			data:{'accion':accion,'comentario':comentario,'idmovimiento':idmovimiento,'codigoOf':codigo},
			success:function(response){
				location.reload(true);

			}
	});

});


});