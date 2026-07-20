import re

with open('SHARED/IN/script_003.txt') as f:
    text = f.read().strip()

# Split on newlines (each line is a sentence/phrase)
lines = [l.strip() for l in text.split('\n') if l.strip()]
print(f'{len(lines)} lines')

n = 3
size = max(1, len(lines) // n)
chunks = []
for i in range(n):
    start = i * size
    end = start + size if i < n - 1 else len(lines)
    chunk = ' '.join(lines[start:end])
    if chunk:
        chunks.append(chunk)

for i, c in enumerate(chunks):
    print(f'chunk_{i}: {len(c)} chars: {c[:60]}')
    with open(f'/tmp/chunk_{i}.txt', 'w') as f:
        f.write(c)
