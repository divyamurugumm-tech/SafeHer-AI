// ===============================
// SAFEHER AI - LOCATION
// ===============================

function getCurrentLocation() {

    if (!navigator.geolocation) {
        alert("❌ Your browser does not support GPS.");
        return;
    }

    navigator.geolocation.getCurrentPosition(

        function (position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            console.log("Latitude:", latitude);
            console.log("Longitude:", longitude);

            sendLocation(latitude, longitude);
        },

        function (error) {

            console.error("Location Error:", error);

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


// ===============================
// SEND LOCATION TO SERVER
// ===============================

async function sendLocation(latitude, longitude) {

    try {

        const response = await fetch("/update_location", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude
            })
        });

        const data = await response.json();

        if (data.success) {

            console.log("✅ Location updated successfully.");

        } else {

            console.error(
                "Location update failed:",
                data.message
            );
        }

    } catch (error) {

        console.error(
            "Location server error:",
            error
        );
    }
}


// ===============================
// AUTOMATIC LOCATION UPDATE
// ===============================

function startLocationTracking() {

    if (!navigator.geolocation) {
        return;
    }

    navigator.geolocation.watchPosition(

        function (position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            sendLocation(latitude, longitude);
        },

        function (error) {

            console.error(
                "Location tracking error:",
                error
            );
        },

        {
            enableHighAccuracy: true,
            maximumAge: 30000,
            timeout: 10000
        }
    );
}