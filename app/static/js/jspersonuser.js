$(document).ready(function(){
	$('#btninsertpersona').on('click',function(){
		$('#insertarpersona').modal('show');
	});

	$('#insertperson').on('click',function(e){
		e.preventDefault();
		const formData= new FormData(document.getElementById('formulariopersona'));

		$.ajax({
			type:'POST',
			url:'/puser/insertperson',
			data:formData,
			contentType: false,
    		processData: false,
			success:function(response){
				if (response==-1){
					mostrarMensaje('error','Hay una persona registrada con el numero dni proporcionada');
					setTimeout(function(){location.reload(true)},1000);
				}
				else{ 
				if(response==1){
					mostrarMensaje('success','Se insertó correctamente');
					setTimeout(function(){location.reload(true);},1000);
				}
				else{
					mostrarMensaje('Error','No pudo insertarse');
				}
				}

			}
		});

	});

	$('.btneditarperson').on('click',function(){
		const dni=$(this).data('updni');
		$.ajax({
			type:'POST',
			url:'/puser/updateperson',
			data:{dni:dni},
			success:function(response){
				$.each(response.datos,function(index,valores){
					$('#dnipe').val(valores.dni);
					$('#nombrepe').val(valores.nombre);
					$('#apellidoppe').val(valores.apellidop);
					$('#apellidompe').val(valores.apellidom);
					$('#emailpe').val(valores.email);
					$('#telefonope').val(valores.telefono);
					$('#distritope').val(valores.distrito);
					$('#direccionpe').val(valores.direccion);
				});				
				
				$('#editarpersona').modal('show');

			}
		});

	});

	$('#tablehistorico').on('click','.btneditarperson',function(){
		const dni=$(this).data('updni');
		$.ajax({
			type:'POST',
			url:'/puser/updateperson',
			data:{dni:dni},
			success:function(response){
				$.each(response.datos,function(index,valores){
					$('#dnipe').val(valores.dni);
					$('#nombrepe').val(valores.nombre);
					$('#apellidoppe').val(valores.apellidop);
					$('#apellidompe').val(valores.apellidom);
					$('#emailpe').val(valores.email);
					$('#telefonope').val(valores.telefono);
					$('#distritope').val(valores.distrito);
					$('#direccionpe').val(valores.direccion);
				});				
				
				$('#editarpersona').modal('show');

			}
		});

	});


	$('#btnsaveupdateperson').on('click',function(e){
		e.preventDefault();
		const formData=new FormData(document.getElementById('formulariopersonaeditar'));
		$.ajax({
			type:'POST',
			url:'/puser/saveupdate',
			data:formData,
			contentType: false,
    		processData: false,
			success:function(response){
				if (response==1){
					mostrarMensaje('success','Exitoso!!');
					setTimeout(function(){location.reload(true);},1000);
				}

				}
		});
	});

	$('.btneliminarperson').on('click',function(){
		const dni = $(this).data('deldni');
		$.ajax({
			type:'POST',
			url:'/puser/deleteperson',
			data:{'dni':dni},
			success: function(response){
				if (response==1){
					mostrarMensaje('success','Se eliminó correctamente!')
					setTimeout(function(){location.reload(true);},1000);
				}
				else{
					if(response==0){
						mostrarMensaje('error','no pudo eliminar el registro!!');
					}
				}
			}
		});
	});

	$('#tablehistorico').on('click','.btneliminarperson',function(){
		const dni = $(this).data('deldni');
		$.ajax({
			type:'POST',
			url:'/puser/deleteperson',
			data:{'dni':dni},
			success: function(response){
				if (response==1){
					mostrarMensaje('success','Se eliminó correctamente!')
					setTimeout(function(){location.reload(true);},1000);
				}
				else{
					if(response==0){
						mostrarMensaje('error','no pudo eliminar el registro!!');
					}
				}
			}
		});
	});


	$('#buscarpersontxt').on('keyup',function(){
		const valor=$(this).val();
		$.ajax({
			type:'POST',
			url:'/puser/searchperson',
			data:{'datos':valor},
			success:function(response){
				$('#tablehistorico').empty();
				console.log(response);
				$.each(response.datos,function(index,valores){
					$('#tablehistorico').append(`<tr>
						<td>${valores.dni}</td>
						<td>${valores.nombre} ${valores.apellidop} ${valores.apellidom}</td>						
						<td>${valores.email}</td>
						<td>${valores.telefono}</td>
						<td>${valores.distrito}</td>
						<td>${valores.direccion}</td>
						<td>
							<button class="btn btn-success btneditarperson" data-updni=${valores.dni} ><i class="fas fa-pencil" aria-hidden="true" title="Editar"></i></button>
          					<button class="btn btn-danger btneliminarperson" data-deldni=${valores.dni}><i class="fas fa-trash" aria-hidden="true" title="Eliminar"></i></button>
						</td>

						</tr>`);
				});

			}

		});

	});

	$('#btninsertuser').on('click',function(){
		$.ajax({
			type:'POST',
			url:'/puser/loadroluser',
			success:function(response){
				$('#selectroluser').empty();
				$('#selectroluser').append(`<option value="">--roles--</option>`);
				$.each(response.datos,function(index,valores){
					$('#selectroluser').append(`<option value=${valores.idrol}>${valores.nombre}</option>`);
				});
				$('#insertarusuario').modal('show');
			}
		});

		
	});

	$('#datosuser').on('keyup',function(){
		const datos=$(this).val();
		$.ajax({
			type:'POST',
			url:'/puser/searchpersonwithoutuser',
			data:{'datos':datos},
			success:function(response){
				console.log(response);
				var resultadosHtml='';
				$.each(response.datos,function(index,valores){
					resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${valores.dni}>${valores.datos} </p>`;
					
				});
				$('#iddivdatosusers').show();
				$('#iddivdatosusers').html(resultadosHtml);
			}
		});

	});

	$('#iddivdatosusers').on('click','p',function(){
		const datos=$(this).text();
		const dni=$(this).data('id');
		$('#datosuser').attr('data-dni',dni);
		$('#datosuser').val(datos);
		$('#iddivdatosusers').hide();

	});


	$('#oficinau').on('keyup',function(){
		const datos=$(this).val();
		$.ajax({
			type:'POST',
			url:'/puser/searchoficinauser',
			data:{'datos':datos},
			success:function(response){
				console.log(response);
				var resultadosHtml='';
				$.each(response.datos,function(index,valores){
					resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${valores.codigo}>${valores.nombre} </p>`;					
				});
				$('#iddivoficinausers').show();
				$('#iddivoficinausers').html(resultadosHtml);
			}
		});

	});

	$('#iddivoficinausers').on('click','p',function(){
		const datos=$(this).text();
		const codigo=$(this).data('id');
		$('#oficinau').attr('data-codigoO',codigo);
		$('#oficinau').val(datos);
		$('#iddivoficinausers').hide();

	});


});