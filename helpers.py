from functools import lru_cache
from datetime import datetime, timedelta
import requests
import os
import openai
import traceback
from dotenv import load_dotenv
from flask import session

load_dotenv('key.env')
openai.api_key = os.getenv("OPENAI_API_KEY")
headers = {"Authorization": f'token {os.getenv('git_hub_project')}'}

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
    repos_url = f"https://api.github.com/users/{username}/repos"
    try:
        repos = requests.get(repos_url, headers=headers).json()
        total_issues = 0
        total_prs = 0
        for repo in repos:
            repo_name = repo['name']
            issues_url = f"https://api.github.com/repos/{username}/{repo_name}/issues?state=open"
            issues = requests.get(issues_url, headers=headers).json()
            for issue in issues:
                if 'pull_request' in issue:
                    total_prs += 1
                else:
                    total_issues += 1
        return {"issues": total_issues, "prs": total_prs}
    except Exception as e:
        print(f"Error fetching issues/PRs: {e}")
        return {"issues": 0, "prs": 0}

def generate_professional_summary(username, user_data, languages, repos):
    if not any([user_data.get('name'), user_data.get('bio'), languages]):
        return "Insufficient data to generate professional summary."
    top_languages_str = ', '.join(languages.keys()) if languages else 'Not detected'
    repo_count = len(repos)
    prompt = f"""
    Analyze this GitHub user's profile and identify their likely primary profession or area of expertise in 1-2 concise sentences. Focus on the skills and potential roles suggested by their profile information.
    GitHub Profile:
    - Username: {username}
    - Name: {user_data.get('name', 'Not provided')}
    - Bio: {user_data.get('bio', 'Not provided')}
    - Top Languages: {top_languages_str}
    - Number of Public Repositories: {repo_count}
    Likely Profession/Expertise:
    """
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.6,
        )
        summary = response.choices[0].message.content.strip()
        return summary if summary else "Could not generate summary."
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return f"Error with OpenAI API: {e}"
    except Exception as e:
        print(f"Unexpected error during summary generation: {e}")
        traceback.print_exc()
        return "Could not generate professional summary due to an unexpected error."

@lru_cache(maxsize=128)
def getUserTechStack(username):
    repo_url = f"https://api.github.com/users/{username}/repos"
    try:
        github_response_repo = requests.get(repo_url, headers=headers)
        github_response_repo = github_response_repo.json()
    except Exception as e:
        print(f"Error fetching repos for {username}: {e}")
        return {}
    github_repo_languages = []
    for repo in github_response_repo:
        github_repo_languages.append(requests.get(repo['languages_url'], headers=headers).json())
    langs = {}
    for info in github_repo_languages:
        for lang, lines in info.items():
            if lang in langs:
                langs[lang].append(lines)
            else:
                langs[lang] = [lines]
    for key, values in langs.items():
        langs[key] = sum(values)
    sorted_langs = dict(sorted(langs.items(), key=lambda item: item[1], reverse=True))
    return sorted_langs

@lru_cache(maxsize=128)
def get_monthly_commits(username):
    repos_url = f"https://api.github.com/users/{username}/repos"
    try:
        repos_response = requests.get(repos_url, headers=headers)
        repos_response.raise_for_status()
        repos = repos_response.json()
    except Exception as e:
        print(f"Error fetching repositories for commits: {e}")
        return {}
    monthly_commits = {}
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    for repo in repos:
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
                        month_year = commit_date.strftime('%Y-%m')
                        monthly_commits[month_year] = monthly_commits.get(month_year, 0) + 1
                except Exception as e:
                    print(f"Error parsing commit date: {e}")
                    continue
            try:
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
            except Exception as e:
                print(f"Error handling pagination for {repo['name']}: {e}")
                break
    sorted_monthly_commits = dict(sorted(monthly_commits.items()))
    return sorted_monthly_commits

@lru_cache(maxsize=128)
def get_top_contributors(username, max_contributors=5):
    repo_url = f"https://api.github.com/users/{username}/repos"
    try:
        repos_response = requests.get(repo_url, headers=headers)
        repos_response.raise_for_status()
        repos = repos_response.json()
    except Exception as e:
        print(f"Error fetching repos for contributors: {e}")
        return []
    contributor_counts = {}
    for repo in repos:
        contributors_url = f"https://api.github.com/repos/{username}/{repo['name']}/contributors"
        try:
            contributors_response = requests.get(contributors_url, headers=headers)
            contributors_response.raise_for_status()
            contributors = contributors_response.json()
            for contributor in contributors:
                login = contributor["login"]
                contributions = contributor["contributions"]
                contributor_counts[login] = contributor_counts.get(login, 0) + contributions
        except Exception as e:
            print(f"Error fetching contributors for {repo['name']}: {e}")
            continue
    sorted_contributors = sorted(contributor_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_contributors[:max_contributors]

@lru_cache(maxsize=128)
def show_users_repo_names(user):
    repourl = f"https://api.github.com/users/{user}/repos"
    response = requests.get(repourl, headers=headers)
    github_rep_response = response.json()
    repo_names = []
    for repo in github_rep_response:
        repo_names.append(repo['name'])
    return repo_names