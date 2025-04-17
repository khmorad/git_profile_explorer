from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
from functools import lru_cache

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
    if request.method == 'POST':
        username = request.form['username']
        
        # Fetch actual user data from GitHub (optional – your current data is placeholder)
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
                "public_repos": user_info.get("public_repos")
            }
            languages = dict(list(getUserTechStack(username).items())[:5])
            repos = show_users_repo_names(username)
        else:
            user_data = {"username": username, "name": "Not Found"}
            repos = []

    return render_template('dashboard.html', user_data=user_data, languages=languages, repos=repos)

if __name__ == '__main__':
    app.run(debug=True)
