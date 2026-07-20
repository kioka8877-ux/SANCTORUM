import re, json

with open('SHARED/IN/script_003.txt') as f:
    text = f.read().strip()

lines = [l.strip() for l in text.split('\n') if l.strip()]
print(f'{len(lines)} lines total')

n = 3
size = max(1, len(lines) // n)
chunks = {}
for i in range(n):
    start = i * size
    end = start + size if i < n - 1 else len(lines)
    chunk = ' '.join(lines[start:end])
    chunks[str(i)] = chunk
    print(f'chunk_{i}: {len(chunk)} chars: {chunk[:60]}')

with open('/tmp/chunks.json', 'w') as f:
    json.dump(chunks, f)
print(f'chunks.json written with {len(chunks)} chunks')
