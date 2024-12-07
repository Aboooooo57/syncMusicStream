let websocket;
let reconnectInterval = 1000; // Initial reconnect interval in milliseconds
const maxReconnectInterval = 16000; // Maximum reconnect interval in milliseconds
const deviceId = getCookie("usr");
let locallyInitiatedPlay = false;
let callerId = deviceId;
let seeking = false;

function initWebSocket() {
    websocket = new WebSocket("ws://localhost:8002");

    websocket.onopen = function (event) {
        console.log("WebSocket connection established.");
        registerDevice();
        reconnectInterval = 1000; // Reset the reconnect interval on successful connection
    };

    websocket.onmessage = function (event) {
        const message = event.data;
        console.log(message)
        const parts = message.split(":");
        const recDeviceId = parts[1] + ":" + parts[2];
        console.log(recDeviceId)
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
        } else if (message.startsWith("position_update:")) {
            const position = parseFloat(parts[3]);
            console.log("Received position update from device:", recDeviceId, "Position:", position);
            if (!isNaN(position)) {
                audioPlayer.currentTime = position;
                if (audioPlayer.paused) {
                    audioPlayer.play(); // Ensure the audio player starts playing if it's paused
                }
            }
        }
    };

    websocket.onerror = function (event) {
        console.error("WebSocket error:", event);
    };

    websocket.onclose = function (event) {
        console.log("WebSocket connection closed. Attempting to reconnect...");
        setTimeout(() => {
            reconnectInterval = Math.min(reconnectInterval * 2, maxReconnectInterval);
            initWebSocket();
        }, reconnectInterval);
    };
}

const audioPlayer = document.getElementById("audioPlayer");

audioPlayer.addEventListener("play", function () {
    if (websocket.readyState === WebSocket.OPEN) {
        if (!locallyInitiatedPlay || parseInt(callerId) !== parseInt(deviceId)) {
            if (!seeking && deviceId) {
                const message = "PLAY:" + deviceId;
                websocket.send(message);
                console.log("Sent play command to all devices.");
            }
        }
        locallyInitiatedPlay = false;
    }
});

audioPlayer.addEventListener("pause", function () {
    if (websocket.readyState === WebSocket.OPEN) {
        if (!locallyInitiatedPlay || parseInt(callerId) !== parseInt(deviceId)) {
            if (!seeking && deviceId) {
                const message = "PAUSE:" + deviceId;
                websocket.send(message);
                console.log("Sent pause command to all devices.");
            }
        }
        locallyInitiatedPlay = false;
    }
});

audioPlayer.addEventListener("seeking", function () {
    seeking = true;
});

audioPlayer.addEventListener("seeked", function () {
    seeking = false;
});

function syncMusic() {
    const position = audioPlayer.currentTime;
    const message = "UPDATE_POSITION:" + deviceId + ":" + position;
    websocket.send(message);
    console.log("Updated position for device:", deviceId, "Position:", position);
}

function registerDevice() {
    if (websocket.readyState === WebSocket.OPEN) {
        if (deviceId) {
            const message = "REGISTER_DEVICE:" + deviceId;
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

document.addEventListener("DOMContentLoaded", function (event) {
    initWebSocket();
});
