from functools import lru_cache
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("git_hub_project")
headers = {"Authorization": token}

@lru_cache(maxsize=128)
def get_user_repos(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching repos for {username}: {e}")
        return []

@lru_cache(maxsize=64)
def get_recent_activity(username, max_events=5):
    url = f"https://api.github.com/users/{username}/events/public"
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        events = resp.json()
        activity = []
        for event in events[:max_events]:
            evt_type = event.get("type")
            repo = event.get("repo", {}).get("name", "")
            created_at = event.get("created_at", "")
            activity.append({"type": evt_type, "repo": repo, "created_at": created_at})
        return activity
    except Exception as e:
        print(f"Error fetching recent activity: {e}")
        return []

@lru_cache(maxsize=64)
def get_open_issues_prs(username):
    repos = get_user_repos(username)
    total_issues = 0
    total_prs = 0
    for repo in repos:
        try:
            repo_name = repo['name']
            issues_url = f"https://api.github.com/repos/{username}/{repo_name}/issues?state=open"
            issues = requests.get(issues_url, headers=headers).json()
            for issue in issues:
                if 'pull_request' in issue:
                    total_prs += 1
                else:
                    total_issues += 1
        except Exception as e:
            print(f"Error fetching issues for {repo['name']}: {e}")
            continue
    return {"issues": total_issues, "prs": total_prs}

@lru_cache(maxsize=128)
def getUserTechStack(username):
    repos = get_user_repos(username)
    langs = {}
    for repo in repos:
        try:
            lang_url = repo['languages_url']
            lang_data = requests.get(lang_url, headers=headers).json()
            for lang, lines in lang_data.items():
                langs[lang] = langs.get(lang, 0) + lines
        except Exception as e:
            print(f"Error fetching languages for {repo['name']}: {e}")
            continue
    return dict(sorted(langs.items(), key=lambda item: item[1], reverse=True))

@lru_cache(maxsize=128)
def get_monthly_commits(username):
    repos = get_user_repos(username)
    monthly_commits = {}
    one_year_ago = datetime.now() - timedelta(days=365)
    for repo in repos:
        if repo.get("fork"):
            continue  # skip forked repos
        commits_url = f"https://api.github.com/repos/{username}/{repo['name']}/commits?since={one_year_ago.isoformat()}"
        while commits_url:
            try:
                commits_response = requests.get(commits_url, headers=headers)
                commits_response.raise_for_status()
                commits = commits_response.json()
            except Exception as e:
                print(f"Error fetching commits for {repo['name']}: {e}")
                break
            for commit_data in commits:
                try:
                    commit_date = datetime.strptime(commit_data['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                    if commit_date >= one_year_ago:
                        key = commit_date.strftime('%Y-%m')
                        monthly_commits[key] = monthly_commits.get(key, 0) + 1
                except Exception as e:
                    continue
            if 'Link' in commits_response.headers:
                links = commits_response.headers['Link'].split(',')
                next_link = None
                for link in links:
                    if 'rel="next"' in link:
                        next_link = link.split(';')[0].strip('<>')
                        break
                commits_url = next_link
            else:
                commits_url = None
    return dict(sorted(monthly_commits.items()))

@lru_cache(maxsize=128)
def get_top_contributors(username, max_contributors=5):
    repos = get_user_repos(username)
    contributor_counts = {}
    for repo in repos:
        try:
            url = f"https://api.github.com/repos/{username}/{repo['name']}/contributors"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            for contributor in response.json():
                login = contributor['login']
                contributions = contributor['contributions']
                contributor_counts[login] = contributor_counts.get(login, 0) + contributions
        except Exception as e:
            print(f"Error fetching contributors for {repo['name']}: {e}")
            continue
    return sorted(contributor_counts.items(), key=lambda x: x[1], reverse=True)[:max_contributors]

@lru_cache(maxsize=128)
def show_users_repo_names(username):
    repos = get_user_repos(username)
    return [repo['name'] for repo in repos]
