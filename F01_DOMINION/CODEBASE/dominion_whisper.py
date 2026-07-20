import sys, whisper

audio_path = sys.argv[1]
output_path = sys.argv[2]

model = whisper.load_model('base')
result = model.transcribe(audio_path, language='en')
text = result['text'].strip()
with open(output_path, 'w') as f:
    f.write(text)
print(f'[WHISPER] {len(text)} chars: {text[:120]}')
