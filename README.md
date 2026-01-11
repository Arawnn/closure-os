# Project Closure OS (PCOS)

**Stop starting. Start finishing.**

Project Closure OS is a CLI tool that transforms scattered brainstorming into structured, tracked, and scheduled work. Built for developers who are great at starting projects but struggle to finish them.

## Why This Exists

We've all been there: dozens of half-finished side projects collecting dust, each one abandoned when the next shiny idea came along. PCOS creates a structured pipeline that transforms raw ideas into actionable work items, tracked in GitHub and scheduled in your calendar.

The goal is simple: **reduce the friction between having an idea and actually shipping it**.

---

## How It Works

PCOS implements a four-phase workflow:

```
Brainstorm → Contract → GitHub → Calendar
```

| Phase | Command | What Happens |
|-------|---------|--------------|
| **Capture** | `pcos watch` | Monitors clipboard for brainstorms, saves to Obsidian |
| **Contract** | `pcos contract` | AI generates structured project contract from brainstorm |
| **Publish** | `pcos publish` | Creates GitHub repo, README, and issues from contract |
| **Schedule** | `pcos schedule` | Plans calendar events with smart spacing |

---

## Quick Start

### Prerequisites

- Python 3.10+
- [Obsidian](https://obsidian.md/) with [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin
- GitHub account with personal access token
- Google Cloud project with Calendar API enabled
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/closure-os.git
cd closure-os

# Install the package
pip install -e .

# Copy and configure
cp config.example.yaml config.yaml
```

### Environment Variables

Create a `.env` file in the project root:

```env
OBSIDIAN_API_KEY=your_obsidian_api_key
GITHUB_TOKEN=your_github_personal_access_token
OPENAI_API_KEY=your_openai_api_key
```

### Configuration

Edit `config.yaml`:

```yaml
vault_name: "MyVault"
obsidian_api_base: "http://127.0.0.1:27123"
projects_root: "projects"

github:
  owner: "your-github-user"
  visibility: "public"

calendar:
  calendar_id: "primary"
  slot_minutes: 60
  work_days: ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
  work_hours:
    start: "09:00"
    end: "18:00"
  max_events_per_day: 3
```

---

## Usage

### The Workflow

#### 1. Start the Watcher

```bash
pcos watch
```

The watcher monitors your clipboard for markdown content with specific tags (`brainstorm`, `pcos`). When detected, it automatically captures the content to your Obsidian vault.

#### 2. Write a Brainstorm

Create a markdown file with YAML frontmatter:

```markdown
---
title: My Awesome Project
type: brainstorm
project: awesome-project
tags: [brainstorm, pcos]
---

## Summary
A brief description of what you want to build.

## Ideas
- Feature idea 1
- Feature idea 2
- Feature idea 3

## Goals
- What does success look like?
```

Copy this content to your clipboard. The watcher will detect it and save it as `{projects_root}/awesome-project/00_brainstorm.md` in your Obsidian vault.

#### 3. Generate a Contract

```bash
pcos contract awesome-project
```

This sends your brainstorm to OpenAI, which generates a structured project contract with:

- Clear objective and definition of done
- Deadline
- Scoped tickets with Fibonacci estimates
- Explicitly excluded scope

The contract is saved as `01_project_contract.md` in your project folder.

#### 4. Publish to GitHub

```bash
pcos publish awesome-project
```

This creates:

- A GitHub repository (if it doesn't exist)
- A README generated from your contract
- GitHub issues for each ticket

#### 5. Schedule Your Work

```bash
pcos schedule awesome-project
```

The scheduler:

- Fetches open, unscheduled issues from GitHub
- Matches them with contract tickets
- Plans a smart schedule (quick wins first, proper spacing)
- Creates Google Calendar events
- Marks issues as "scheduled"

---

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `pcos watch` | Monitor clipboard for brainstorms | `pcos watch --allowed-tags brainstorm,pcos` |
| `pcos capture` | Manually capture content to Obsidian | `pcos capture --project my-project --input file.md` |
| `pcos contract` | Generate contract from brainstorm | `pcos contract my-project` |
| `pcos publish` | Publish to GitHub | `pcos publish my-project` |
| `pcos schedule` | Schedule issues to calendar | `pcos schedule my-project` |
| `pcos validate` | Validate config and contract files | `pcos validate contract.md` |

### Watch Options

```bash
pcos watch \
  --project my-project \          # Force project name (optional)
  --allowed-tags brainstorm,pcos \ # Tags to monitor
  --debounce 3.0 \                 # Debounce delay in seconds
  --interval 1.0                   # Polling interval
```

---

## Project Structure

```
closure-os/
├── src/pcos/
│   ├── cli.py                 # Main CLI entry point
│   ├── config.py              # Configuration management
│   ├── parser.py              # Contract parsing & validation
│   ├── contract_generator.py  # LLM-powered contract generation
│   ├── contracts.py           # Contract loading utilities
│   ├── clipboard_watcher.py   # Real-time clipboard monitoring
│   ├── obsidian.py            # Obsidian REST API client
│   ├── github.py              # GitHub API client
│   ├── calendar.py            # Google Calendar API client
│   ├── llm.py                 # OpenAI API client
│   ├── issues.py              # GitHub issue synchronization
│   ├── scheduler.py           # Smart scheduling algorithm
│   ├── prompts.py             # LLM prompt templates
│   └── renderers.py           # README markdown generation
├── examples/
│   ├── brainstorm.md          # Example brainstorm format
│   └── contract.md            # Example contract format
├── docs/
│   └── backlog.md             # Deferred enhancements
├── config.example.yaml        # Configuration template
└── pyproject.toml             # Project metadata
```

---

## Data Formats

### Brainstorm Format

```markdown
---
title: Project Name
type: brainstorm
project: my-project
tags: [brainstorm, pcos]
---

## Summary
What are you building and why?

## Ideas
- Feature 1
- Feature 2
```

### Contract Format

```markdown
---
project: my-project
title: Project Title
objective: Clear project objective
definition_of_done: Specific completion criteria
deadline: 2026-03-01
excluded_scope:
  - Item explicitly out of scope
tickets:
  - name: Build authentication system
    estimate_slots: 8
    description: Implement JWT-based auth
    scope_excluded:
      - OAuth integration
---

## Tickets

| # | Ticket | Estimate | Description |
|---|--------|----------|-------------|
| 1 | Build authentication | 8 | JWT-based auth |
```

---

## Smart Scheduling

The scheduling algorithm uses estimation-based spacing to prevent burnout:

| Estimate (slots) | Spacing |
|------------------|---------|
| 1-2 | 1 day |
| 3-5 | 2 days |
| 8+ | estimate/2 days (min 3) |

**Features:**

- Quick wins first (sorted by estimate)
- Alternates morning (7:00) and evening slots
- Respects work day configuration
- Enforces rest days every 7 consecutive days

---

## Architecture

<details>
<summary>Component Diagram</summary>

```
┌─────────────────────────────────────────────────────────────┐
│                    PROJECT CLOSURE OS                        │
└─────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │   Clipboard  │──── pcos watch ────┐
     └──────────────┘                    │
                                         ▼
     ┌──────────────┐              ┌──────────────┐
     │   Markdown   │──── pcos ───▶│   Obsidian   │
     │    File      │    capture   │    Vault     │
     └──────────────┘              └──────┬───────┘
                                          │
                                   pcos contract
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │   OpenAI     │
                                   │   (GPT-4)    │
                                   └──────┬───────┘
                                          │
                                          ▼
                                   ┌──────────────┐
     ┌──────────────┐              │   Contract   │
     │   GitHub     │◀── pcos ────│     in       │
     │  Repository  │    publish   │   Obsidian   │
     └──────┬───────┘              └──────────────┘
            │
     pcos schedule
            │
            ▼
     ┌──────────────┐
     │   Google     │
     │   Calendar   │
     └──────────────┘
```

</details>

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `typer` | CLI framework |
| `pyyaml` | YAML parsing |
| `rich` | Terminal formatting |
| `requests` | HTTP client |
| `python-dotenv` | Environment variables |
| `google-api-python-client` | Google Calendar API |
| `google-auth-oauthlib` | OAuth 2.0 flow |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is open source. See the LICENSE file for details.

---

## Acknowledgments

Built with the philosophy that the best project management system is one that gets out of your way and lets you focus on shipping.

*"The only way to finish a project is to start finishing it."*
