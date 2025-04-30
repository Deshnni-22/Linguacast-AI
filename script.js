document.getElementById("generateBtn").addEventListener("click", async () => {
    const inputText = document.getElementById("inputText").value.trim();
    const language = document.getElementById("languageSelector").value;

    if (!inputText) {
        alert("Please enter an English sentence.");
        return;
    }

    const response = await fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ sentence: inputText, language: language })
    });

    const data = await response.json();

    document.getElementById("englishText").textContent = data.english;
    document.getElementById("translatedText").textContent = data.translation;
    document.getElementById("audioPlayer").src = data.audio_path;
    document.getElementById("downloadLink").href = data.audio_path;

    document.getElementById("outputSection").style.display = "block";
});

// Normalize string (for comparing spoken vs. expected)
function normalize(str) {
    return str
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "") // strip accents
        .replace(/[.,!?]/g, "")
        .trim();
}

// Pronunciation check
function checkPronunciation() {
    const expected = normalize(document.getElementById("translatedText").innerText);
    const feedback = document.getElementById("feedbackText");

    if (!expected) {
        feedback.innerText = "⚠️ Please generate the podcast first.";
        return;
    }

    const language = document.getElementById("languageSelector").value;
    const langMap = {
        fr: 'fr-FR',
        de: 'de-DE',
        hi: 'hi-IN',
        ta: 'ta-IN'
    };

    const recognitionLang = langMap[language] || 'fr-FR';

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = recognitionLang;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    feedback.innerText = "🎙️ Listening... Speak the translated sentence";

    recognition.start();

    recognition.onresult = function (event) {
        const spoken = normalize(event.results[0][0].transcript);
        console.log("Spoken:", spoken);
        console.log("Expected:", expected);

        if (spoken === expected) {
            feedback.innerText = "✅ Excellent! Your pronunciation is accurate!";
        } else if (expected.includes(spoken) || spoken.includes(expected)) {
            feedback.innerText = "🤏 Almost there! Minor differences detected.";
        } else {
            feedback.innerText = `❌ Try again. We heard: "${spoken}"`;
        }
    };

    recognition.onerror = function (event) {
        feedback.innerText = "❌ Speech recognition error: " + event.error;
    };
}

  
