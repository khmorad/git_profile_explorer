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
    print(requests.get("https://api.github.com/users/khmorad"))
    github_response_repo = requests.get(repo_url, headers=headers)
    github_response_repo = github_response_repo.json()
    
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
    repos_response = requests.get(repos_url, headers=headers)
    repos = repos_response.json()

    monthly_commits = {}
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)

    for repo in repos:
        commits_url = f"https://api.github.com/repos/{username}/{repo['name']}/commits?since={one_year_ago.isoformat()}"
        while commits_url:
            commits_response = requests.get(commits_url, headers=headers)
            if commits_response.status_code == 200:
                commits = commits_response.json()
                for commit_data in commits:
                    commit_date = datetime.strptime(commit_data['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                    if commit_date >= one_year_ago:
                        month_year = commit_date.strftime('%Y-%m')
                        monthly_commits[month_year] = monthly_commits.get(month_year, 0) + 1
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
            else:
                print(f"Error fetching commits for {repo['name']}: {commits_response.status_code}")
                commits_url = None
                break  

    sorted_monthly_commits = dict(sorted(monthly_commits.items()))
    return sorted_monthly_commits

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
    monthly_commits = None
    if request.method == 'POST':
        username = request.form['username']
        
        
        user_info_url = f"https://api.github.com/users/{username}"
        headers = {"Authorization": token}
        user_info_response = requests.get(user_info_url, headers=headers)
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            user_data = {
                "username": user_info.get("login"),
                "name": user_info.get("name"),
                "bio": user_info.get("bio"),
                "location": user_info.get("location"),
                "public_repos": user_info.get("public_repos"),
                "porfile_pic": user_info.get("avatar_url")
            }
            languages = dict(list(getUserTechStack(username).items())[:5])
            repos = show_users_repo_names(username)
            monthly_commits = get_monthly_commits(username)

        else:
            user_data = {"username": username, "name": "Not Found"}
            repos = []

    return render_template('dashboard.html', user_data=user_data, languages=languages, repos=repos,  monthly_commits=monthly_commits)

if __name__ == '__main__':
    app.run(debug=True)