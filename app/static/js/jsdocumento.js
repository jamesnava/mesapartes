$(document).ready(function(){
  $(document).on('click', '.btnblockdubleclick', function (e) {
        let $btn = $(this);

    // Si ya se está procesando, cancela
    if ($btn.data('processing')) {
        e.preventDefault();
        e.stopImmediatePropagation(); // Evita que se ejecuten otros handlers del click
        return false;
    }

    // Marca como en proceso
    $btn.data('processing', true);

    // Deshabilita visualmente
    $btn.prop('disabled', true)
        .data('texto-original', $btn.text())
        .text('Procesando...');      
    });


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

			if (response.movimiento!=0){
				mostrarMensaje('success','Exitoso!');
				
				//mostrar div de impresion
				$('#verconstancia').attr('src',response.direccion);
				$('#constancia').modal('show');
				$('#constancia').on('hidden.bs.modal', function () {
  					location.reload(true);
				});

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
			$('#tipoAccion').empty();
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
			
			if (response==1){
				mostrarMensaje('success','Recepcionado');
				setTimeout(function(){location.reload(true);},1000);			
				
			}
			else{
				mostrarMensaje('error','Ocurrió un error');
			}
		},
		error: function(xhr,status,error){
			console.log(xhr.status);
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
				if (response==1)
				setTimeout(function(){location.reload(true);},1000);
			}
	});

});


$('#btnconsultar').on('click',function(){
	const codigo=$('#codigoSeguimiento').val();
	$.ajax({
		url:'/documents/followrequest',
		type:'POST',
		data:{'codigo':codigo} ,
		success:function(response){
			$('#resultadoSeguimiento').show();
      $('#historialTabla').empty();
      $('#lineaTiempo').show();
      const linea = $('.timeline');
      linea.empty();
			$.each(response.datos,function(index,valores){
				 $('#historialTabla').append(`
          <tr>
            <td>${valores.fecha}</td>
            <td>${valores.accion}</td>
            <td>${valores.origen}</td>
            <td>${valores.destino}</td>
            <td>${valores.usuario}</td>
            <td>${valores.comentario || ''}</td>
          </tr>`);

				 linea.append(`
          <li><strong>${valores.fecha}</strong>: ${valores.accion} — <em>${valores.origen}</em> → <em>${valores.destino}</em><br>${valores.comentario || ''}</li>`);
      
			});

		}
	});


});

//revertir
$('.salidadoc').on('click',function(){
	const idmovimiento=$(this).data('idmovimientoderivado');	
	  Swal.fire({
    title: '¿Estás seguro?',
    text: "Revertir documento",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Sí, continuar',
    cancelButtonText: 'Cancelar'
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
      		url:'/documents/revertirdoc',
      		type:'POST',
      		data:{'idmovimiento':idmovimiento},
      		success:function(response){
      			console.log(response);
      			if (response==1){
      				mostrarMensaje('success','Se revertió, correctamente');
      				setTimeout(function(){location.reload(true);},1000);
      			}
      			else{
      				mostrarMensaje('error','ocurrió un error!')
      				setTimeout(function(){location.reload(true);},1000);
      			}
      			

      		}

      });

    }
  });


});

$('.btnsubsanar').on('click',function(){
	const idmovimiento=$(this).data('idmovimientosubsanar');
	$('#idmovimientooculto').val(idmovimiento);
	$('#modalsubsanar').modal('show');

});

$('#btnconfirmarsubsanacion').on('click',function(){
	const formData=new FormData($('#formsubsanacion')[0]);

	$.ajax({
		url:'/documents/subsanacion',
		type:'POST',
		data:formData,
		contentType:false,
		processData:false,
		success:function(response){
			if(response!=0){
				mostrarMensaje('success','Exitoso!');
				setTimeout(function(){location.reload(true);},1000);
			}
			else{
				mostrarMensaje('error','No pudo subsanarse');
				setTimeout(function(){location.reload(true);},1000);
			}
		}
	});


});

$('.comentarios').on('click',function(){
	const idmovimiento=$(this).data('idmovimiento');
	$('#vercomentarios').modal('show');
	$.ajax({
		type:'POST',
		url:'/documents/vercomentarios',
		data:{'idmovimiento':idmovimiento},
		success: function(response){
			$('#spancomentarios').text('');
			$('#spancomentarios').text(response.comentarios);
		}

	});

});

//validar adjunto
$('#adjunto').on('change', function () {
			
				const maxSizeMB = 2;
        let archivo = this.files[0];
        if (!archivo) return;

        // Verifica tamaño
        if (archivo.size > maxSizeMB * 1024 * 1024) {
            mostrarMensaje('error', `El archivo supera el límite de ${maxSizeMB}MB.`);
            $(this).val(''); // Limpiar campo
            return;
        }      
    });



$('input[name="rfilter"]').on('change',function(){
	const seleccion=$(this).val();
	$.ajax({
		url:'/documents/fillhistorico',
		type:'POST',
		data:{'tipo':seleccion} ,
		success:function(response){
			$('#tablehistorico').empty()
			$.each(response.datos,function(index,valores){
				$('#tablehistorico').append(`
					<tr>
					<td>${valores.numeracion}</td>
					<td>${valores.titulo}</td>
					<td>${valores.fecha}</td>
					<td>${valores.usuario}</td>
					<td>${valores.oficina}</td>
					<td>${valores.flujo}</td>
					<td>${valores.codigo}</td>
					<td><button class="btn btn-success"><i class="fas fa-eye" aria-hidden="true" title="ver"></i></button></td>
					</tr>
					`);
			});

		}
	});

});

$('#btndocpendientes').on('keyup',function(){
let valor=$(this).val();
$.ajax({
	type:'POST',
	url:'/documents/searchdocuments',
	data:{'valor':valor,'tipo':'RECEPCION'},
	success:function(response){
		if (response.tipo=="RECEPCION"){
			//condicional prioridad
			tablehtml=$('#tablaBandejapendienterecepcion').empty();
			$.each(response.datos,function(index,valores){
				const colorprioridad=obtenerClasePrioridad(valores.nombreprioridad);				
				tablehtml.append(
					`<tr>
					<td>${valores.fecha}</td>
					<td>${valores.titulo}</td>
					<td>${valores.nameemisor}</td>
					<td>${valores.tipodoc}</td>
					<td>${valores.asunto}</td>
					<td>${valores.oficina}</td>
					<td style="text-align: center;">					
					<i aria-hidden="true" class="fas fa-circle ${colorprioridad}
					  title="${valores.nombreprioridad}">
             </i>
					</td>
					<td>
						<button class="btn btn-primary ver-pdf" data-url="${valores.url}" type="button">
              <i class="fas fa-file-pdf" title="Ver documento"></i>
            </button>
            <button class="btn btn-success recepcionardocd" data-idmovimiento="${valores.idmovimiento}" type="button">
              <i class="fas fa-check-circle" title="Recepcionar documento"></i>
            </button>
            <button class="btn btn-danger comentarios" data-idmovimiento="${valores.idmovimiento}" type="button">
             	<i class="fas fa-comments" title="Ver datos adicionales"></i>
            </button>
					</td>
					</tr>`
					);
			});
		}

	}
});

});

$('#btndocrecepcionados').on('keyup',function(){
let valor=$(this).val();
$.ajax({
	type:'POST',
	url:'/documents/searchdocuments',
	data:{'valor':valor,'tipo':'RECEPCIONADOS'},
	success:function(response){
		if (response.tipo=="RECEPCIONADOS"){
			//condicional prioridad
			tablehtml=$('#tablaBandejarecepcionados').empty();
			$.each(response.datos,function(index,valores){
				const colorprioridad=obtenerClasePrioridad(valores.nombreprioridad);				
				tablehtml.append(
					`<tr>
					<td>${valores.fecha}</td>
					<td>${valores.titulo}</td>
					<td>${valores.nameemisor}</td>
					<td>${valores.tipodoc}</td>
					<td>${valores.asunto}</td>
					<td>${valores.oficina}</td>
					<td style="text-align: center;">					
					<i aria-hidden="true" class="fas fa-circle ${colorprioridad}
					  title="${valores.nombreprioridad}">
             </i>
					</td>
					<td>${valores.codseg}</td>
					<td>
						 	<button class="btn btn-primary ver-pdf" data-url="${valores.url}" type="button">
                <i class="fas fa-file-pdf" title="Ver documento"></i>
              </button>
              <button class="btn btn-success acciones" data-idmovimiento="${valores.idmovimiento}" type="button">
                <i class="fas fa-paper-plane" title="Acciones"></i>
              </button>
              <button class="btn btn-danger " data-idmovimiento="${valores.idmovimiento}" type="button">
                <i class="fas fa-undo" title="Revertir"></i>
              </button>
					</td>
					</tr>`
					);
			});
		}


	}
});

});


$('#tablaBandejapendienterecepcion, #tablaBandejarecepcionados').on('click','.ver-pdf',function(){
	const url=$(this).data('url');
	$('#visorPDF').attr('src', "/static/uploads/"+url);	
  $('#verpdf').modal('show');
});


$('#tablaBandejapendienterecepcion').on('click','.recepcionardocd',function(){
	const id=$(this).data('idmovimiento');
	const oficina=$('#oficina').val();
	const idusuario=$('#usuario_id').val();
	$.ajax({
		url:'/documents/recepcionardoc',
		type:'POST',
		data:{'idDoc':id,'oficina':oficina,'idusuario':idusuario},
		success:function(response){
			
			if (response==1){				
				mostrarMensaje('success','Recepcionado');
				setTimeout(function(){location.reload(true);},1000);
			}
			else{
				mostrarMensaje('error','Error!!');
			}
		}
	});

});

$('#tablaBandejapendienterecepcion').on('click','.comentarios',function(){
	const idmovimiento=$(this).data('idmovimiento');
	$('#vercomentarios').modal('show');
	$.ajax({
		type:'POST',
		url:'/documents/vercomentarios',
		data:{'idmovimiento':idmovimiento},
		success: function(response){
			$('#spancomentarios').text('');
			$('#spancomentarios').text(response.comentarios);
		}

	});

});

$('#tablaBandejarecepcionados').on('click','.acciones',function(){
	$('#idmovi').val($(this).data('idmovimiento'));
	$.ajax({
		url:'/documents/acciones',
		type:'POST',
		
		success:function(response){
			$('#tipoAccion').empty();
			$.each(response.acciones,function(index,acciones){
				$('#tipoAccion').append(`<option value=${acciones.Id_Accion}>${acciones.Nombre_Accion}</option>`);
			});
		}
	});
	$('#veracciones').modal('show');
});


$('#veracciones').on('click','#btnConfirmarAccion',function(){
	accion=$('#tipoAccion').val();
	comentario=$('#comentarioAccion').val();
	idmovimiento=$('#idmovi').val();
	const codigo = $('#tableoficinasD tbody tr:first td:first').text();	
	$.ajax({
			url:'/documents/confirmaraccion',
			type:'POST',
			data:{'accion':accion,'comentario':comentario,'idmovimiento':idmovimiento,'codigoOf':codigo},
			success:function(response){
				if (response==1)
				setTimeout(function(){location.reload(true);},1000);
			}
	});

});

$('#buscarobservados').on('keyup',function(){
	let valor=$(this).val();
	$.ajax({
		url:'/documents/searchobservados',
		type:'POST',
		data:{'valor':valor},
		success:function(response){
			tablehtml=$('#tablebodyobservados');
			tablehtml.empty();
			$.each(response.datos,function(index,valores){
				tablehtml.append(`<tr>
					<td>${valores.titulo}</td>
					<td>${valores.asunto}</td>
					<td>${valores.fecha}</td>
					<td>${valores.observacion}</td>
					<td>
						<button class="btn btn-primary btnsubsanar" data-idmovimientosubsanar="${valores.idmov}" type="button">
              <i class="fas fa-pencil-square-o" title=" Subsanar"></i>
            </button>
					</td>
					</tr>`);
			});
		}
	});
});


$('#tablebodyobservados').on('click','.btnsubsanar',function(){
	const idmovimiento=$(this).data('idmovimientosubsanar');
	$('#idmovimientooculto').val(idmovimiento);
	$('#modalsubsanar').modal('show');

});

$('#txtbuscarhistorial').on('keyup',function(){
	let valradio=$('input[name="rfilter"]:checked').val();
	let tipo=$(this).val();
	if (valradio){
		$.ajax({
			type:'POST',
			url:'/documents/filterfillhistorico',
			data:{'radio':valradio,'argumento':tipo},
			success:function(response){
				tablehtml=$('#tablehistorico');
				tablehtml.empty();				
					$.each(response.datos,function(index,valores){
						tablehtml.append(`
						<tr>
							<td>${valores.numeracion}</td>
							<td>${valores.titulo}</td>
							<td>${valores.fecha}</td>
							<td>${valores.usuario}</td>
							<td>${valores.oficina}</td>
							<td>${valores.flujo}</td>
							<td>${valores.codigo}</td>
							<td></td>
						</tr>
						`);
					});					

			}
		});

	}
	else{
		mostrarMensaje('error','Seleccion el tipo de registro!');
	}

});
$('input[name="Dfilter"]').on('change',function(){
	const seleccion=$(this).val();
	$.ajax({
		type:'POST',
		url:'/documents/filtertypedocument',
		data:{'seleccion':seleccion},
		success:function(response){
			tablehtml=$('#tablehistoricoD');
			tablehtml.empty();
			$.each(response.datos,function(index,valores){
				tablehtml.append(`<tr>
					<td>${valores.titulo}</td>
					<td>${valores.fecha}</td>
					<td>${valores.usuario}</td>
					<td>${valores.codigo}</td>
					<td>${valores.detalles}</td>				
					</tr>`);
			});

		}
	});
});

$('#txtbuscardocumento').on('keyup',function(){
const valor=$(this).val();
const tipo=$('input[name="Dfilter"]:checked').val();
$.ajax({
	type:'POST',
	url:'/documents/searchotherdocuments',
	data:{'valor':valor,'tipo':tipo},
	success:function(response){
		tablehtml=$('#tablehistoricoD');
		tablehtml.empty();
		$.each(response.datos,function(index,valores){
				tablehtml.append(`<tr>
					<td>${valores.titulo}</td>
					<td>${valores.fecha}</td>
					<td>${valores.usuario}</td>
					<td>${valores.codigo}</td>
					<td>${valores.detalles}</td>				
					</tr>`);
			});
	}
});

});



});

	function obtenerClasePrioridad(nombrePrioridad) {
    	switch (nombrePrioridad) {
        case 'Inmediata': return 'prioridad-inmediata';
        case 'Alta': return 'prioridad-alta';
        case 'Media': return 'prioridad-media';
        case 'Baja': return 'prioridad-baja';
        case 'Muy Baja': return 'prioridad-muy-baja';
        default: return '';
    	}
			}