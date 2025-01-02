let websocket;
let reconnectInterval = 1000;
const maxReconnectInterval = 16000;
const deviceId = getCookie("usr");
let locallyInitiatedPlay = false;
let callerId = deviceId;
let seeking = false;
let playState = {
    isPlaying: false,
    currentPosition: 0,
    waitingForPermission: false,
    lastCommand: null
};

const controlButtons = document.createElement('div');
controlButtons.innerHTML = `
    <button id="remotePlayButton" style="display:none;">Start Music</button>
    <button id="remotePauseButton" style="display:none;">Pause Music</button>
`;
document.body.appendChild(controlButtons);

const playButton = document.getElementById('remotePlayButton');
const pauseButton = document.getElementById('remotePauseButton');
const audioPlayer = document.getElementById("audioPlayer");

function initWebSocket() {
    websocket = new WebSocket("ws://localhost:8002");

    websocket.onopen = function (event) {
        console.log("WebSocket connection established.");
        registerDevice();
        reconnectInterval = 1000;
    };

    websocket.onmessage = function (event) {
        const message = event.data;
        console.log("Received message:", message);
        const parts = message.split(":");
        const recDeviceId = parts[1] + ":" + parts[2];

        if (message.startsWith("playing:") || message.startsWith("paused:")) {
            if (parseInt(recDeviceId) !== parseInt(deviceId)) {
                callerId = recDeviceId;
                locallyInitiatedPlay = true;

                if (message.startsWith("playing:")) {
                    console.log("Received play command from device:", recDeviceId);

                    playState.waitingForPermission = true;
                    playState.lastCommand = 'play';
                    playState.currentPosition = audioPlayer.currentTime;

                    if (playState.waitingForPermission) {

                        if (playState.currentPosition) {
                            audioPlayer.currentTime = playState.currentPosition;
                        }
                        audioPlayer.play();
                        playState.waitingForPermission = false;
                    }


                    playButton.style.display = 'block';
                    playButton.textContent = 'Music Started From Second Device. You Can Start It if not Played';

                    pauseButton.style.display = 'none';
                }

                if (message.startsWith("paused:")) {
                    console.log("Received pause command from device:", recDeviceId);


                    playState.waitingForPermission = true;
                    playState.lastCommand = 'pause';


                    pauseButton.style.display = 'block';
                    pauseButton.textContent = 'Music Paused From Second Device. You Can Pause It if You want';


                    playButton.style.display = 'none';
                }
            }
        } else if (message.startsWith("position_update:")) {
            const position = parseFloat(parts[3]);
            console.log("Received position update from device:", recDeviceId, "Position:", position);

            if (!isNaN(position)) {
                playState.currentPosition = position;
                if (playState.waitingForPermission) {
                    audioPlayer.currentTime = position;
                    audioPlayer.play();
                    playState.waitingForPermission = false;
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

playButton.addEventListener('click', function() {

    this.style.display = 'none';
    playState.waitingForPermission = false;
    if (playState.currentPosition) {
        audioPlayer.currentTime = playState.currentPosition;
    }
    audioPlayer.play().catch((err) => {
    console.log("Playback blocked by browser:", err);
    });


    const message = "PLAY:" + deviceId;
    websocket.send(message);
    console.log("Sent play confirmation to all devices.");
});


pauseButton.addEventListener('click', function() {
    this.style.display = 'none';
    playState.waitingForPermission = false;
    audioPlayer.pause();
    const message = "PAUSE:" + deviceId;
    websocket.send(message);
    console.log("Sent pause confirmation to all devices.");
});


audioPlayer.addEventListener("play", function () {
    if (websocket.readyState === WebSocket.OPEN && !playState.waitingForPermission) {
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
    if (websocket.readyState === WebSocket.OPEN && !playState.waitingForPermission) {
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

audioPlayer.addEventListener("timeupdate", function() {
    setInterval(() => {
    if (!playState.waitingForPermission && audioPlayer.paused === false) {
        syncMusic();
        }
    }, 5000);
});

audioPlayer.addEventListener("seeking", function () {
    seeking = true;
});

audioPlayer.addEventListener("seeked", function () {
    seeking = false;

    if (websocket.readyState === WebSocket.OPEN && !playState.waitingForPermission) {
        syncMusic();
    }
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

const style = document.createElement('style');
style.textContent = `
#remotePlayButton, #remotePauseButton {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    z-index: 1000;
}
#remotePlayButton:hover, #remotePauseButton:hover {
    background-color: #45a049;
}
#remotePauseButton {
    background-color: #f44336;
}
#remotePauseButton:hover {
    background-color: #da190b;
}
`;
document.head.appendChild(style);