
    // Mobile nav
    const navToggle = document.getElementById('navToggle');
    const navLinks  = document.getElementById('navLinks');
    navToggle?.addEventListener('click', () => {
      document.body.classList.toggle('nav-open');
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', (e) => {
        const id = a.getAttribute('href');
        if (!id || id === '#') return;
        const el = document.querySelector(id);
        if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        document.body.classList.remove('nav-open');
      });
    });

    // Footer year
    document.getElementById('year').textContent = new Date().getFullYear();

    // Farmer Pass logic
    const form = document.getElementById('passForm');
    const printBtn = document.getElementById('printPass');
    const clearBtn = document.getElementById('clearPass');

    const pName   = document.getElementById('pName');
    const pVillage= document.getElementById('pVillage');
    const pCrop   = document.getElementById('pCrop');
    const pSeason = document.getElementById('pSeason');
    const pArea   = document.getElementById('pArea');
    const pValid  = document.getElementById('pValid');
    const pId     = document.getElementById('pId');
    const qr      = document.getElementById('qr');

    const nameIn   = document.getElementById('name');
    const villageIn= document.getElementById('village');
    const cropIn   = document.getElementById('crop');
    const seasonIn = document.getElementById('season');
    const areaIn   = document.getElementById('area');
    const validIn  = document.getElementById('valid');
    const idIn     = document.getElementById('id');
    const qrIn     = document.getElementById('qrtext');

    function randomId(){ return 'AGP-' + Math.floor(100000 + Math.random()*899999); }

    function updatePreview(){
      pName.textContent    = 'Farmer: ' + (nameIn.value || '—');
      pVillage.textContent = 'Village: ' + (villageIn.value || '—');
      pCrop.textContent    = cropIn.value || '—';
      pSeason.textContent  = seasonIn.value || '—';
      pArea.textContent    = areaIn.value || '—';
      pValid.textContent   = validIn.value || '—';
      pId.textContent      = (idIn.value || randomId());
      // Minimal QR placeholder (for demo). Replace with real QR lib if needed.
      qr.textContent = 'QR';
      qr.title = qrIn.value || '';
    }

    [nameIn, villageIn, cropIn, seasonIn, areaIn, validIn, idIn, qrIn].forEach(el => {
      el.addEventListener('input', updatePreview);
    });

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!form.checkValidity()) return;
      updatePreview();
      localStorage.setItem('agripass', JSON.stringify({
        name: nameIn.value,
        village: villageIn.value,
        crop: cropIn.value,
        season: seasonIn.value,
        area: areaIn.value,
        valid: validIn.value,
        id: idIn.value,
        qr: qrIn.value
      }));
      alert('Pass generated! You can now print it.');
    });

    printBtn.addEventListener('click', () => window.print());
    clearBtn.addEventListener('click', () => {
      form.reset(); updatePreview(); localStorage.removeItem('agripass');
    });

    // Restore saved pass
    (function(){
      const data = localStorage.getItem('agripass');
      if (!data) return;
      try {
        const d = JSON.parse(data);
        nameIn.value = d.name || '';
        villageIn.value = d.village || '';
        cropIn.value = d.crop || '';
        seasonIn.value = d.season || '';
        areaIn.value = d.area || '';
        validIn.value = d.valid || '';
        idIn.value = d.id || '';
        qrIn.value = d.qr || '';
        updatePreview();
      } catch(_){}
    })();

    // Contact form (demo only)
    const cform = document.getElementById('contactForm');
    const cresult = document.getElementById('contactResult');
    cform.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!cform.checkValidity()) return;
      cresult.textContent = 'Thanks! We will reply within 24 hours.';
    });
    // </script>
    
  // ---- Voice + Speak Feature for Marketplace ----
  const voiceBtn = document.getElementById("voiceBtn");
  const voiceStatus = document.getElementById("voiceStatus");

  // Function to speak text
  function speak(text) {
    speechSynthesis.cancel(); // ✅ prevent overlapping
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-IN"; // Indian English accent
    utter.rate = 1; // normal speed
    utter.pitch = 1;
    speechSynthesis.speak(utter);
  }

  // Function to find product by name
  function findProduct(name) {
    const products = document.querySelectorAll("#market .card.product");
    for (let product of products) {
      const pnameOriginal = product.querySelector("h3")?.textContent.trim();
      const pname = pnameOriginal?.toLowerCase();
      const price = product.querySelector(".price")?.textContent;
      const muted = product.querySelector(".muted")?.textContent;
      if (pname && pname.includes(name.toLowerCase())) {
        return { name: pnameOriginal, price, muted }; // ✅ return proper name
      }
    }
    return null;
  }

  // Setup Speech Recognition (browser support check)
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = "en-IN"; // Indian English
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    voiceBtn.addEventListener("click", () => {
      recognition.start();
      voiceStatus.textContent = "🎙️ Listening... Say a vegetable name.";
    });

    recognition.addEventListener("result", (e) => {
      const transcript = e.results[0][0].transcript;
      voiceStatus.textContent = `✅ You said: "${transcript}"`;

      const product = findProduct(transcript);
      if (product) {
        const msg = `${product.name}, ${product.muted}. Price is ${product.price}`;
        speak(msg);
      } else {
        speak("Sorry, I could not find that vegetable in the marketplace.");
      }
    });

    recognition.addEventListener("end", () => {
      voiceStatus.textContent += " | Tap again to speak.";
    });
  } else {
    voiceBtn.disabled = true;
    voiceStatus.textContent = "❌ Voice recognition not supported in this browser.";
  }

  // Button-based "Speak Price"
  document.querySelectorAll(".speak-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const product = btn.closest(".product");
      const name = product.querySelector("h3").textContent;
      const price = product.querySelector(".price").textContent;
      speak(`${name} price is ${price}`);
    });
  });


