const serverEndpoint = "ws://0.0.0.0:8080/ws";
const socket = new WebSocket(serverEndpoint);
var chat_id;

function getNickname() {
  const promptMessage = "Please enter your nickname:";
  const defaultNickname = "Anonymous";
  let nickname = prompt(promptMessage, defaultNickname);
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

function printMessage(className, text) {
  var chatMessages = document.getElementById("chat-messages");
  var newMessage = document.createElement("div");
  newMessage.setAttribute("class", className);
  newMessage.innerText = text;
  chatMessages.appendChild(newMessage);
  chatMessages.scrollTop = chatMessages.scrollHeight;
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
    printMessage("enterance", data.content + "님이 입장하셨습니다.");
  } else if (data.message_type == "exit") {
    printMessage("exit", data.content + "님이 퇴장하셨습니다.");
  } else if (data.content.sender == chat_id) {
    printMessage("my-message", data.content.message);
  } else {
    printMessage(
      "not-my-message",
      data.content.sender_nickname + ": " + data.content.message
    );
  }
});

socket.addEventListener("close", (event) => {
  console.log("socket closed!");
});
