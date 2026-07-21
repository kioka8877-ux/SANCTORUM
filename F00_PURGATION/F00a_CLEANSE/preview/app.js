document.addEventListener('DOMContentLoaded', function () {

  // ─── State ───
  let wavesurfer = null;
  let audioFile = null;
  let audioDuration = 0;
  let region = null;

  // ─── Auto-load pre-placed audio ───
  const PRELOAD_AUDIO = 'ref_audio.mp3';

  // ─── DOM refs ───
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const dropContent = document.getElementById('drop-content');
  const fileInfo = document.getElementById('file-info');
  const waveformSection = document.getElementById('waveform-section');
  const waveformContainer = document.getElementById('waveform-container');
  const optionsSection = document.getElementById('options-section');
  const exportSection = document.getElementById('export-section');
  const segmentStart = document.getElementById('segment-start');
  const segmentEnd = document.getElementById('segment-end');
  const playSegment = document.getElementById('play-segment');
  const playFull = document.getElementById('play-full');
  const stopPlay = document.getElementById('stop-play');
  const optVocalIsolation = document.getElementById('opt-vocal-isolation');
  const optDenoise = document.getElementById('opt-denoise');
  const optSpeed = document.getElementById('opt-speed');
  const speedValue = document.getElementById('speed-value');
  const configPreview = document.getElementById('config-preview');
  const downloadConfig = document.getElementById('download-config');
  const copyConfig = document.getElementById('copy-config');
  const copyFeedback = document.getElementById('copy-feedback');

  // ─── Auto-load pre-placed audio if available ───
  function tryPreloadAudio() {
    fetch(PRELOAD_AUDIO, { method: 'HEAD' })
      .then(resp => {
        if (resp.ok) {
          // File exists — load it
          audioFile = new File([''], 'ref_audio.mp3', { type: 'audio/mpeg' });
          loadAudioFromUrl(PRELOAD_AUDIO, 'ref_audio.mp3', 1154125);
        }
      })
      .catch(() => {
        // No pre-placed file, user will upload manually
      });
  }

  function loadAudioFromUrl(url, filename, filesize) {
    const sizeMB = (filesize / 1024 / 1024).toFixed(2);
    fileInfo.innerHTML = `
      <p>✅ <strong>${filename}</strong> (auto-chargé)</p>
      <p class="text-gray-400">${sizeMB} MB · audio/mpeg</p>
    `;
    fileInfo.classList.remove('hidden');

    if (wavesurfer) wavesurfer.destroy();

    wavesurfer = WaveSurfer.create({
      container: waveformContainer,
      waveColor: '#6b7280',
      progressColor: '#f59e0b',
      cursorColor: '#f59e0b',
      barWidth: 2,
      barRadius: 1,
      responsive: true,
      height: 100,
      url: url,
    });

    wavesurfer.on('ready', () => {
      audioDuration = wavesurfer.getDuration();
      waveformSection.classList.remove('hidden');
      optionsSection.classList.remove('hidden');
      exportSection.classList.remove('hidden');

      const defaultEnd = Math.min(20, audioDuration);
      segmentStart.value = 0;
      segmentEnd.value = defaultEnd.toFixed(1);
      segmentEnd.max = audioDuration.toFixed(1);

      enableRegionSelection();
      updateConfig();
    });

    wavesurfer.on('finish', () => { wavesurfer.seekTo(0); });
  }

  // Try to preload audio on page load
  tryPreloadAudio();

  // ─── File upload (manual) ───
  dropContent.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
  });

  function handleFile(file) {
    audioFile = file;
    const sizeMB = (file.size / 1024 / 1024).toFixed(2);
    fileInfo.innerHTML = `
      <p>✅ <strong>${file.name}</strong></p>
      <p class="text-gray-400">${sizeMB} MB · ${file.type || 'unknown type'}</p>
    `;
    fileInfo.classList.remove('hidden');

    const url = URL.createObjectURL(file);
    loadAudioFromUrl(url, file.name, file.size);
  }

  // ─── Region selection (click-drag on waveform) ───
  function enableRegionSelection() {
    let isDragging = false;
    let dragStart = 0;

    waveformContainer.addEventListener('mousedown', startDrag);
    waveformContainer.addEventListener('touchstart', startDrag);

    function startDrag(e) {
      const rect = waveformContainer.getBoundingClientRect();
      const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
      const pct = Math.max(0, Math.min(1, x / rect.width));
      dragStart = pct * audioDuration;
      isDragging = true;
      segmentStart.value = dragStart.toFixed(1);
    }

    document.addEventListener('mousemove', updateDrag);
    document.addEventListener('touchmove', updateDrag);

    function updateDrag(e) {
      if (!isDragging) return;
      const rect = waveformContainer.getBoundingClientRect();
      const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
      const pct = Math.max(0, Math.min(1, x / rect.width));
      const time = pct * audioDuration;
      if (time > dragStart) {
        segmentEnd.value = time.toFixed(1);
      }
      updateConfig();
    }

    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);

    function endDrag() {
      if (isDragging) {
        isDragging = false;
        // Ensure start < end
        const s = parseFloat(segmentStart.value);
        const en = parseFloat(segmentEnd.value);
        if (s > en) {
          segmentStart.value = en;
          segmentEnd.value = s;
        }
        updateConfig();
      }
    }
  }

  // ─── Manual input changes ───
  [segmentStart, segmentEnd].forEach(input => {
    input.addEventListener('input', updateConfig);
  });

  // ─── Playback ───
  playFull.addEventListener('click', () => {
    wavesurfer.seekTo(0);
    wavesurfer.play();
  });

  playSegment.addEventListener('click', () => {
    const start = parseFloat(segmentStart.value);
    const end = parseFloat(segmentEnd.value);
    wavesurfer.seekTo(start / audioDuration);
    wavesurfer.play();

    // Stop at end
    const checkTime = setInterval(() => {
      if (wavesurfer.getCurrentTime() >= end) {
        wavesurfer.pause();
        clearInterval(checkTime);
      }
    }, 50);
  });

  stopPlay.addEventListener('click', () => {
    wavesurfer.pause();
  });

  // ─── Speed slider ───
  optSpeed.addEventListener('input', () => {
    const val = parseFloat(optSpeed.value);
    speedValue.textContent = val.toFixed(2) + 'x';
    updateConfig();
  });

  // ─── Toggle changes ───
  [optVocalIsolation, optDenoise].forEach(toggle => {
    toggle.addEventListener('change', updateConfig);
  });

  // ─── Config generation ───
  function updateConfig() {
    const config = {
      source: audioFile ? audioFile.name : 'unknown',
      segment: {
        start: parseFloat(segmentStart.value) || 0,
        end: parseFloat(segmentEnd.value) || 20
      },
      vocal_isolation: optVocalIsolation.checked,
      denoise: optDenoise.checked,
      speed: parseFloat(optSpeed.value) || 1.0
    };
    configPreview.textContent = JSON.stringify(config, null, 2);
  }

  // ─── Download config ───
  downloadConfig.addEventListener('click', () => {
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
    navigator.clipboard.writeText(configPreview.textContent).then(() => {
      copyFeedback.classList.remove('hidden');
      setTimeout(() => copyFeedback.classList.add('hidden'), 2000);
    });
  });

});
