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
				var resultadosHtml='';
				$.each(response.datos,function(index,valores){
					resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${valores.dni}>${valores.datos} </p>`;
					
				});
				$('#iddivdatosusers').empty();
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
				var resultadosHtml='';
				$.each(response.datos,function(index,valores){
					resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${valores.codigo}>${valores.nombre} </p>`;					
				});
				$('#iddivoficinausers').empty();
				$('#iddivoficinausers').show();
				$('#iddivoficinausers').html(resultadosHtml);
			}
		});

	});

	$('#iddivoficinausers').on('click','p',function(){
		const datos=$(this).text();
		const codigo=$(this).data('id');
		$('#oficinau').attr('data-codigoo',codigo);
		$('#oficinau').val(datos);
		$('#iddivoficinausers').hide();

	});

	$('#insertuser').on('click',function(){
		const formulario=document.getElementById('formulariousuario');
		if (!formulario.checkValidity()){
			formulario.classList.add('was-validated');
			return;
		}
		formData=new FormData(document.getElementById('formulariousuario'));
		const dni=$('#datosuser').data('dni');
		const oficina=$('#oficinau').data('codigoo');		
		formData.append('dni',dni);
		formData.append('oficina',oficina)
		$.ajax({
			url:'/puser/insertsaveuser',
			type:'POST',
			data:formData,
			contentType:false,
			processData:false,
			success:function(response){
				if(response==-1){
					mostrarMensaje("error","existe un usuario vinculado con este dni");
					setTimeout(function(){location.reload(true);},1000);
				}
				else{
					if(response==1){
						mostrarMensaje("success","Registro Exitoso");
						setTimeout(function(){location.reload(true);},1000);
					}
					else{
						mostrarMensaje("error","no pudo insertarse");
						setTimeout(function(){location.reload(true);},1000);
					}
				}
			}
		});

	});

	$('.btnchangestate').on('click',function(){
		const dni=$(this).data('dni');
		$.ajax({
			url:'/puser/changestate',
			type:'POST',
			data:{'dni':dni} ,
			success:function(response){
				if (response==1){
					mostrarMensaje("success","Actualizacion correcta")
					setTimeout(function(){location.reload(true);},1000);
				}
				else{
					mostrarMensaje("error","error!")
					setTimeout(function(){location.reload(true);},1000);
				}

			}
		});

	});


$('.btnchangeoficina').on('click',function(){
	$('#modalchangeoficina').modal('show');		
	$('#ofhidden').val($(this).data('dni'));
});

$('#oficinachange').on('keyup',function(){
	let valor=$(this).val();
	$.ajax({
		type:'POST',
		url:'/puser/searchoficinauser',
		data:{'datos':valor},
		success:function(response){
			var resultadosHtml='';
			$.each(response.datos,function(index,valores){
				resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${valores.codigo}>${valores.nombre} </p>`
			});

			$("#iddivoficinachangeusers").empty();
			$("#iddivoficinachangeusers").show();
			$("#iddivoficinachangeusers").append(resultadosHtml);

		}

	});

});

$('#iddivoficinachangeusers').on('click','p',function(){
		const datos=$(this).text();
		const codigo=$(this).data('id');
		$('#oficinachange').attr('data-codigooficinai',codigo);
		$('#oficinachange').val(datos);
		$('#iddivoficinachangeusers').hide();

	});

$('#grabarupdateoficinauser').on('click',function(){
	let dni=$('#ofhidden').val();
	let oficina=$('#oficinachange').data('codigooficinai');
	$.ajax({
		type:'POST',
		url:'/puser/updateoficinauser',
		data:{'dni':dni,'oficina':oficina},
		success:function(response){
			if(Number(response)){
				mostrarMensaje('success','Actualización exitosa');
				setTimeout(function(){location.reload(true)},100);
			}
			else{mostrarMensaje('error','No pudo actualizarse');
				setTimeout(function(){location.reload(true)},100);}
		}
	});

});

$('.btnchangeclave').on('click',function(){
	let dni=$(this).data('dni');
	$('#userhiddenclave').val(dni);
	$('#modalchangepassword').modal('show');
});

$('#grabarupdatepassworduser').on('click',function(){
	$.ajax({
		type:'POST',
		url:'/puser/updatepassworduser',
		data:{'dni':$('#userhiddenclave').val(),'clave':$('#passwordchange').val()},
		success:function(response){
			if (Number(response)){
				mostrarMensaje('success','Se actualizó correctamente!!')
				setTimeout(function(){location.reload(true);},1000);
			}
			else{
				mostrarMensaje('error','No pudo actualizar!!')
				setTimeout(function(){location.reload(true);},1000);
			}

		}
	});
});

$('.btnaddperfiluser').on('click',function(){
	$('#addperfiluser').modal('show');
	$('#userhiddenperfil').val($(this).data('dni'));
	$.ajax({
		type:'POST',
		url:'/puser/cargarperfil',
		success:function(response){
			htmselect=$('#selectperfil');
			htmselect.empty();
			$.each(response.datos,function(index,valores){
				htmselect.append(`<option value=${valores.id}>${valores.nombre}</option>`);
			});

		}
	});
});

$('#grabarupdateperfiluser').on('click',function(){
	let dni=$('#userhiddenperfil').val();
	let rol=$('#selectperfil').val();
	$.ajax({
		type:'POST',
		url:'/puser/grabacambioperfil',
		data:{'dni':dni,'rol':rol},
		success:function(response){
			if (response==1){
				mostrarMensaje('success','Exitoso!');
				setTimeout(function(){location.reload(true);},1000);
			}
			else{
				mostrarMensaje('error','no pudo actualizar!');
				setTimeout(function(){location.reload(true);},1000);

			}
		}
	});


});

$('#linkchangeclave').on('click',function(){
	$('#Mcambioclave').modal('show');
});

$('#confirmarclave').on('keyup',function(){
	const pass=$('#clave').val();
	const confirmar=$(this).val();	
	const mensaje=$('#mensaje-error');

	if(pass!==confirmar){mensaje.text('La contraseña no coinciden');}
	else{
		mensaje.text("");}
});

$('#grabarcambioclave').on('click',function(){
	const claveactual=$('#claveactual').val();
	const clave=$('#clave').val();
	const claveconfirmar=$('#confirmarclave').val();
	if (clave==claveconfirmar){
		$.ajax({
		type:'POST',
		url:'/main/changepassword',
		data:{'clave':clave,'claveactual':claveactual},
		success:function(response){
			if (response==1){
				mostrarMensaje('success','Se actualizó correctamente!');
				setTimeout(function(){location.reload(true);},1000);
			}
			else if(response==-1){
				mostrarMensaje('error','La clave actual no corresponde, intente nuevamente');
				setTimeout(function(){location.reload(true);},1000);
			}
			else if (response==0){
				mostrarMensaje('error','Ocurrio un problema al actualizar!!');
				setTimeout(function(){location.reload(true);},1000);
			}
		}
	});
	}
	else{
		mostrarMensaje('error','La nueva clave no coincide!!');
		setTimeout(function(){location.reload(true);},1000);
	}
	
});

});