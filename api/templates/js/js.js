// var eventSource = new EventSource("http://185.230.162.51:8002/sse"); // Establish SSE connection
var audioPlayer = document.getElementById("audioPlayer");
// var locallyInitiatedPlay = false;
// const deviceId = getCookie("usr");
// var callerId = deviceId;
// var seeking = false;
//
var currentUrl = window.location.href;
var parsedUrl = new URL(currentUrl);
var token = parsedUrl.pathname.split('/').pop();


// Function to handle SSE events
function handleEvent(event) {
    const data = JSON.parse(event.data);
    console.log(data);
    if (data.event === "pause") {
        audioPlayer.pause();
    } else if (data.event === "play") {
        audioPlayer.play();
    }
}

// Function to establish SSE connection
function connectSSE() {
    const eventSource = new EventSource("/sse");

    // Add event listener to handle incoming events
    eventSource.addEventListener("message", handleEvent);

    // Add event listener to handle connection errors
    eventSource.addEventListener("error", function (event) {
        console.error("SSE connection error:", event);
    });
}

// Call the connectSSE function when the page loads
window.onload = connectSSE;


// eventSource.onmessage = function(event) {
//     var message = event.data;
//     var parts = message.split(":");
//     var recDeviceId = parts[1];
//     if (message.startsWith("playing:") || message.startsWith("paused:")) {
//         if (parseInt(recDeviceId) !== parseInt(deviceId)) {
//             callerId = recDeviceId;
//             locallyInitiatedPlay = true;
//             if (message.startsWith("playing:")) {
//                 console.log("Received play command from device:", recDeviceId);
//                 audioPlayer.play();
//             } else {
//                 console.log("Received paused command from device:", recDeviceId);
//                 audioPlayer.pause();
//             }
//         }
//     } else if (message.startsWith("position_update:")) {
//         var deviceId = parts[1];
//         var position = parseFloat(parts[2]);
//         console.log("Received position update from device:", deviceId, "Position:", position);
//         if (!isNaN(position)) {
//             console.log("i'm here")
//             audioPlayer.currentTime = position;
//         }
//     }
// };
//
audioPlayer.addEventListener("play", function() {

    fetch('/music/play/'+ token)
        .then(response => {
            console.log(response);
            if (response.status === 200) {
                console.log("Play command sent successfully.");
            } else {
                console.error("Failed to send play command:", response.status);
            }
        })
        .catch(error => {
            console.error("Error sending play command:", error);
        });
    // if (!locallyInitiatedPlay || parseInt(callerId) !== parseInt(deviceId)) {
    //     if (!seeking && deviceId) {
    //         var message = "PLAY:" + deviceId;
    //         eventSource.send(message);
    //         console.log("Sent play command to all devices.");
    //     }
    // }
    // locallyInitiatedPlay = false;
});
//
audioPlayer.addEventListener("pause", function() {
    fetch('/music/pause/'+token)
    .then(response => {
        console.log(response);

        if (response.status === 200) {
            console.log("pause command sent successfully.");
        } else {
            console.error("Failed to send pause command:", response.status);
        }
    })
    .catch(error => {
        console.error("Error sending pause command:", error);
    });

    // if (!locallyInitiatedPlay || parseInt(callerId) !== parseInt(deviceId)) {
    //     if (!seeking && deviceId) {
    //         var message = "PAUSE:" + deviceId;
    //         eventSource.send(message);
    //         console.log("Sent pause command to all devices.");
    //     }
    // }
    // locallyInitiatedPlay = false;
});
//
// audioPlayer.addEventListener("seeking", function() {
//     seeking = true;
// });
//
// audioPlayer.addEventListener("seeked", function() {
//     seeking = false;
// });
//
// function syncMusic() {
//     var position = audioPlayer.currentTime;
//     var message = "UPDATE_POSITION:" + deviceId + ":" + position;
//     eventSource.send(message);
//     console.log("Updated position for device:", deviceId, "Position:", position);
// }
//
// function registerDevice() {
//     if (deviceId) {
//         var message = "REGISTER_DEVICE:" + deviceId;
//         eventSource.send(message);
//         console.log("Registered device:", deviceId);
//     } else {
//         console.log("Please provide a device ID.");
//     }
// }
//
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
//
// document.addEventListener("DOMContentLoaded", function(event) {
//     console.log("DOMContentLoaded event fired.");
//     registerDevice();
// });
