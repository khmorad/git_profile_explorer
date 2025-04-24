from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
from functools import lru_cache
from datetime import datetime, timedelta
load_dotenv()
token = os.getenv("git_hub_project")
print(token)

@lru_cache(maxsize=128)
def getUserTechStack(username):
    headers = {"Authorization": token}

    #url = f"https://api.github.com/users/{username}"
    repo_url = f"https://api.github.com/users/{username}/repos"
    # response = requests.get(url, headers=headers)
    
    #fetch users repo info
    try:
        github_response_repo = requests.get(repo_url, headers=headers)
        github_response_repo = github_response_repo.json()
    except Exception as e:
        print(f"Error fetching repos for {username}: {e}")
        return {}    
    #get language url through repo list
    github_repo_languages = [] 
    for repo in github_response_repo:
        github_repo_languages.append(requests.get(repo['languages_url'], headers=headers).json())
        
    # using the data fetch to create a language dictorary in decreasing order    
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
    headers = {"Authorization": token}
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
    headers = {"Authorization": token}
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
    headers = {"Authorization": token}
    repourl = f"https://api.github.com/users/{user}/repos"
    response = requests.get(repourl, headers=headers)
    github_rep_response = response.json()
    repo_names = []
    for repo in github_rep_response:
        repo_names.append(repo['name'])

    return repo_names  

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    user_data = None
    languages = None
    repos = []
    top_contributors = []
    monthly_commits = None

    if request.method == 'POST':
        username = request.form['username']
        user_info_url = f"https://api.github.com/users/{username}"
        headers = {"Authorization": token}

        try:
            user_info_response = requests.get(user_info_url, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            
            user_data = {
                "username": user_info.get("login"),
                "name": user_info.get("name"),
                "bio": user_info.get("bio"),
                "location": user_info.get("location"),
                "public_repos": user_info.get("public_repos"),
                "porfile_pic": user_info.get("avatar_url")
            }

            try:
                languages = dict(list(getUserTechStack(username).items())[:5])
            except Exception as e:
                print(f"Error getting user tech stack: {e}")
                languages = None

            try:
                repos = show_users_repo_names(username)
            except Exception as e:
                print(f"Error getting repo names: {e}")
                repos = []
            try:
                top_contributors = get_top_contributors(username)
            except Exception as e:
                print(f"Error fetching top contributors: {e}")
            try:
                monthly_commits = get_monthly_commits(username)
            except Exception as e:
                print(f"Error getting monthly commits: {e}")
                monthly_commits = None

        except Exception as e:
            print(f"Error fetching user info for {username}: {e}")
            user_data = {"username": username, "name": "Not Found"}
            repos = []

    return render_template('dashboard.html',user_data=user_data,languages=languages,repos=repos,
                           monthly_commits=monthly_commits, top_contributors=top_contributors)

if __name__ == '__main__':
    app.run(debug=True)