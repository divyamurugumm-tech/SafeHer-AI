// ===============================
// SAFEHER AI - NEARBY HELP
// ===============================

function getNearbyLocation() {

    if (!navigator.geolocation) {
        alert("GPS is not supported by your browser.");
        return;
    }

    const status = document.getElementById("locationStatus");

    if (status) {
        status.textContent = "Getting your location...";
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            const mapUrl =
                "https://www.google.com/maps/search/?api=1&query=" +
                latitude + "," + longitude;

            if (status) {
                status.textContent = "Location found.";
            }

            const mapButton =
                document.getElementById("openMapButton");

            if (mapButton) {
                mapButton.href = mapUrl;
                mapButton.style.display = "inline-flex";
            }

        },
        function () {

            if (status) {
                status.textContent =
                    "Unable to get your location. Please allow GPS permission.";
            }

        },
        {
            enableHighAccuracy: false,
            timeout: 10000,
            maximumAge: 60000
        }
    );
}