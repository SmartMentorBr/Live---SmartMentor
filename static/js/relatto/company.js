document.addEventListener("DOMContentLoaded",function(){
	mainCompany();	
});

function mainCompany(){
	recarregaCategoria();
	if(pegaGET("edit") != null){
		carregaCategoriasTopico()	
	}
	
	notificationAll()
	var membros = document.getElementsByName("delete-membro");
	company = pegaGET('company');
	for (var i = 0; i < membros.length; i++) {
		membros[i].addEventListener("click",function(){
			excluir(this);
		})
	};

	var btnPost = document.getElementsByName('edit_topic');
	for (var i = 0; i < btnPost.length; i++) {
		btnPost[i].addEventListener('click',function(){
			checarTopico();
		})
	};
	document.getElementById("addCategoria").addEventListener("click",function(){
		addNewCategory();
	})
}

function recarregaCategoria(){
	var company = pegaGET('company');
	var data_url = 'company='+company;
	$.ajax({
		url: url.get_category,
		data: data_url,
		success: function(data) {
			CarregaCategorias(data);
		},
		error: function(data){
			console.log(data);
		}
	});
}

function addNewCategory(){
	var nova_categoria = document.getElementById("newCategoria").value;
	var company = pegaGET('company');
	var data_url = 'company='+company+'&category='+nova_categoria;
	if(nova_categoria.trim() != ""){
		$.ajax({
			type: 'POST',
			url: url.add_category_new,
			data: data_url,
			success: function(data) {
				if(data){
					recarregaCategoria();
					document.getElementById("newCategoria").value = "";
				}
			},
			error: function(data){
				console.log(data);
			}
		});
	}else{
		alert(text.alert.categoryEmpty);
	}
}

jQuery("#user_invite").keyup(function(){
	ajax('get_user', ['user_invite'], 'suggestions')
});

jQuery("#user_invite").change(Sugestoes);


jQuery("#newCategoria").keyup(function(){
	ajax('get_categories',['AddCategoria'],'suggestions_cat')
});

// jQuery("#suggestions_cat").onclick(function(){
	
// })


function checarTopico(){
	var formulario 	   = document.getElementById('user_member');
	// var texto 	   	   = document.getElementById('topic_tp_content');
	// var titulo     	   = document.getElementById('topic_title');
	var categorias     = document.getElementsByName('categoria');
	var temCategoria   = false;

	for (var i = 0; i < categorias.length; i++) {
		if(categorias[i].checked){
			temCategoria = true;
		}
	};

	if (temCategoria){
		formulario.submit();
	}else{
		alert(text.alert.selectCategory);
	};
	
}

	


function Sugestoes(){
	var sugestoes = document.getElementsByName("sugestao");

	for (var i = 0; i < sugestoes.length; i++) {
		sugestoes[i].addEventListener("click",function(){
			adiciona(this);
		});
	}
}

function excluir(e){	
	if (confirm("Deseja Realmente excluir esse membro?")){
		$.ajax({
			type: 'POST',
			url: url.delete_user_of_company,
			data: "id="+e.id+"&company="+company
		}).done(function (){
			location.reload();
		});
	};
}

function adiciona(e){
	company = pegaGET('company');
	$.ajax({
		type: 'POST',
		url: url.add_user_to_company,
		data: "id="+e.id+"&company="+company+"&role=member"
	}).done(function (){
		location.reload();
	});
}

function editReply(id){
	$.ajax({
		type: 'POST',
		url: url.reply_to_edit,
		data: "id="+id,
		success: function(data){
			var json 			= data;
			var d 				= document.getElementById('reply_rp_content_'+json.topic);
			d.value 			= json.rp_content;
			var btn 			= document.getElementById('reply_save_btn');
			btn.value 			= 'Save';
			var reply_save 		= document.getElementById('edit_reply_'+json.topic);
			reply_save.value 	= 'True';
			var reply_id_form   = document.getElementById('reply_to_edit_id_'+json.topic);
			reply_id_form.value = id;

			//Pega o comentário que foi selecionado e adiciona a classe de edição					

			comments = document.querySelectorAll("[data-comment]")
			for (var i = 0; i < comments.length; i++) {
				comments[i].classList.remove("comentario-editando");
			};

			var comment = document.querySelector("[data-comment='"+id+"']");					
			comment.classList.add("comentario-editando");

		},
		error: function(data){
			console.log(data);
		}
	});
};


function CarregaCategorias(json_categorias){

	jsonData = json_categorias;

	var categorias = "";
		for (var i = 0; i < jsonData.categorias.length; i++) {
			categorias += "<li>"
			+"<input type='checkbox' name='categoria' value='"
			+jsonData.categorias[i].nome+"'>"
			+jsonData.categorias[i].nome+"</li>"

		};
	categorias += "";

	var lista = document.getElementById("lista-c").getElementsByTagName("ul");
	lista[0].innerHTML = categorias;
}


function carregaCategoriasTopico(){

	var idTopic = pegaGET("edit");

	$.ajax({
		url: url.get_topic_category,
		data: "topic="+idTopic,
		success: function(data) {
			console.log("Json",data);

			data =  $.parseJSON(data);
			data = eval(data);
			var ConteudoSelect = document.getElementById('TagsSelect')
			
			var listaCategoria = document.querySelectorAll("#lista-c ul li input")
			for( iListaCategoria in listaCategoria){
				for (var iData = 0; iData < data.length; iData++) {
						if(listaCategoria[iListaCategoria].value == data[iData])
						{
							listaCategoria[iListaCategoria].checked = true;
							ConteudoSelect.innerHTML += "<span>"+listaCategoria[iListaCategoria].value +"</span> "
						}
				};
				
			}
			
			
		},
		error: function(data){
			console.log(data);
		}
	});
}


function ConfirmaCategorias(){
	var ConteudoSelect = document.getElementById('TagsSelect');
	var SelectMultiplo = document.getElementsByName('categoria');
	

	for (var i = 0; i < SelectMultiplo.length; i++) {
		if (SelectMultiplo[i].checked){
			if(ConteudoSelect.innerHTML.indexOf(SelectMultiplo[i].value) <= 0){
					ConteudoSelect.innerHTML += "<span>"+SelectMultiplo[i].value +"</span> ";
			}
		}
		else if(ConteudoSelect.innerHTML.indexOf(SelectMultiplo[i].value) > 0 ){
				var palavra = "<span>"+SelectMultiplo[i].value +"</span>";
				ConteudoSelect.innerHTML =  ConteudoSelect.innerHTML.replace(palavra,"");
		};
	};
};


function mostraCategorias(){

	var DivDasCategorias = document.getElementById('CategoriaList');


	if(document.getElementById('lista-c').style.display == 'none')
	{
		console.log('true');
		document.getElementById('lista-c').style.display = 'block';
	}
	else{
		console.log('false');
		document.getElementById('lista-c').style.display = 'none';
	}
}


