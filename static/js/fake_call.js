// ===============================
// SAFEHER AI - FAKE CALL
// ===============================

let callTimer = null;
let callSeconds = 0;

function startFakeCall() {

    const screen = document.getElementById("callScreen");

    if (!screen) {
        return;
    }

    screen.style.display = "block";

    callSeconds = 0;

    clearInterval(callTimer);

    callTimer = setInterval(function () {

        callSeconds++;

        const minutes = Math.floor(callSeconds / 60);
        const seconds = callSeconds % 60;

        const duration =
            document.getElementById("callDuration");

        if (duration) {
            duration.textContent =
                String(minutes).padStart(2, "0") +
                ":" +
                String(seconds).padStart(2, "0");
        }

    }, 1000);
}

function endFakeCall() {

    clearInterval(callTimer);

    const screen = document.getElementById("callScreen");

    if (screen) {
        screen.style.display = "none";
    }

    callSeconds = 0;
}