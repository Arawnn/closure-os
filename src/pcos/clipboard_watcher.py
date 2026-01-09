import hashlib
import re
import signal
import subprocess
import sys
import time
from typing import Optional, Set

import pyperclip
import yaml

# =========================
# Defaults
# =========================

DEFAULT_CHECK_INTERVAL = 1.0
DEFAULT_DEBOUNCE_SECONDS = 3.0
DEFAULT_ALLOWED_TAGS = {"brainstorm", "pcos"}

# =========================
# Runtime state
# =========================

running = True


# =========================
# Signal handling
# =========================


def handle_sigint(sig, frame):
    global running
    print("\n🛑 Stopping clipboard watcher...")
    running = False


signal.signal(signal.SIGINT, handle_sigint)

# =========================
# Frontmatter parsing
# =========================

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def extract_frontmatter(text: str) -> Optional[dict]:
    match = FRONTMATTER_RE.match(text.strip())
    if not match:
        return None

    raw_yaml = match.group(1)
    try:
        data = yaml.safe_load(raw_yaml)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def extract_brainstorm_metadata(
    text: str,
    allowed_tags: Set[str],
) -> Optional[dict]:
    fm = extract_frontmatter(text)
    if not fm:
        return None

    tags = fm.get("tags", [])
    if not isinstance(tags, list):
        return None

    normalized_tags = {str(tag).lower() for tag in tags}
    if not normalized_tags.intersection(allowed_tags):
        return None

    project = fm.get("project")
    if not project or not isinstance(project, str):
        return None

    return {
        "project": project.strip(),
        "tags": normalized_tags,
    }


# =========================
# Utilities
# =========================


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# =========================
# Watch loop (callable)
# =========================


def watch_clipboard(
    *,
    project: Optional[str],
    allowed_tags: Set[str],
    debounce_seconds: float,
    check_interval: float,
):
    print("🧠 Clipboard watcher started (CTRL+C to stop)")
    print(f"• allowed_tags={sorted(allowed_tags)}")
    print(f"• debounce={debounce_seconds}s")

    last_hash: Optional[str] = None
    last_trigger_ts: float = 0.0

    while running:
        try:
            text = pyperclip.paste() or ""
            text = text.strip()

            if not text:
                time.sleep(check_interval)
                continue

            metadata = extract_brainstorm_metadata(
                text,
                allowed_tags=allowed_tags,
            )
            if not metadata:
                time.sleep(check_interval)
                continue

            resolved_project = project or metadata["project"]

            h = hash_text(text)
            now = time.time()

            should_trigger = (
                h != last_hash
                and (now - last_trigger_ts) > debounce_seconds
            )

            if should_trigger:
                print(f"✨ Brainstorm detected → project={resolved_project}")

                subprocess.run(
                    ["pcos", "capture", "--project", resolved_project],
                    input=text,
                    text=True,
                    check=True,
                )

                last_hash = h
                last_trigger_ts = now

        except subprocess.CalledProcessError as e:
            print("❌ pcos capture failed:", e)

        except Exception as e:
            print("⚠️ Watcher error:", e)

        time.sleep(check_interval)

    print("👋 Watcher stopped.")
    sys.exit(0)
