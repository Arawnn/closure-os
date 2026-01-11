from pcos.config import get_env
import requests


class GitHubClient:
    def __init__(self):
        token = get_env("GITHUB_TOKEN")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
            }
        )
        self.api = "https://api.github.com"

    # ---------- Repo ----------

    def get_repo(self, owner: str, name: str):
        r = self.session.get(f"{self.api}/repos/{owner}/{name}")
        return r if r.status_code == 200 else None

    def create_repo(self, name: str, private: bool = False):
        payload = {"name": name, "private": private}
        r = self.session.post(f"{self.api}/user/repos", json=payload)
        r.raise_for_status()
        return r.json()

    def get_user(self):
        r = self.session.get(f"{self.api}/user")
        r.raise_for_status()
        return r.json()

    # ---------- README ----------

    def upsert_readme(self, owner: str, repo: str, content: str):
        import base64

        path = f"{self.api}/repos/{owner}/{repo}/contents/README.md"
        encoded = base64.b64encode(content.encode("utf-8")).decode()

        existing = self.session.get(path)
        payload = {"message": "Sync README", "content": encoded}

        if existing.status_code == 200:
            sha = existing.json()["sha"]
            payload["sha"] = sha

        r = self.session.put(path, json=payload)
        r.raise_for_status()

    # ---------- Issues ----------

    def list_issues(self, owner: str, repo: str):
        r = self.session.get(
            f"{self.api}/repos/{owner}/{repo}/issues",
            params={"state": "all"},
        )
        r.raise_for_status()
        return r.json()

    def create_issue(self, owner: str, repo: str, title: str, body: str):
        payload = {"title": title, "body": body}
        r = self.session.post(
            f"{self.api}/repos/{owner}/{repo}/issues",
            json=payload,
        )
        r.raise_for_status()
        return r.json()

    def list_open_unscheduled_issues(self, owner: str, repo: str):
        issues = self.list_issues(owner, repo)
        return [
            i
            for i in issues
            if "scheduled" not in [l["name"] for l in i["labels"]]
            and i["state"] == "open"
        ]

    def add_label(self, owner: str, repo: str, issue_number: int, label: str):
        url = f"{self.api}/repos/{owner}/{repo}/issues/{issue_number}/labels"
        self.session.post(url, json={"labels": [label]}).raise_for_status()
