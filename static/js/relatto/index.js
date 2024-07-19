document.addEventListener("DOMContentLoaded",function(){
	$(window).scroll(function(){
		if ($(this).scrollTop() > 100) {
			$('#scrollToTop').fadeIn();
		} else {
			$('#scrollToTop').fadeOut();
		}
	});

	if(document.getElementsByName("submeterEmpresa")[0] != null){
		document.getElementsByName("submeterEmpresa")[0].addEventListener("click",function(){
			validaCriacaoEmpresa();
		});
	}
	document.getElementById("scrollToTop").addEventListener("click",scrollTop);

	function scrollTop(){
		var body = $("html, body");
		body.animate({scrollTop:0}, '500', 'swing', function() {
		});
	}


	if (document.getElementById('categoriaClick') != null) {

		document.getElementById('categoriaClick').addEventListener("click",function(){
			mostraCategorias();
		},false);

		

		document.getElementById("btnConfirmCat").addEventListener("click",function(){

			ConfirmaCategorias();
			mostraCategorias();
		},false);

	};
	if (pegaGET('tag') != null) {
		categoria = pegaGET('tag').replace("+"," ");

		document.getElementById("categorialAtual").innerHTML= categoria;
	}
	else{

	}



	var termoBusca = document.getElementsByName("parametroBusca");
	var parametro = pegaGET("q");
	for (var i = 0; i < termoBusca.length; i++) {
		termoBusca[i].innerHTML = parametro;
	};

	if (document.getElementById('TagsSelect') != null) {
	
		var ConteudoSelect = document.getElementById('TagsSelect');
		var SelectMultiplo = document.getElementsByName('categoria')
				//SelectMultiplo.multiple = true;

				for (var i = 0; i < SelectMultiplo.length; i++) {
					SelectMultiplo[i].addEventListener("click",function(){
						if( ConteudoSelect.innerHTML.indexOf(this.value) > 0 ){
							var palavra = "<span>"+this.value +"</span>";
							ConteudoSelect.innerHTML =  ConteudoSelect.innerHTML.replace(palavra,"");
						}
						else
						{
							ConteudoSelect.innerHTML += "<span>"+this.value +"</span> ";
						}
					},false);
				};
	};

			identificaLinks()
			var btnCancelaInvestimento = document.getElementsByName("cancel-investiment");
			for (var i = 0; i < btnCancelaInvestimento.length; i++) {
				btnCancelaInvestimento[i].addEventListener("click",function(){
						Ajax(this); // pega no switch e joga para o caminho certo
					});
			};
			var textareas = document.getElementsByTagName('textarea');	
			for (var i = 0; i < textareas.length; i++) {
				textareas[i].addEventListener("keyup",function(){
				
				if(this.value.length >= 1500){
					this.value = this.value.substr(0,1500);
				}
			});
		};
			
},false);


function validaCriacaoEmpresa(){
	var form ;
	if(document.getElementById("no_table_site") != null){
		var site = document.getElementById("no_table_site");
		var nome = document.getElementById("no_table_name");
		form = 0
	}else{
	var site = document.getElementById("company_site");
	var nome = document.getElementById("company_name");	
		form=1
	}
	
	if(nome.value != ""){
		if(site.value != ""? regexLink(site) : true){
			document.forms[form].submit()
		}
		else{
			alert(text.alert.link);	
		}
	}
	else{
		alert(text.alert.companyName);
	}
	



}




function Ajax(e){

	switch(e.name){
		case "cancel-investiment":
		caminho = "decline_request_to_invest";
		vars = e.id;

	}


	$.ajax({
		type: 'POST',
		url: caminho,
		data: 'rid='+vars,
		success: function(data){
			if(e.name == "cancel-investiment"){
				deletaInvestimento(vars);
			};
		},
		error: function(data){
			console.log(data);
		}});

}

function deletaInvestimento(id){


	console.log("Id",id);

	var empresas = document.getElementById("investimentos-aprovacao").querySelectorAll("[data-company]");
	console.log("empresas",empresas);
	for (var i = 0; i < empresas.length; i++) {
		console.log("empresas[i].getAttribute('data-company')",empresas[i].getAttribute("data-company") );
		console.log("Id",id);

		if(empresas[i].getAttribute("data-company") == id){

			document.getElementById("investimentos-aprovacao").removeChild(empresas[i]);
		}
	};
}




// Ajax do editar
var botoesEditar = document.querySelectorAll('[data-post]');

for (var i = 0; i < botoesEditar.length; i++) {
    botoesEditar[i].addEventListener('click',function(){
        ajaxEditResposta(this);
    });
};

function ajaxEditResposta(e){

var idRespota = e.getAttribute('data-post');

$.ajax({
    type: 'POST',
    url: url.reply_edit+'/'+idRespota,
    success: function(data) {
        var json = data;
        document.getElementById('contentReply').value = json.rp_content;
        document.getElementById('idPostReply').value = idRespota;
    },
    error: function(data){
      console.log(data);
    }
  });

}