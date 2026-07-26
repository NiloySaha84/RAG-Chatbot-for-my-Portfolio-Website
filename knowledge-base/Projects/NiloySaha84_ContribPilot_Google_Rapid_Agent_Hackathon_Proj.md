# ContribPilot

**ContribPilot is an AI-powered open source contribution coach built with Gemini, Google Cloud, and GitLab MCP.**

The biggest barrier to contributing to open source is not writing code — it's figuring out where to start.

Developers often struggle to:

- Find beginner-friendly issues
- Understand unfamiliar repositories
- Follow project-specific contribution workflows
- Determine whether an issue matches their skill level
- Know exactly what steps to take before opening a Merge Request

ContribPilot solves this problem by acting as a contribution coach.

A user provides their skills and interests, and ContribPilot:

1. Finds relevant beginner-friendly GitLab issues
2. Reads repository context (README, CONTRIBUTING, documentation, and project files)
3. Explains the issue in plain language
4. Assesses difficulty and required skills
5. Generates a repository-specific implementation plan
6. Guides the user from issue selection to Merge Request submission

The project was built for the **Google Cloud Agent Hackathon** using:

- Gemini
- Google Cloud
- GitLab MCP
- GitLab OAuth
- FastAPI
- Cloud Run

---

# Example Workflow

User:

> I know Python and Docker. Help me make my first open source contribution.

ContribPilot:

1. Searches GitLab for suitable beginner-friendly issues
2. Ranks opportunities using BM25-based relevance scoring
3. Retrieves repository context
4. Reads README and contribution guidelines
5. Generates a personalized implementation plan

Example output:

- Difficulty: Beginner
- Estimated time: 1–2 hours
- Skills required: Python, Git
- Recommended branch name
- Files likely involved
- Testing instructions
- Merge Request checklist

Instead of receiving a list of links, the user receives a complete contribution roadmap.

---

# Why ContribPilot?

Most issue recommendation tools stop at discovery.

ContribPilot goes further.

It combines issue discovery, repository understanding, contribution guidance, and GitLab workflow knowledge into a single agent experience.

The goal is simple:

**Help developers successfully complete their first open source contribution.**

---

# Architecture

```text
Browser  ──►  ContribPilot (Cloud Run)
                  │
                  │  MCP over HTTP (/mcp)
                  ▼
              GitLab MCP backend (Cloud Run)
                  │
                  │  GitLab REST API + OAuth
                  ▼
              gitlab.com
```

| Part | Folder | What it is |
|------|--------|------------|
| MCP backend | `app/` | FastAPI app, OAuth, GitLab client, MCP tool handlers |
| ContribPilot | `contrib_pilot/` | ADK agent + FastAPI server + chat UI |
| Standalone ADK agent | `adk_agent/` | Minimal agent wired to the MCP backend |
| Deploy scripts | `scripts/` | One-command Cloud Run deployments |

---

# Agent Workflow

```text
User
↓
Provides skills and experience

ContribPilot
↓
recommend_contribution_issues

GitLab MCP Backend
↓
GitLab

ContribPilot
↓
get_issue

ContribPilot
↓
read_project_files

ContribPilot
↓
Generates repository-specific implementation plan

User
↓
Starts contributing
```

---

# GitLab MCP Integration

ContribPilot uses a custom GitLab MCP backend that exposes GitLab functionality as MCP tools.

The agent uses MCP tools to:

- Discover contribution opportunities
- Retrieve issue details
- Search projects
- Read repository context
- Analyze repositories
- Generate contribution plans

This allows the Gemini-powered agent to reason over real GitLab data and take meaningful actions beyond simple chat responses.

---

# What ContribPilot Does

You open the chat, tell it your skills (Python, React, Docker, whatever), and it:

1. **Finds issues** — searches GitLab and ranks open issues with BM25 scoring, biased toward beginner-friendly labels such as "good first issue" and "help wanted".
2. **Reads the repo** — pulls README, CONTRIBUTING, docs, and config files so advice is specific to that repository.
3. **Builds a plan** — once you pick an issue, it walks through setup, branching, likely files to touch, testing, and opening a merge request.

You connect your GitLab account once via OAuth so the backend can search issues and read repositories on your behalf.

---

# MCP Tools

The backend exposes these tools:

| Tool | Purpose |
|--------|----------|
| `recommend_contribution_issues` | Search + BM25 rank beginner-friendly issues |
| `read_project_files` | Fetch README, CONTRIBUTING, docs, and project context |
| `gitlab_search` | Search issues, merge requests, or projects |
| `get_issue` | Full details for a GitLab issue |
| `create_issue` | Open a new issue |
| `get_merge_request` | Retrieve merge request details |
| `create_merge_request` | Open a merge request |
| `get_merge_request_commits` | Retrieve MR commits |
| `get_merge_request_diffs` | Retrieve MR diffs |
| `get_merge_request_pipelines` | Retrieve MR pipelines |
| `get_pipeline_jobs` | Retrieve pipeline jobs |
| `semantic_code_search` | Code search (blob search fallback) |
| `get_mcp_server_version` | MCP version check |

ContribPilot primarily uses:

- `recommend_contribution_issues`
- `get_issue`
- `read_project_files`
- `gitlab_search`

---

# Issue Ranking

`recommend_contribution_issues` performs more than a basic GitLab search.

The ranking process:

1. Generates targeted search queries based on skills and contribution keywords.
2. Retrieves issue details and recent discussion.
3. Scores issues using BM25 across:
   - title
   - description
   - labels
   - comments
4. Applies a freshness bonus for recently updated issues.
5. Returns the highest ranked contribution opportunities.

Ranking logic lives in:

```text
app/issue_ranking.py
app/issue_recommender.py
```

---

# GitLab Authentication

The backend uses **OAuth 2.0 with Dynamic Client Registration (RFC 7591) and PKCE**.

No manual GitLab OAuth application setup is required.

## Local Development

1. Copy `.env.example` to `.env`
2. Start the backend:

```bash
python server.py
```

3. Visit:

```text
http://localhost:8080/auth/gitlab
```

4. Authenticate with GitLab

Access tokens are stored locally in `.env`.

OAuth client metadata is stored in:

```text
.gitlab_oauth.json
```

---

## Cloud Run

1. Deploy the backend
2. Visit:

```text
{SERVICE_URL}/auth/gitlab
```

3. Authenticate once

OAuth credentials are stored in Google Secret Manager.

Access tokens are refreshed automatically when possible.

---

## Public vs Private Repositories

- Most issue discovery workflows work with the OAuth `mcp` scope.
- `read_project_files` works on public repositories without additional scopes.
- Private repository file access requires broader GitLab permissions such as `read_repository` or `api`.

---

# Prerequisites

- Python 3.12+
- GitLab account
- Google Cloud project
- Vertex AI enabled
- Google Cloud CLI
- Docker (via Cloud Build)

---

# Local Setup — MCP Backend

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python server.py
```

Authenticate GitLab:

```text
http://localhost:8080/auth/gitlab
```

Useful endpoints:

| URL | Purpose |
|------|---------|
| `/` | Service information |
| `/mcp` | MCP endpoint |
| `/auth/gitlab` | GitLab OAuth login |
| `/auth/status` | Authentication status |
| `/health` | Health check |

---

# Local Setup — ContribPilot

```bash
cd contrib_pilot

pip install -r requirements.txt

export MCP_BACKEND_URL=http://localhost:8080/mcp
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_CLOUD_LOCATION=us-central1

python -m contrib_pilot.server
```

Open:

```text
http://localhost:8081
```

Connect GitLab through the UI.

---

# Deploy to Cloud Run

## Deploy MCP Backend

```bash
./scripts/deploy-cloud-run.sh YOUR_GCP_PROJECT us-central1 gitlab-mcp-backend
```

After deployment:

```text
{SERVICE_URL}/auth/gitlab
```

Authenticate once.

---

## Deploy ContribPilot

```bash
MCP_BACKEND_URL=https://your-mcp-service.run.app/mcp \
./scripts/deploy-agent-cloud-run.sh YOUR_GCP_PROJECT us-central1 contrib-pilot-agent
```

Open the resulting Cloud Run URL to access the application.

---

# Standalone ADK Agent

The repository also includes a minimal standalone ADK agent.

Purpose:

- ADK experimentation
- Agent Engine testing
- MCP backend demonstrations

Relevant files:

```text
adk_agent/agent.py
adk_agent/mcp_config.py
```

---

# Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── mcp_server.py
│   ├── oauth.py
│   ├── gitlab_client.py
│   ├── issue_ranking.py
│   ├── issue_recommender.py
│   ├── project_context.py
│   ├── token_store.py
│   └── secret_store.py
│
├── contrib_pilot/
│   ├── agent.py
│   ├── server.py
│   └── static/
│
├── adk_agent/
│
├── scripts/
│
├── tests/
│
├── server.py
├── Dockerfile
├── cloudbuild.yaml
├── requirements.txt
└── .env.example
```

---

# Tests

```bash
pip install pytest

pytest tests/
```

Tests cover:

- OAuth configuration
- Token storage
- BM25 ranking
- Repository file prioritization

---

# Troubleshooting

### GitLab is not authenticated

Visit:

```text
/auth/gitlab
```

Check:

```text
/auth/status
```

---

### OAuth redirect mismatch

Verify:

```text
APP_BASE_URL
```

matches the deployed Cloud Run URL.

---

### ContribPilot cannot reach GitLab

Authenticate through the GitLab connection flow and verify the MCP backend is running.

---

### read_project_files returns 403

The repository may be private or require additional GitLab scopes.

---

### Agent Builder / MCP 401

If using Agent Builder, leave `MCP_AUTH_TOKEN` unset because Agent Builder cannot send custom Authorization headers.

---

### Token refresh failures

Re-authenticate via:

```text
/auth/gitlab
```

Verify Secret Manager permissions on Cloud Run.

---

# License

This project is licensed under the MIT License. See the LICENSE file for details.
