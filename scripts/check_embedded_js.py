from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for name in ("index.html", "products.html"):
    html = (ROOT / name).read_text(encoding="utf-8")
    soup_scripts = re.findall(r"<script([^>]*)>(.*?)</script>", html, flags=re.S | re.I)
    blocks = [(attrs, block) for attrs, block in soup_scripts if 'application/ld+json' not in attrs.lower() and 'src=' not in attrs.lower()]
    for index, (attrs, block) in enumerate(blocks):
        if not block.strip():
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as handle:
            handle.write(block)
            temp_name = handle.name
        result = subprocess.run(["node", "--check", temp_name], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f"{name} script {index} failed:\n{result.stderr}")
print("Embedded JavaScript syntax: OK")
