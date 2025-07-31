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
				//mostrar div de impresion
				$('#verconstancia').attr('src', "/static/ticket/doc.pdf");
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
	//$('#visorPDF').attr('src', "/static/ticket/doc.pdf");
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
      			if (response!=0){
      				mostrarMensaje('success','Se revertio, correctamente');
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



});