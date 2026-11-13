"""Zet de HTML uit een opgeslagen read_artifact-resultaat om naar index.html.

Gebruik: python3 scripts/sync_artifact.py <pad-naar-read_artifact-output> <doel-index.html>
Het read_artifact-resultaat mag JSON (lijst met tekstblokken) of platte tekst zijn.
"""
import json
import re
import sys

src, dest = sys.argv[1], sys.argv[2]
raw = open(src, encoding="utf-8").read()
try:
    data = json.loads(raw)
    text = "\n".join(b.get("text", "") for b in data if isinstance(b, dict))
except (json.JSONDecodeError, AttributeError, TypeError):
    text = raw

doc = None
for m in re.finditer(r"<(untrusted-document-[0-9a-f]+)>(.*?)</\1>", text, re.S):
    if "<!DOCTYPE html>" in m.group(2):
        doc = m.group(2)
        break
if doc is None:
    sys.exit("Geen HTML-document gevonden in het artifact-resultaat")

inner = doc[doc.find("<!DOCTYPE html>"):].rstrip()
if inner.endswith("</body></html>"):
    inner = inner[: -len("</body></html>")].rstrip()
if not inner.endswith("</html>") or len(inner) < 1000:
    sys.exit("HTML lijkt onvolledig, niets weggeschreven")

with open(dest, "w", encoding="utf-8") as f:
    f.write(inner + "\n")
print(f"index.html bijgewerkt ({len(inner)} tekens)")
