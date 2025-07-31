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
			}
		});
	});

});