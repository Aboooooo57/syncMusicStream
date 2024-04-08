var websocket = new WebSocket("ws://localhost:8002");
var audioPlayer = document.getElementById("audioPlayer");
var locallyInitiatedPlay = false;
const deviceId = getCookie("usr");
var callerId = deviceId;
var seeking = false;

websocket.onmessage = function(event) {
    var message = event.data;
    var parts = message.split(":");
    var recDeviceId = parts[1];
    if (message.startsWith("playing:") || message.startsWith("paused:")) {

        if (parseInt(recDeviceId) !== parseInt(deviceId)) {
            callerId = recDeviceId;
            locallyInitiatedPlay = true;
            if (message.startsWith("playing:")) {
                console.log("Received play command from device:", recDeviceId);
                audioPlayer.play();
            } else {
                console.log("Received paused command from device:", recDeviceId);
                audioPlayer.pause();
            }
        }
    }
    else if (message.startsWith("position_update:")){
        var deviceId = parts[1];
        var position = parseFloat(parts[2]);
        console.log("Received position update from device:", deviceId, "Position:", position);
        if (!isNaN(position)) {
            console.log("i'm here")
            audioPlayer.currentTime = position;
        }
    }
};

audioPlayer.addEventListener("play", function() {
    if (websocket.readyState === WebSocket.OPEN) {
        if (!locallyInitiatedPlay || parseInt(callerId) !== parseInt(deviceId)) {
            if (!seeking && deviceId) {
                var message = "PLAY:" + deviceId;
                websocket.send(message);
                console.log("Sent play command to all devices.");
            }
        }
        locallyInitiatedPlay = false;
    }
});

audioPlayer.addEventListener("pause", function() {
    if (websocket.readyState === WebSocket.OPEN) {
        if (!locallyInitiatedPlay || parseInt(callerId) !== parseInt(deviceId)) {
            if (!seeking && deviceId) {
                var message = "PAUSE:" + deviceId;
                websocket.send(message);
                console.log("Sent pause command to all devices.");
            }
        }
        locallyInitiatedPlay = false;
    }
});

audioPlayer.addEventListener("seeking", function() {
    seeking = true;
});

audioPlayer.addEventListener("seeked", function() {
    seeking = false;
});





function syncMusic(){
    var position = audioPlayer.currentTime;
    var message = "UPDATE_POSITION:" + deviceId + ":" + position;
    websocket.send(message);
    console.log("Updated position for device:", deviceId, "Position:", position);

}
function registerDevice() {
    if (websocket.readyState === WebSocket.OPEN) {
        if (deviceId) {
            var message = "REGISTER_DEVICE:" + deviceId;
            websocket.send(message);
            console.log("Registered device:", deviceId);
        } else {
            console.log("Please provide a device ID.");
        }
    } else {
        console.log("WebSocket connection not open.");
    }
}

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=');
        if (cookieName === name) {
            return decodeURIComponent(cookieValue);
        }
    }
    return null;
}

document.addEventListener("DOMContentLoaded", function(event) {

    websocket.onopen = function(event) {
        console.log("WebSocket connection established.");
        registerDevice();
    };



websocket.onerror = function(event) {
    console.error("WebSocket error:", event);
};

websocket.onclose = function(event) {
    console.log("WebSocket connection closed.");
};

});
