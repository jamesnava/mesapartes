$(document).ready(function(){
$('#cargarPlantilla').on('click',function(){
	
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


$('#TFlujo').on('change',function(){
	tflujo=$('#TFlujo').val();
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

});

$('#Emisor').on('keydown',function(event){
	if(event.key=='Enter'){ 
	dni=$('#Emisor').val()
	$.ajax({
		type:'POST',
		url:'/documents/filldata',
		data:{dni:dni},
		success:function(response){
			console.log(response.datos.length);
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

	//recorremos la tabla
	$('#tableoficinas tbody tr').each(function(index,fila){

		const codigo=$(fila).find('td:eq(0)').text().trim();
		const oficina=$(fila).find('td:eq(1)').text().trim();		
		 
    formData.append('codigos[]', codigo);
    formData.append('oficinas[]', oficina);
  	

	});



	$.ajax({
		url:'/documents/insertdocument',
		type:'POST',
		data:formData,
		contentType:false,
		processData:false,
		success: function(response){

		}
	});

});


});