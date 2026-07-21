document.addEventListener('DOMContentLoaded', function () {

  // ─── State ───
  let wavesurfer = null;
  let wsRegions = null;
  let activeRegion = null;
  let clickCount = 0;
  let audioDuration = 0;
  let audioFileName = 'ref_audio.mp3';
  let audioBuffer = null;        // decoded AudioBuffer for Web Audio processing
  let audioContext = null;
  let currentSource = null;       // currently playing BufferSourceNode
  let isCleanMode = false;        // A/B toggle: false=raw, true=cleaned
  let isPlaying = false;

  // ─── DOM refs ───
  const fileInfo = document.getElementById('file-info');
  const fileInput = document.getElementById('file-input');
  const waveformContainer = document.getElementById('waveform-container');
  const timeIn = document.getElementById('time-in');
  const timeOut = document.getElementById('time-out');
  const timeDur = document.getElementById('time-dur');
  const playSegment = document.getElementById('play-segment');
  const playFull = document.getElementById('play-full');
  const stopPlay = document.getElementById('stop-play');
  const resetRegion = document.getElementById('reset-region');
  const optVocalIsolation = document.getElementById('opt-vocal-isolation');
  const optDenoise = document.getElementById('opt-denoise');
  const optSpeed = document.getElementById('opt-speed');
  const speedValue = document.getElementById('speed-value');
  const configPreview = document.getElementById('config-preview');
  const downloadConfig = document.getElementById('download-config');
  const copyConfig = document.getElementById('copy-config');
  const copyFeedback = document.getElementById('copy-feedback');
  const modeRaw = document.getElementById('mode-raw');
  const modeClean = document.getElementById('mode-clean');
  const previewProcessed = document.getElementById('preview-processed');

  // ─── Init WaveSurfer ───
  function initWaveSurfer(url) {
    if (wavesurfer) {
      wavesurfer.destroy();
      wavesurfer = null;
      activeRegion = null;
      clickCount = 0;
    }

    wavesurfer = WaveSurfer.create({
      container: waveformContainer,
      waveColor: '#6b7280',
      progressColor: '#f59e0b',
      cursorColor: '#f59e0b',
      cursorWidth: 2,
      barWidth: 2,
      barRadius: 1,
      responsive: true,
      height: 100,
      url: url,
    });

    wsRegions = wavesurfer.registerPlugin(
      WaveSurfer.Regions.create()
    );

    wavesurfer.on('ready', () => {
      audioDuration = wavesurfer.getDuration();
      fileInfo.innerHTML = `
        <p>✅ <strong>${audioFileName}</strong> · ${audioDuration.toFixed(1)}s</p>
        <p class="text-gray-400">Clique sur la waveform pour poser IN puis OUT</p>
      `;

      // Also decode the audio for Web Audio API processing
      decodeAudioForProcessing(url);
      updateConfig();
    });

    wavesurfer.on('interaction', (newTime) => {
      clickCount++;
      if (clickCount === 1) {
        wsRegions.clearRegions();
        activeRegion = null;
        const start = newTime;
        const end = Math.min(newTime + 13, audioDuration);
        activeRegion = wsRegions.addRegion({
          start: start,
          end: end,
          color: 'rgba(245, 158, 11, 0.15)',
          drag: true,
          resize: true,
        });
        updateTimeLabels();
        updateConfig();
      } else {
        if (activeRegion) {
          const currentStart = activeRegion.start;
          if (newTime > currentStart) {
            activeRegion.setOptions({ end: Math.min(newTime, audioDuration) });
          } else {
            activeRegion.setOptions({ start: newTime, end: currentStart });
          }
          updateTimeLabels();
          updateConfig();
        }
        clickCount = 0;
      }
    });

    wsRegions.on('region-updated', (region) => {
      activeRegion = region;
      updateTimeLabels();
      updateConfig();
    });

    wsRegions.on('region-clicked', (region, e) => {
      e.stopPropagation();
      activeRegion = region;
      region.play();
    });

    wavesurfer.on('finish', () => {
      wavesurfer.seekTo(0);
      isPlaying = false;
    });
  }

  // ─── Decode audio for Web Audio API ───
  async function decodeAudioForProcessing(url) {
    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      console.log('[WEB AUDIO] Audio décodé:', audioBuffer.duration.toFixed(1) + 's', audioBuffer.sampleRate + 'Hz');
    } catch (e) {
      console.warn('[WEB AUDIO] Décodage échoué:', e);
    }
  }

  // ─── Play with Web Audio API (speed + filters) ───
  function playProcessed(startSec, endSec, applyFilters, speed) {
    // Stop any current playback
    stopWebAudio();
    stopWaveSurfer();

    if (!audioBuffer || !audioContext) {
      // Fallback: just play wavesurfer
      if (wavesurfer) {
        wavesurfer.seekTo(startSec / audioDuration);
        wavesurfer.setPlaybackRate(speed, true);
        wavesurfer.play();
      }
      return;
    }

    const ctx = audioContext;
    if (ctx.state === 'suspended') ctx.resume();

    const source = ctx.createBufferSource();
    source.buffer = audioBuffer;
    source.playbackRate.value = speed;

    // Chain: source → [filters] → gain → destination
    let lastNode = source;

    if (applyFilters) {
      // 1. High-pass filter (remove low rumble, bass, background hum)
      const highpass = ctx.createBiquadFilter();
      highpass.type = 'highpass';
      highpass.frequency.value = 80;
      highpass.Q.value = 1;
      lastNode.connect(highpass);
      lastNode = highpass;

      // 2. Vocal isolation approximation: band-pass boost on vocal frequencies
      if (optVocalIsolation.checked) {
        // Peaking filter to boost vocals (1-4kHz)
        const vocalBoost = ctx.createBiquadFilter();
        vocalBoost.type = 'peaking';
        vocalBoost.frequency.value = 2500;
        vocalBoost.Q.value = 0.7;
        vocalBoost.gain.value = 6; // +6dB on vocals
        lastNode.connect(vocalBoost);
        lastNode = vocalBoost;

        // Notch to cut music frequencies (low mids where music sits)
        const notchLow = ctx.createBiquadFilter();
        notchLow.type = 'notch';
        notchLow.frequency.value = 200;
        notchLow.Q.value = 1.5;
        lastNode.connect(notchLow);
        lastNode = notchLow;

        // High-pass more aggressively to remove music bass
        const aggressiveHP = ctx.createBiquadFilter();
        aggressiveHP.type = 'highpass';
        aggressiveHP.frequency.value = 150;
        aggressiveHP.Q.value = 1;
        lastNode.connect(aggressiveHP);
        lastNode = aggressiveHP;
      }

      // 3. Noise gate (simple: use a compressor as expander)
      if (optDenoise.checked) {
        const compressor = ctx.createDynamicsCompressor();
        compressor.threshold.value = -40;
        compressor.knee.value = 10;
        compressor.ratio.value = 20;
        compressor.attack.value = 0.003;
        compressor.release.value = 0.1;
        lastNode.connect(compressor);
        lastNode = compressor;

        // High-shelf to brighten vocals (cut dullness from noise)
        const highShelf = ctx.createBiquadFilter();
        highShelf.type = 'highshelf';
        highShelf.frequency.value = 3000;
        highShelf.gain.value = 3;
        lastNode.connect(highShelf);
        lastNode = highShelf;
      }
    }

    // Gain
    const gain = ctx.createGain();
    gain.gain.value = 1.0;
    lastNode.connect(gain);
    gain.connect(ctx.destination);

    // Calculate offset and duration
    const offset = startSec;
    const duration = (endSec - startSec) / speed; // adjusted for speed

    source.start(0, offset, (endSec - startSec));
    currentSource = source;
    isPlaying = true;

    // Auto-stop at end
    source.onended = () => {
      isPlaying = false;
      currentSource = null;
    };

    // Also move wavesurfer cursor for visual feedback
    if (wavesurfer) {
      wavesurfer.seekTo(startSec / audioDuration);
    }
  }

  function stopWebAudio() {
    if (currentSource) {
      try { currentSource.stop(); } catch (e) {}
      currentSource = null;
    }
    isPlaying = false;
  }

  function stopWaveSurfer() {
    if (wavesurfer) {
      wavesurfer.pause();
    }
  }

  // ─── Time labels ───
  function updateTimeLabels() {
    if (!activeRegion) {
      timeIn.textContent = '--';
      timeOut.textContent = '--';
      timeDur.textContent = '--';
      return;
    }
    const s = activeRegion.start;
    const e = activeRegion.end;
    timeIn.textContent = s.toFixed(1) + 's';
    timeOut.textContent = e.toFixed(1) + 's';
    timeDur.textContent = (e - s).toFixed(1) + 's';
  }

  // ─── Config generation ───
  function updateConfig() {
    if (!activeRegion || !audioDuration) {
      configPreview.textContent = 'Sélectionne un segment d\'abord...';
      return;
    }
    const config = {
      source: audioFileName,
      segment: {
        start: parseFloat(activeRegion.start.toFixed(2)),
        end: parseFloat(activeRegion.end.toFixed(2))
      },
      vocal_isolation: optVocalIsolation.checked,
      denoise: optDenoise.checked,
      speed: parseFloat(optSpeed.value) || 1.0
    };
    configPreview.textContent = JSON.stringify(config, null, 2);
  }

  // ─── A/B mode toggle ───
  modeRaw.addEventListener('click', () => {
    isCleanMode = false;
    modeRaw.classList.add('ab-active');
    modeRaw.classList.remove('btn-secondary');
    modeClean.classList.remove('ab-active');
    modeClean.classList.add('btn-ghost');
  });

  modeClean.addEventListener('click', () => {
    isCleanMode = true;
    modeClean.classList.add('ab-active');
    modeClean.classList.remove('btn-ghost');
    modeRaw.classList.remove('ab-active');
    modeRaw.classList.add('btn-secondary');
  });

  // ─── Playback controls ───
  playSegment.addEventListener('click', () => {
    if (!activeRegion) {
      alert('Sélectionne d\'abord un segment (clic IN puis clic OUT)');
      return;
    }
    const speed = parseFloat(optSpeed.value) || 1.0;
    if (isCleanMode) {
      playProcessed(activeRegion.start, activeRegion.end, true, speed);
    } else {
      // Raw mode: use wavesurfer with speed
      stopWebAudio();
      wavesurfer.setPlaybackRate(speed, true);
      wavesurfer.seekTo(activeRegion.start / audioDuration);
      wavesurfer.play();

      // Stop at region end
      const checkTime = setInterval(() => {
        if (wavesurfer.getCurrentTime() >= activeRegion.end) {
          wavesurfer.pause();
          clearInterval(checkTime);
        }
      }, 50);
    }
  });

  playFull.addEventListener('click', () => {
    stopWebAudio();
    const speed = parseFloat(optSpeed.value) || 1.0;
    wavesurfer.setPlaybackRate(speed, true);
    wavesurfer.seekTo(0);
    wavesurfer.play();
  });

  stopPlay.addEventListener('click', () => {
    stopWebAudio();
    stopWaveSurfer();
  });

  resetRegion.addEventListener('click', () => {
    if (wsRegions) {
      wsRegions.clearRegions();
      activeRegion = null;
      clickCount = 0;
      updateTimeLabels();
      updateConfig();
    }
  });

  // ─── PREVIEW processed button ───
  previewProcessed.addEventListener('click', () => {
    if (!activeRegion) {
      alert('Sélectionne d\'abord un segment');
      return;
    }
    const speed = parseFloat(optSpeed.value) || 1.0;
    // Force clean mode for this preview
    playProcessed(activeRegion.start, activeRegion.end, true, speed);
    // Update A/B buttons
    isCleanMode = true;
    modeClean.classList.add('ab-active');
    modeClean.classList.remove('btn-ghost');
    modeRaw.classList.remove('ab-active');
    modeRaw.classList.add('btn-secondary');
  });

  // ─── Speed slider ───
  optSpeed.addEventListener('input', () => {
    const val = parseFloat(optSpeed.value);
    speedValue.textContent = val.toFixed(2) + 'x';
    // If currently playing raw via wavesurfer, update speed live
    if (wavesurfer && !isPlaying) {
      wavesurfer.setPlaybackRate(val, true);
    }
    updateConfig();
  });

  // ─── Toggle changes ───
  [optVocalIsolation, optDenoise].forEach(toggle => {
    toggle.addEventListener('change', updateConfig);
  });

  // ─── Download config ───
  downloadConfig.addEventListener('click', () => {
    if (!activeRegion) {
      alert('Sélectionne d\'abord un segment');
      return;
    }
    const blob = new Blob([configPreview.textContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'config.json';
    a.click();
    URL.revokeObjectURL(url);
  });

  // ─── Copy config ───
  copyConfig.addEventListener('click', () => {
    if (!activeRegion) {
      alert('Sélectionne d\'abord un segment');
      return;
    }
    navigator.clipboard.writeText(configPreview.textContent).then(() => {
      copyFeedback.classList.remove('hidden');
      setTimeout(() => copyFeedback.classList.add('hidden'), 2000);
    });
  });

  // ─── Manual file upload ───
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      const file = e.target.files[0];
      audioFileName = file.name;
      const sizeMB = (file.size / 1024 / 1024).toFixed(2);
      fileInfo.innerHTML = `<p>Chargement de <strong>${file.name}</strong> (${sizeMB} MB)...</p>`;
      const url = URL.createObjectURL(file);
      initWaveSurfer(url);
    }
  });

  // ─── Auto-load ref_audio.mp3 ───
  fetch('ref_audio.mp3', { method: 'HEAD' })
    .then(resp => {
      if (resp.ok) {
        initWaveSurfer('ref_audio.mp3');
      } else {
        fileInfo.innerHTML = '<p class="text-gray-400">Aucun audio pré-chargé. Charge un fichier ci-dessous.</p>';
      }
    })
    .catch(() => {
      fileInfo.innerHTML = '<p class="text-gray-400">Aucun audio pré-chargé. Charge un fichier ci-dessous.</p>';
    });

});
