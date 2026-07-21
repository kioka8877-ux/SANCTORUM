document.addEventListener('DOMContentLoaded', function () {

  // ─── State ───
  let wavesurfer = null;
  let audioBuffer = null;
  let audioContext = null;
  let currentSource = null;
  let audioDuration = 0;
  let audioFileName = 'output.mp3';
  let currentSpeed = 0.85;
  let isPlaying = false;

  // ─── DOM ───
  const fileInfo = document.getElementById('file-info');
  const fileInput = document.getElementById('file-input');
  const waveformContainer = document.getElementById('waveform-container');
  const playOriginal = document.getElementById('play-original');
  const playSlowed = document.getElementById('play-slowed');
  const stopPlay = document.getElementById('stop-play');
  const nowPlaying = document.getElementById('now-playing');
  const npSpeed = document.getElementById('np-speed');
  const playSpeedLabel = document.getElementById('play-speed-label');
  const optSpeed = document.getElementById('opt-speed');
  const speedValue = document.getElementById('speed-value');
  const durOriginal = document.getElementById('dur-original');
  const durAdjusted = document.getElementById('dur-adjusted');
  const durSpeedLabel = document.getElementById('dur-speed-label');
  const durDiff = document.getElementById('dur-diff');
  const configPreview = document.getElementById('config-preview');
  const downloadConfig = document.getElementById('download-config');
  const copyConfig = document.getElementById('copy-config');
  const copyFeedback = document.getElementById('copy-feedback');
  const presetBtns = document.querySelectorAll('.preset-btn');

  // ─── Init WaveSurfer ───
  function initWaveSurfer(url, name) {
    if (wavesurfer) {
      wavesurfer.destroy();
      wavesurfer = null;
    }

    audioFileName = name;
    wavesurfer = WaveSurfer.create({
      container: waveformContainer,
      waveColor: '#6b7280',
      progressColor: '#f59e0b',
      cursorColor: '#f59e0b',
      cursorWidth: 2,
      barWidth: 2,
      barRadius: 1,
      responsive: true,
      height: 80,
      url: url,
    });

    wavesurfer.on('ready', () => {
      audioDuration = wavesurfer.getDuration();
      fileInfo.innerHTML = `<p>✅ <strong>${audioFileName}</strong> · ${audioDuration.toFixed(1)}s</p>`;
      updateDurations();
      updateConfig();
      decodeAudio(url);
    });

    wavesurfer.on('finish', () => {
      wavesurfer.seekTo(0);
      isPlaying = false;
      nowPlaying.classList.add('hidden');
    });
  }

  // ─── Decode for Web Audio API ───
  async function decodeAudio(url) {
    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    } catch (e) {
      console.warn('[WEB AUDIO] Decode failed:', e);
    }
  }

  // ─── Play at speed ───
  function playAtSpeed(speed) {
    stopAll();

    if (!audioBuffer || !audioContext) {
      // Fallback: wavesurfer
      if (wavesurfer) {
        wavesurfer.setPlaybackRate(speed, true);
        wavesurfer.seekTo(0);
        wavesurfer.play();
      }
    } else {
      const ctx = audioContext;
      if (ctx.state === 'suspended') ctx.resume();

      const source = ctx.createBufferSource();
      source.buffer = audioBuffer;
      source.playbackRate.value = speed;
      source.connect(ctx.destination);
      source.start(0);
      currentSource = source;
    }

    isPlaying = true;
    npSpeed.textContent = speed.toFixed(2) + 'x';
    nowPlaying.classList.remove('hidden');
  }

  function stopAll() {
    if (currentSource) {
      try { currentSource.stop(); } catch (e) {}
      currentSource = null;
    }
    if (wavesurfer) {
      wavesurfer.pause();
    }
    isPlaying = false;
    nowPlaying.classList.add('hidden');
  }

  // ─── Duration display ───
  function updateDurations() {
    if (!audioDuration) return;
    const adjusted = audioDuration / currentSpeed;
    const diff = adjusted - audioDuration;
    const sign = diff > 0 ? '+' : '';

    durOriginal.textContent = audioDuration.toFixed(1) + 's';
    durAdjusted.textContent = adjusted.toFixed(1) + 's';
    durSpeedLabel.textContent = currentSpeed.toFixed(2) + 'x';
    durDiff.textContent = `${sign}${diff.toFixed(1)}s · ${diff > 0 ? 'plus lent' : diff < 0 ? 'plus rapide' : 'identique'}`;
  }

  // ─── Config ───
  function updateConfig() {
    const config = {
      source: audioFileName,
      speed: parseFloat(currentSpeed.toFixed(2)),
      original_duration: parseFloat(audioDuration.toFixed(1)),
      adjusted_duration: parseFloat((audioDuration / currentSpeed).toFixed(1))
    };
    configPreview.textContent = JSON.stringify(config, null, 2);
  }

  // ─── Speed change ───
  function setSpeed(speed) {
    currentSpeed = speed;
    speedValue.textContent = speed.toFixed(2) + 'x';
    playSpeedLabel.textContent = speed.toFixed(2) + 'x';
    optSpeed.value = speed;

    // Update preset active state
    presetBtns.forEach(btn => {
      const btnSpeed = parseFloat(btn.dataset.speed);
      if (Math.abs(btnSpeed - speed) < 0.005) {
        btn.classList.add('preset-active');
      } else {
        btn.classList.remove('preset-active');
      }
    });

    updateDurations();
    updateConfig();
  }

  // ─── Events ───
  optSpeed.addEventListener('input', () => {
    setSpeed(parseFloat(optSpeed.value));
  });

  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      setSpeed(parseFloat(btn.dataset.speed));
    });
  });

  playOriginal.addEventListener('click', () => {
    playAtSpeed(1.0);
  });

  playSlowed.addEventListener('click', () => {
    playAtSpeed(currentSpeed);
  });

  stopPlay.addEventListener('click', stopAll);

  downloadConfig.addEventListener('click', () => {
    const blob = new Blob([configPreview.textContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'post_config.json';
    a.click();
    URL.revokeObjectURL(url);
  });

  copyConfig.addEventListener('click', () => {
    navigator.clipboard.writeText(configPreview.textContent).then(() => {
      copyFeedback.classList.remove('hidden');
      setTimeout(() => copyFeedback.classList.add('hidden'), 2000);
    });
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      const file = e.target.files[0];
      const sizeMB = (file.size / 1024 / 1024).toFixed(2);
      fileInfo.innerHTML = `<p>Chargement de <strong>${file.name}</strong> (${sizeMB} MB)...</p>`;
      initWaveSurfer(URL.createObjectURL(file), file.name);
    }
  });

  // ─── Auto-load output.mp3 ───
  fetch('output.mp3', { method: 'HEAD' })
    .then(resp => {
      if (resp.ok) {
        initWaveSurfer('output.mp3', 'output.mp3');
      } else {
        fileInfo.innerHTML = '<p class="text-gray-400">Aucun audio pré-chargé. Charge un fichier ci-dessous.</p>';
      }
    })
    .catch(() => {
      fileInfo.innerHTML = '<p class="text-gray-400">Aucun audio pré-chargé. Charge un fichier ci-dessous.</p>';
    });

});
