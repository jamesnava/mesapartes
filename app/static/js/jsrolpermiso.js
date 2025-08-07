$(document).ready(function(){

	$('#btnaddmodulo').on('click',function(){
		$('#AgregarModulos').modal('show');
	});

	$('#rolguardar').on('click',function(event){
		nombre=$('#txtMdenominacion').val()
		$.ajax({
			type:'POST',
			url:'/rol/insertmodulo',
			data:{denominacion:nombre},
			success:function(response){
				
				if(response==1){
					mostrarMensaje('success','se insertó correctamente!!')
					setTimeout(function(){location.reload(true);},1000);
				}
				else{
					mostrarMensaje('error','no se pudo insertar!')
					setTimeout(function(){location.reload(true);},1000);
				}
			}
		});
	});

	$('.delmodulo').on('click',function(){
		let codigo=$(this).data('codigo');
		Swal.fire({
    	title: 'Borrar',
    	text: "¿Estas seguro de eliminar?",
    	icon: 'warning',
    	showCancelButton: true,
    	confirmButtonText: 'Sí, continuar',
    	cancelButtonText: 'Cancelar'
  			}).then((result) => {
  			if (result.isConfirmed) {
  				$.ajax({type:'POST',url:'/rol/delmodulo',data:{'codigo':codigo},
				success:function(response){
					
					if(response===1){mostrarMensaje('success','Se eliminó correctamente!'); setTimeout(function(){location.reload(true)},1000)}

					else{mostrarMensaje('error','no pudo eliminarse!'); setTimeout(function(){location.reload(true)},1000)}
				}
			});

  		 }
  		});
		
	});


	$('.checkperfil').on('click',function(){
		let valor=$(this).data('id');
		$.ajax({
			type:'POST',
			url:'/rol/queryperfildetalle',
			data:{'valor':valor},
			success: function(response){
				$('#perfilesmodulo').empty()
				$.each(response.datos,function(index,valores){
					$('#perfilesmodulo').append(`<tr>
						<td>${valores.id}</td>
						<td>${valores.permiso}</td>
						</tr>`)
				});
			}
		});

	});

	$('#createperfil').on('click',function(){
		let seleccionados=[];
		$('#tablemodulos tbody tr').each(function(){
			let check=$(this).find('.checkboxm');
			if (check.is(':checked')){
				id=$(check).data('idmo');
				seleccionados.push({'id':id})
			}

		});

		let marcado = $('.checkperfil').filter(':checked').first();
		idrol=marcado.data('id');

		data={'idrol':idrol,'perfil':seleccionados}
		$.ajax({
			url:'/rol/createperfil',
			type:'POST',
			contentType:'application/json',
			data:JSON.stringify(data),
			success:function(response){
				if (response==1){
					mostrarMensaje('success','Se actualizó correctamente!!');
					setTimeout(function(){location.reload(true)},1000);
				}
				else{
					mostrarMensaje('error','no pudo actualizar!');
					setTimeout(function(){location.reload(true)},1000);
				}
			}
		});
		
	});

	$('#btnaddroles').on('click',function(){
		$('#Agregarroles').modal('show');

	});

	$('#permisoguardar').on('click',function(){
		let denominacion=$('#txtRDenominacion').val();
		$.ajax({
			type:'POST',
			url:'/rol/insertpermiso',
			data:{'denominacion':denominacion},
			success: function(response){
				if (response==1){
					mostrarMensaje('success','Se inserto correctamente!');
					setTimeout(function(){location.reload(true);},1000);
				}
				else{
					mostrarMensaje('error','no pudo insertarse');
					setTimeout(function(){location.reload(true);},1000);
				}
			}
		});
	});


});