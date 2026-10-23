"""영상에서 프레임 N장을 뽑아 한 장의 검수용 이미지로 만든다.

사용법: python3 tools/contact_sheet.py <영상.mp4> <출력.png> [장수=8]
렌더 후 겹침, 잘림, 잔상을 눈으로 확인할 때 쓴다.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

v, out = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v]))
tmp = Path(tempfile.mkdtemp())
ims = []
for k in range(n):
    s = d * (k + 0.5) / n if k < n - 1 else d - 0.2
    p = tmp / f"f{k}.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{s:.2f}", "-i", v, "-frames:v", "1", str(p)], check=True)
    ims.append(Image.open(p).resize((640, 360)))
W = Image.new("RGB", (1280, 360 * ((n + 1) // 2)))
for i, im in enumerate(ims):
    W.paste(im, ((i % 2) * 640, (i // 2) * 360))
W.save(out)
print(f"duration={d:.1f}s -> {out}")
