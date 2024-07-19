function notificationAll(){
	
	subscribeNotificationChange()
}

function WebSocketTest(){
  if ("WebSocket" in window)
  {
     alert("WebSocket is supported by your Browser!");
     // Let us open a web socket

     var ws = new WebSocket("ws://localhost:8888/socket");

     ws.onopen = function()
     {
        // Web Socket is connected, send data using send()
        ws.send("Message to send");
        alert("Message is sent...");
     };
     ws.onmessage = function (evt) 
     { 
        var received_msg = evt.data;
        alert("Message is received...");
     };
     ws.onclose = function()
     { 
        // websocket is closed.
        alert("Connection is closed..."); 
     };
  }
  else
  {
     // The browser doesn't support WebSocket
     alert("WebSocket NOT supported by your Browser!");
  }
}


function subscribeNotificationChange(){
	var icoNot = document.getElementsByName("icoNotification");
	for (var i = 0; i < icoNot.length; i++) {
		icoNot[i].addEventListener("click",function(){
			if(this.getAttribute("data-state") == "on"){
				console.log("Off")
				this.src = images.notificationDesable
				this.setAttribute("data-state",'off')
			}else{
				console.log("On");
				this.src = images.notification
				this.setAttribute("data-state",'on')
			}
		})
	};
}
