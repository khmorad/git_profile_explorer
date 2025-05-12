from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
import openai
from helpers import (
    get_recent_activity,
    get_open_issues_prs,
    getUserTechStack,
    get_monthly_commits,
    get_top_contributors,
    show_users_repo_names,
)
from functools import lru_cache

from ai_summary import generate_professional_summary

import github_explorer_analysis_module as analysis

load_dotenv()

token = os.getenv("git_hub_project")
openai.api_key = os.getenv("OPENAI_API_KEY")



app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    user_data = None
    languages = None
    repos = []
    top_contributors = []
    monthly_commits = None
    profession_summary = None
    followers = None
    following = None
    language_data = None
    recent_activity = []
    open_stats = {"issues": 0, "prs": 0}
    social_engagement = {} 
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
                "porfile_pic": user_info.get("avatar_url"),
                "followers": user_info.get("followers"),
                "following": user_info.get("following"),
                "blog": user_info.get("blog"),
                "linkedin": user_info.get("blog") if "linkedin.com" in str(user_info.get("blog")).lower() else None
            }
            followers = user_info.get("followers")
            following = user_info.get("following")
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
            try:
                recent_activity = get_recent_activity(username)
            except Exception as e:
                print(f"Error getting recent activity: {e}")
                recent_activity = []
            try:
                open_stats = get_open_issues_prs(username)
            except Exception as e:
                print(f"Error getting open issues/prs: {e}")
                open_stats = {"issues": 0, "prs": 0}
            try:
                language_data = analysis.get_repo_analysis_data(username)
            except Exception as e:
                print(f"Error while getting repo language analysis: {e}")
            try:
                social_engagement = analysis.get_user_social_engagement_metadata(username)
            except Exception as e:
                print(f"Error getting social engagement metadata: {e}")
                social_engagement = {}
        except Exception as e:
            print(f"Error fetching user info for {username}: {e}")
            user_data = {"username": username, "name": "Not Found"}
            repos = []

    return render_template(
        'dashboard.html',
        user_data=user_data,
        languages=languages,
        repos=repos,
        monthly_commits=monthly_commits,
        top_contributors=top_contributors,
        profession_summary=profession_summary,
        followers=followers,
        following=following,
        recent_activity=recent_activity,
        open_stats=open_stats,
        language_data=language_data,
        social_engagement=social_engagement
    )
from flask import jsonify


@lru_cache(maxsize=256)
@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"summary": "No username provided."}), 400

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
            "porfile_pic": user_info.get("avatar_url"),
            "followers": user_info.get("followers"),
            "following": user_info.get("following"),
            "blog": user_info.get("blog"),
        }

        repos = show_users_repo_names(username)
        languages = dict(list(getUserTechStack(username).items())[:5])
        summary = generate_professional_summary(username, user_data, languages, repos)
        return jsonify({"summary": summary})
    except Exception as e:
        print(f"Error generating summary: {e}")
        return jsonify({"summary": "Summary unavailable."}), 500

if __name__ == '__main__':
    app.run(debug=True)
