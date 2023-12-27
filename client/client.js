// function isOpen(ws) { return ws.readyState === ws.OPEN }

// 웹소켓 생성
const socket = new WebSocket("ws://0.0.0.0:8080/ws");
var chat_id;

function sendMessage() {
  var messageInput = document.getElementById("message-input");
  var message = messageInput.value;

  if (message.trim() !== "") {
    socket.send(message);

    // 메시지를 보낸 후에 입력 필드를 비웁니다.
    messageInput.value = "";
  }
}

input = document.getElementById("message-input");
input.addEventListener("keyup", function (event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    sendMessage();
  }
});

// 데이터를 수신 받았을 때
socket.addEventListener("message", (event) => {
  data = JSON.parse(event.data);
  console.log("Message from server", data);
  if (data.message_type == "info") {
    var idInfo = document.getElementById("id-info");
    chat_id = data.content;
    idInfo.innerText = "아이디: " + chat_id;
  } else if (data.content.sender == chat_id) {
    var chatMessages = document.getElementById("chat-messages");
    var newMessage = document.createElement("div");
    newMessage.setAttribute("id", "my-message");
    newMessage.innerText = "나: " + data.content.message;
    chatMessages.appendChild(newMessage);
  } else {
    var chatMessages = document.getElementById("chat-messages");
    var newMessage = document.createElement("div");
    newMessage.setAttribute("id", "not-my-message");
    newMessage.innerText = data.content.sender + ": " + data.content.message;
    chatMessages.appendChild(newMessage);
  }
});
