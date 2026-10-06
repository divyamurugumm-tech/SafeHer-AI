// ==========================================
// SAFEHER AI - VOICE SOS
// ==========================================

let recognition = null;
let listening = false;


// ==========================================
// START VOICE SOS
// ==========================================

function startVoiceSOS() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert(
            "❌ Voice recognition is not supported.\n\n" +
            "Please use Google Chrome."
        );
        return;
    }

    // Prevent multiple recognition sessions
    if (listening) {
        return;
    }

    recognition = new SpeechRecognition();

    recognition.lang = "en-IN";

    // Keep listening until we receive a result
    recognition.continuous = true;

    // Get partial speech results too
    recognition.interimResults = true;

    recognition.maxAlternatives = 3;


    // ======================================
    // RECOGNITION STARTED
    // ======================================

    recognition.onstart = function () {

        listening = true;

        console.log("🎙️ Voice recognition started");

        const status =
            document.getElementById("voiceStatus");

        if (status) {
            status.textContent =
                "🎙️ Listening... Say SOS, Help, or Emergency";
        }
    };


    // ======================================
    // SPEECH RESULT
    // ======================================

    recognition.onresult = function (event) {

        let finalText = "";
        let interimText = "";

        for (
            let i = event.resultIndex;
            i < event.results.length;
            i++
        ) {

            const transcript =
                event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalText += transcript + " ";
            } else {
                interimText += transcript + " ";
            }
        }


        // Show what browser is currently hearing
        console.log(
            "FINAL:",
            finalText,
            "INTERIM:",
            interimText
        );

        const heardText =
            (finalText || interimText)
                .toLowerCase()
                .trim();


        const status =
            document.getElementById("voiceStatus");

        if (status && heardText) {
            status.textContent =
                "👂 Heard: " + heardText;
        }


        // ==================================
        // EMERGENCY KEYWORD DETECTION
        // ==================================

        const emergencyDetected =
            heardText.includes("sos") ||
            heardText.includes("help") ||
            heardText.includes("emergency") ||
            heardText.includes("save me") ||
            heardText.includes("i need help");


        if (emergencyDetected) {

            console.log(
                "🚨 EMERGENCY COMMAND DETECTED:",
                heardText
            );

            // Stop recognition
            try {
                recognition.stop();
            } catch (error) {
                console.log(error);
            }

            listening = false;


            // Show confirmation
            alert(
                "🚨 Emergency voice command detected!\n\n" +
                "SafeHer is opening the emergency center."
            );


            // Open existing SOS page
            window.location.href = "/sos";
        }
    };


    // ======================================
    // ERROR
    // ======================================

    recognition.onerror = function (event) {

        console.error(
            "🎙️ Voice recognition error:",
            event.error
        );

        listening = false;

        const status =
            document.getElementById("voiceStatus");

        if (status) {

            if (event.error === "not-allowed") {

                status.textContent =
                    "⚠️ Microphone permission denied.";

            } else if (event.error === "no-speech") {

                status.textContent =
                    "🔇 No speech detected. Try again.";

            } else {

                status.textContent =
                    "⚠️ Voice recognition error: " +
                    event.error;
            }
        }
    };


    // ======================================
    // RECOGNITION ENDED
    // ======================================

    recognition.onend = function () {

        console.log("🎙️ Voice recognition ended");

        listening = false;

        const status =
            document.getElementById("voiceStatus");

        if (status) {

            status.textContent =
                "Tap the button and say SOS, Help, or Emergency.";
        }
    };


    // ======================================
    // START
    // ======================================

    try {

        recognition.start();

    } catch (error) {

        console.error(
            "Could not start voice recognition:",
            error
        );

        listening = false;

        alert(
            "⚠️ Could not start microphone recognition."
        );
    }
}


// ==========================================
// STOP VOICE SOS
// ==========================================

function stopVoiceSOS() {

    if (recognition) {

        try {
            recognition.stop();
        } catch (error) {
            console.log(error);
        }
    }

    listening = false;

    const status =
        document.getElementById("voiceStatus");

    if (status) {
        status.textContent =
            "Voice SOS stopped.";
    }
}