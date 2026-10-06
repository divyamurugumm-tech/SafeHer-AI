// ===============================
// SAFEHER AI - SAFETY TIMER
// ===============================

let timerInterval = null;
let remainingSeconds = 0;


// ===============================
// SELECT TIME
// ===============================

function selectTime(minutes, button) {

    document.querySelectorAll(".time-option").forEach(function (btn) {
        btn.classList.remove("selected");
    });

    if (button) {
        button.classList.add("selected");
    }

    const input = document.getElementById("duration");

    if (input) {
        input.value = minutes;
    }
}


// ===============================
// START TIMER
// ===============================

function startTimer() {

    const durationInput = document.getElementById("duration");

    if (!durationInput) {
        return;
    }

    const minutes = parseInt(durationInput.value);

    if (!minutes || minutes <= 0) {
        alert("Please select a timer duration.");
        return;
    }

    remainingSeconds = minutes * 60;

    updateDisplay();

    clearInterval(timerInterval);

    timerInterval = setInterval(function () {

        remainingSeconds--;

        updateDisplay();

        if (remainingSeconds <= 0) {
            clearInterval(timerInterval);
            timerExpired();
        }

    }, 1000);
}


// ===============================
// UPDATE DISPLAY
// ===============================

function updateDisplay() {

    const display = document.getElementById("timerDisplay");

    if (!display) {
        return;
    }

    const minutes = Math.floor(remainingSeconds / 60);
    const seconds = remainingSeconds % 60;

    display.textContent =
        String(minutes).padStart(2, "0") +
        ":" +
        String(seconds).padStart(2, "0");
}


// ===============================
// TIMER EXPIRED
// ===============================

async function timerExpired() {

    alert(
        "⚠️ Safety Timer expired.\n\n" +
        "Your safety alert will now be processed."
    );

    try {

        await fetch("/safety_timer_expired", {
            method: "POST"
        });

        window.location.reload();

    } catch (error) {

        console.error("Timer expiry error:", error);

        alert("Unable to process the safety alert.");
    }
}


// ===============================
// CHECK IN
// ===============================

async function checkIn() {

    clearInterval(timerInterval);

    try {

        const response = await fetch("/check_in", {
            method: "POST"
        });

        if (response.ok) {

            alert(
                "✅ Check-in successful!\n\n" +
                "You are marked safe."
            );

            window.location.reload();

        } else {

            alert("Unable to complete check-in.");

        }

    } catch (error) {

        console.error("Check-in error:", error);

        alert("Something went wrong.");
    }
}


// ===============================
// CANCEL TIMER
// ===============================

async function cancelTimer() {

    clearInterval(timerInterval);

    try {

        const response = await fetch("/cancel_safety_timer", {
            method: "POST"
        });

        if (response.ok) {

            alert("🛑 Safety Timer cancelled.");

            window.location.reload();

        } else {

            alert("Unable to cancel the timer.");

        }

    } catch (error) {

        console.error("Cancel timer error:", error);

        alert("Something went wrong.");
    }
}


// ===============================
// PAGE LOAD
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Safety Timer loaded.");

});