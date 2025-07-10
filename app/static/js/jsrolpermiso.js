$(document).ready(function(){
	$('#rolguardar').on('click',function(event){
		nombre=$('#txtMdenominacion').val()
		$.ajax({
			type:'POST',
			url:'/rol/insertmodulo',
			data:{denominacion:nombre,tabla:'modulo'},
			success:function(response){
				if(response[0]==1){
					location.reload();
				}
				else{
					mostrarMensaje('error','no se pudo insertar!')
				}
			}
		});
	});
});