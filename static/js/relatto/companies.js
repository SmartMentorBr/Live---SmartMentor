document.addEventListener('DOMContentLoaded',function(){
	deletaEmpresa();
});


function deletaEmpresa(){
	var deleteempresas = document.getElementsByName('delete-empresa');
	for (var i = 0; i < deleteempresas.length; i++){
		deleteempresas[i].addEventListener('click',function(){
			if(confirm('Deseja deletar essa empresa?')){
				excluibloco(this);
			}
		});
	};
	// Exclui o bloco da empresa na pagina companies
	function excluibloco(e){
		var blocoempresa = document.querySelectorAll('[data-empresa]');
		for (var i = 0; i < blocoempresa.length; i++) {
			console.log(blocoempresa[i].getAttribute('data-empresa'));
		};
	};

}
