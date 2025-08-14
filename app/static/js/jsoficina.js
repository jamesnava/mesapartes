$(document).ready(function(){
	$('#addbuttonoficina').on('click',function(){
		$('#addoficina').modal('show');
		$.ajax({
			url:'/office/gencodigo',
			type:'POST',
			success:function(response){
				$('#oficodi').val(response);
			}
		});

	});


	$('#responsableoficina').on('keyup',function(){
	valor=$('#responsableoficina').val();	
	$.ajax({
		url:'/office/searchkey',
		type:'POST',
		data:{valor:valor},
		success:function(response){
			var resultadosHtml='';
			$.each(response.responsable,function(index,valores){
				resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${valores.dni}>${valores.datos} </p>`;
			});
			$('#iddivdestinoresponsable').show()
			$('#iddivdestinoresponsable').html(resultadosHtml);
		}
		});
	});

	$('#iddivdestinoresponsable').on('click','p',function(){
	const id=$(this).data('id');
	const nombre=$(this).text();
	$('#responsableoficina').val("")
	$('#responsableoficina').val(nombre)
	$('#responsableoficina').attr('data-dni',id)
	$('#iddivdestinoresponsable').hide()	
	});


	$('#responsableoficinaup').on('keyup',function(){
	valor=$(this).val();	
	$.ajax({
		url:'/office/searchkey',
		type:'POST',
		data:{valor:valor},
		success:function(response){
			var resultadosHtml='';
			$.each(response.responsable,function(index,valores){
				resultadosHtml+=`<p style="cursor: pointer;background:#666a70" data-id=${valores.dni}>${valores.datos} </p>`;
			});
			$('#iddivresponsableup').show()
			$('#iddivresponsableup').html(resultadosHtml);
		}
		});
	});

	$('#iddivresponsableup').on('click','p',function(){
		const id=$(this).data('id');
		const nombre=$(this).text();
		$('#responsableoficinaup').val("")
		$('#responsableoficinaup').val(nombre)
		$('#responsableoficinaup').attr('data-dni',id)
		$(this).hide()	
	});


	$('#grabaroficina').on('click',function(){
		const codigo=$('#oficodi').val();
		const nombre=$('#nameoficina').val();
		const padre=$('#codigopadre').val();
		const responsable=$('#codigopadre').data('dni')	;
		datos={'codigo':codigo,'nombre':nombre,'padre':padre,'responsable':responsable}
		$.ajax({
			url:'/office/insertoficina',
			type:'POST',
			data:datos,
			success:function(response){
				if(response===1){
					mostrarMensaje('success','Exitoso!')
					setTimeout(function(){location.reload(true);},1000);
				}
			}
		});

	});

	$('.upbtnoficina').on('click',function(){
		const codigo=$(this).data('codigo');
		$('#codigoup').val(codigo);
		$('#updateoficina').modal('show');
		$.ajax({
			type:'POST',
			url:'/office/fillupdateoffice',
			data:{'codigo':codigo},
			success:function(response){
				$('#responsableoficinaup').val(response.datospersonales);
				$('#responsableoficinaup').attr('dni',response.dni);				
				$('#upcodigopadre').val(response.codigopadre);

			}
		});
	});

	$('#upgrabaroficina').on('click',function(){
		const codigo=$('#codigoup').val();
		const nombre=$('#upnameoficina').val();
		const padre=$('#upcodigopadre').val();
		const responsable=$('#responsableoficinaup').data('dni');

		datos={'codigo':codigo,'nombre':nombre,'responsable':responsable,'codigopadre':padre}
		console.log(datos);

		$.ajax({
			url:'/office/updateoficina',
			type:'POST',
			data:datos,
			success:function(response){
				if (response==1){
					mostrarMensaje('success','Actualizacion correcta!!');
					setTimeout(function(){location.reload(true);},1000)
				}
				else{
					mostrarMensaje('error','No pudo actualizar');
					//setTimeout(function(){location.reload(true);},1000);
				}
			}

		});

	});

$('.deleteinput').on('click',function(){
	$(this).val("");	
});


});