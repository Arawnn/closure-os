import requests
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Local only for now


class ObsidianError(Exception):
    pass


class ObsidianClient:
    def __init__(self, base_url: str, vault_name: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.vault_name = vault_name
        self.api_key = api_key

        
        self.session = requests.Session()
        self.session.verify = False  # Local only for now

        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "text/plain; charset=utf-8",
        })

    def _build_note_url(self, path: str) -> str:
        """
        Build URL like:
        https://127.0.0.1:27124/vault/Obsidian%20Vault/path/to/file.md
        """
        vault = quote(self.vault_name)
        note_path = quote(path)
        return f"{self.base_url}/vault/{vault}/{note_path}"

    def write_note(self, path: str, content: str):
        url = self._build_note_url(path)

        r = self.session.put(
            url,
            data=content.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8"},
            timeout=10,
        )

        if not r.ok:
            raise ObsidianError(
                f"Failed to write note {path}: {r.status_code} {r.text}"
            )
        
    def read_note(self, path: str) -> str:
        url = self._build_note_url(path)

        r = self.session.get(url, timeout=10)
        r.raise_for_status()

        return r.text