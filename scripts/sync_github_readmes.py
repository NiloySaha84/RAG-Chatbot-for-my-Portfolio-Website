#!/usr/bin/env python3
"""Sync GitHub repository READMEs into knowledge-base/Projects/."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

DEFAULT_USERNAME = "NiloySaha84"
DEFAULT_OUTPUT_DIR = "knowledge-base/Projects"
GITHUB_API = "https://api.github.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download GitHub repository READMEs into the knowledge base."
    )
    parser.add_argument(
        "--username",
        default=os.getenv("GITHUB_USERNAME", DEFAULT_USERNAME),
        help=f"GitHub username (default: {DEFAULT_USERNAME})",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for README markdown files (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--include-forks",
        action="store_true",
        help="Include forked repositories",
    )
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include private repositories (requires GITHUB_TOKEN with repo scope)",
    )
    return parser.parse_args()


def github_headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def list_repositories(
    username: str,
    token: str | None,
    include_forks: bool,
    include_private: bool,
) -> list[dict]:
    repos: list[dict] = []
    page = 1

    while True:
        if include_private and token:
            url = f"{GITHUB_API}/user/repos"
            params = {
                "per_page": 100,
                "page": page,
                "sort": "updated",
                "affiliation": "owner",
            }
        else:
            url = f"{GITHUB_API}/users/{username}/repos"
            params = {"per_page": 100, "page": page, "sort": "updated"}

        response = requests.get(url, headers=github_headers(token), params=params, timeout=30)
        response.raise_for_status()
        batch = response.json()

        if not batch:
            break

        for repo in batch:
            if repo.get("fork") and not include_forks:
                continue
            if repo.get("private") and not include_private:
                continue
            repos.append(repo)

        page += 1

    return repos


def fetch_readme(owner: str, repo_name: str, token: str | None) -> str | None:
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/readme"
    headers = github_headers(token)
    headers["Accept"] = "application/vnd.github.raw"

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.text


def clear_existing_readmes(output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    removed = 0

    for path in output_dir.glob("*.md"):
        path.unlink()
        print(f"Removed: {path}")
        removed += 1

    return removed


def sync_readmes(
    username: str,
    output_dir: Path,
    token: str | None,
    include_forks: bool,
    include_private: bool,
) -> tuple[int, int, int, int]:
    removed = clear_existing_readmes(output_dir)
    print(f"Cleared {removed} existing README file(s)\n")

    repos = list_repositories(username, token, include_forks, include_private)

    saved = 0
    skipped = 0
    failed = 0

    for repo in repos:
        repo_name = repo["name"]
        owner = repo["owner"]["login"]
        output_path = output_dir / f"{username}_{repo_name}.md"

        try:
            readme = fetch_readme(owner, repo_name, token)
            if readme is None:
                print(f"Skipped (no README): {owner}/{repo_name}")
                skipped += 1
                continue

            output_path.write_text(readme.strip() + "\n", encoding="utf-8")
            print(f"Saved: {output_path}")
            saved += 1
        except requests.HTTPError as exc:
            print(f"Failed: {owner}/{repo_name} ({exc})", file=sys.stderr)
            failed += 1

    return removed, saved, skipped, failed


def main() -> int:
    load_dotenv(override=True)
    args = parse_args()

    token = os.getenv("GITHUB_TOKEN")
    output_dir = Path(args.output_dir)

    print(f"Syncing READMEs for GitHub user: {args.username}")
    print(f"Output directory: {output_dir.resolve()}")

    try:
        removed, saved, skipped, failed = sync_readmes(
            username=args.username,
            output_dir=output_dir,
            token=token,
            include_forks=args.include_forks,
            include_private=args.include_private,
        )
    except requests.HTTPError as exc:
        print(f"GitHub API error: {exc}", file=sys.stderr)
        if exc.response is not None:
            print(exc.response.text, file=sys.stderr)
        return 1

    print(
        f"\nDone. Removed: {removed}, saved: {saved}, "
        f"skipped: {skipped}, failed: {failed}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
