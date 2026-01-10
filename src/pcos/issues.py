def sync_issues(client, owner: str, repo: str, tickets: list):
    existing = client.list_issues(owner, repo)
    existing_titles = {issue["title"] for issue in existing}

    created = 0

    for d in tickets:
        title = d["name"]
        body = d.get("description", "")

        if title in existing_titles:
            continue

        client.create_issue(owner, repo, title, body)
        created += 1

    return created
