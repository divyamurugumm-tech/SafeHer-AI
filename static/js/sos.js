// ===============================
// SAFEHER AI - SOS
// ===============================

let countdown = 5;
let countdownInterval = null;


// ===============================
// START SOS
// ===============================

function startSOS() {

    const countdownDisplay =
        document.getElementById("countdown");

    if (!countdownDisplay) {
        return;
    }

    countdown = 5;
    countdownDisplay.textContent = countdown;

    clearInterval(countdownInterval);

    countdownInterval = setInterval(function () {

        countdown--;

        countdownDisplay.textContent = countdown;

        if (countdown <= 0) {

            clearInterval(countdownInterval);

            sendSOS();
        }

    }, 1000);
}


// ===============================
// CANCEL SOS
// ===============================

function cancelSOS() {

    clearInterval(countdownInterval);

    alert("SOS cancelled.");
}


// ===============================
// SEND SOS
// ===============================

function sendSOS() {

    if (!navigator.geolocation) {

        alert("❌ GPS is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(

        async function (position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            try {

                const formData = new FormData();

                formData.append("latitude", latitude);
                formData.append("longitude", longitude);

                const response = await fetch("/send_sos", {
                    method: "POST",
                    body: formData
                });

                if (response.ok) {

                    alert(
                        "🚨 SOS ALERT SENT!\n\n" +
                        "Your trusted contacts have been notified."
                    );

                    window.location.href = "/dashboard";

                } else {

                    alert("❌ Failed to send SOS alert.");
                }

            } catch (error) {

                console.error("SOS Error:", error);

                alert(
                    "❌ Something went wrong while sending SOS."
                );
            }
        },

        function (error) {

            console.error("GPS Error:", error);

            alert(
                "⚠️ Unable to get your location.\n\n" +
                "Please allow location access and try again."
            );
        },

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 30000
        }
    );
}