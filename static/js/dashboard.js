// ===============================
// SAFEHER AI - DASHBOARD JS
// ===============================

function showMessage(message) {
    alert(message);
}


// ===============================
// QUICK SOS
// ===============================

async function quickSOS() {

    const button = document.getElementById("quickSOSButton");

    if (button && button.disabled) {
        return;
    }

    if (!navigator.geolocation) {
        alert("❌ Your browser does not support GPS location.");
        return;
    }

    if (button) {
        button.disabled = true;
        button.innerHTML = "📍 GETTING LOCATION...";
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

                    alert("❌ Unable to send SOS alert.");

                }

            } catch (error) {

                console.error("Quick SOS Error:", error);

                alert(
                    "❌ Something went wrong while sending the SOS."
                );

            } finally {

                if (button) {
                    button.disabled = false;
                    button.innerHTML = "🚨 QUICK SOS";
                }
            }
        },

        function (error) {

            console.error("GPS Error:", error);

            let message = "⚠️ Unable to get your location.";

            if (error.code === 1) {
                message =
                    "⚠️ Location permission was denied.\n\n" +
                    "Please allow location access in your browser.";
            }

            if (error.code === 2) {
                message =
                    "⚠️ Your location could not be determined.";
            }

            if (error.code === 3) {
                message =
                    "⚠️ Location request timed out.\n\n" +
                    "Please try again.";
            }

            alert(message);

            if (button) {
                button.disabled = false;
                button.innerHTML = "🚨 QUICK SOS";
            }
        },

        {
            enableHighAccuracy: false,
            timeout: 10000,
            maximumAge: 60000
        }
    );
}


// ===============================
// PAGE LOAD
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    console.log("SafeHer AI Dashboard loaded.");

});