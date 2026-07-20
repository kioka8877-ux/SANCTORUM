from pydub import AudioSegment
import glob, os

wavs = sorted(glob.glob('/tmp/chunks/chunk_*.wav'))
print(f'{len(wavs)} wavs found')
combined = AudioSegment.empty()
for f in wavs:
    seg = AudioSegment.from_wav(f)
    combined += seg
    print(f'  [+] {os.path.basename(f)}: {len(seg)/1000:.1f}s')
out = '/tmp/voice_003.mp3'
combined.export(out, format='mp3', bitrate='192k')
print(f'[DONE] {len(combined)/1000:.1f}s -> {out}')
