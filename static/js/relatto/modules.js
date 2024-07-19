// Crianção da função nativa TRIM()
String.prototype.trim = function () {
	return this.replace(/^\s+|\s+$/g,"");
}

function regexLink(e){
	var expression = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
	var regex      = new RegExp(expression);
	var link       = e.value;

	 if (link.match(regex)){
	   return true
	 }else{
	   return false;
	 }
}

function pegaGET(name){
	var url   = window.location.search.replace("?", "");
	var itens = url.split("&");

	for(n in itens)
	{
		if( itens[n].match(name) )
		{
			return decodeURIComponent(itens[n].replace(name+"=", ""));
		}
	}
	return null;
}

function identificaLinks(){
	textos = document.querySelectorAll("[data-texto]")
	for (var i = 0; i < textos.length; i++) {
		textos[i].innerHTML = chat_string_create_urls(textos[i].innerHTML);
	};
	
}

function chat_string_create_urls(input){
    return input
    .replace(/<br>/gim, '\n')
    .replace(/(ftp|http|https|file):\/\/[\S]+(\b|$)/gim,'<a href="$&" class="my_link" target="_blank">$&</a>')
    .replace(/([^\/])(www[\S]+(\b|$))/gim,'$1<a href="http://$2" class="my_link" target="_blank">$2</a>')
    .replace(/\n/gim, '<br>');
}
