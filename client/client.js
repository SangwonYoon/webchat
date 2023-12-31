// function isOpen(ws) { return ws.readyState === ws.OPEN }

// 웹소켓 생성
const socket = new WebSocket("ws://0.0.0.0:8080/ws");
var chat_id;

function getNickname() {
  let nickname = prompt("Please enter your nickname:", "Anonymous");
  if (nickname == null || nickname == "") {
    nickname = getNickname();
  }
  return nickname;
}

function sendMessage() {
  var messageInput = document.getElementById("message-input");
  var message = messageInput.value;

  if (message.trim() !== "") {
    socket.send(message);

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

socket.addEventListener("open", (event) => {
  nickname = getNickname();
  console.log("nickname: " + nickname);
  socket.send(nickname);
});

// 데이터를 수신 받았을 때
socket.addEventListener("message", (event) => {
  data = JSON.parse(event.data);
  console.log("Message from server", data);
  if (data.message_type == "info") {
    chat_id = data.content;
  } else if (data.message_type == "enterance") {
    var chatMessages = document.getElementById("chat-messages");
    var newMessage = document.createElement("div");
    newMessage.setAttribute("class", "enterance");
    newMessage.innerText = data.content + "님이 입장하셨습니다.";
    chatMessages.appendChild(newMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } else if (data.content.sender == chat_id) {
    var chatMessages = document.getElementById("chat-messages");
    var newMessage = document.createElement("div");
    newMessage.setAttribute("class", "my-message");
    newMessage.innerText = data.content.message;
    chatMessages.appendChild(newMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } else {
    var chatMessages = document.getElementById("chat-messages");
    var newMessage = document.createElement("div");
    newMessage.setAttribute("class", "not-my-message");
    newMessage.innerText =
      data.content.sender_nickname + ": " + data.content.message;
    chatMessages.appendChild(newMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});

socket.addEventListener("close", (event) => {
  console.log("socket closed!");
});
