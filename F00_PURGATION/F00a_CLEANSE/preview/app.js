document.addEventListener('DOMContentLoaded', function () {

  // ─── State ───
  let wavesurfer = null;
  let wsRegions = null;
  let activeRegion = null;
  let clickCount = 0;
  let audioDuration = 0;
  let audioFileName = 'ref_audio.mp3';

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

    // Regions plugin
    wsRegions = wavesurfer.registerPlugin(
      WaveSurfer.Regions.create()
    );

    wavesurfer.on('ready', () => {
      audioDuration = wavesurfer.getDuration();
      fileInfo.innerHTML = `
        <p>✅ <strong>${audioFileName}</strong> · ${audioDuration.toFixed(1)}s</p>
        <p class="text-gray-400">Clique sur la waveform pour poser IN puis OUT</p>
      `;
      updateConfig();
    });

    // Click on waveform → set IN then OUT
    wavesurfer.on('interaction', (newTime) => {
      clickCount++;

      if (clickCount === 1) {
        // First click = IN point
        // Remove any existing region
        wsRegions.clearRegions();
        activeRegion = null;

        // Create a small region starting here
        const start = newTime;
        const end = Math.min(newTime + 5, audioDuration); // default 5s preview
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
        // Second click = OUT point
        if (activeRegion) {
          const currentStart = activeRegion.start;
          if (newTime > currentStart) {
            // Move end to clicked position
            activeRegion.setOptions({
              end: Math.min(newTime, audioDuration),
            });
          } else {
            // Clicked before start → swap: new click is IN, old start is OUT
            activeRegion.setOptions({
              start: newTime,
              end: currentStart,
            });
          }
          updateTimeLabels();
          updateConfig();
        }
        // Reset click count for next selection
        clickCount = 0;
      }
    });

    // Region updated (drag/resize)
    wsRegions.on('region-updated', (region) => {
      activeRegion = region;
      updateTimeLabels();
      updateConfig();
    });

    // Region clicked → play it
    wsRegions.on('region-clicked', (region, e) => {
      e.stopPropagation();
      activeRegion = region;
      region.play();
    });

    wavesurfer.on('finish', () => {
      wavesurfer.seekTo(0);
    });
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

  // ─── Playback controls ───
  playSegment.addEventListener('click', () => {
    if (activeRegion) {
      activeRegion.play();
    } else {
      alert('Sélectionne d\'abord un segment (clic IN puis clic OUT sur la waveform)');
    }
  });

  playFull.addEventListener('click', () => {
    wavesurfer.seekTo(0);
    wavesurfer.play();
  });

  stopPlay.addEventListener('click', () => {
    wavesurfer.pause();
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
