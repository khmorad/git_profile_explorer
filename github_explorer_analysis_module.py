import requests as r
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
import datetime
import os
import seaborn as sns

repo_url = "https://api.github.com/"
token = os.getenv("git_hub_project")

def get_function(repo_url):
    response = r.request(
        url=repo_url,
        method="GET",
        headers={
            'Authorization': token,
            # 'page_limit': '100'
        })
    html = response.json()
    if html is not None:
        return html
    else:
        return None


# User profile
def get_user_metadata(username):
    url = repo_url + "users/" + username
    metadata_list = ['bio', 'location', 'email', 'blog', 'twitter_username', 'company', 'hireable']
    data = get_function(url)
    profile_result = {}
    for metadata in metadata_list:
        profile_result[metadata] = 1 if data[metadata] != '' else 0
    return profile_result


def get_all_repo_metadata(username):
    url = repo_url + "users/" + username + '/repos'
    data = get_function(url)
    # recently_updated_repo_count = count_recently_updated_repo(data)
    return data


def count_recently_updated_repo(data: list):
    recent_range = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30) # Mark recent as 30 days range
    count = 0
    for repo in data:
        # Count number of date time
        if pd.to_datetime(repo['updated_at'], utc=True) > recent_range:
            count += 1
    return count


def get_top_5_language(language_series: pd.Series):
    all = language_series.sum().sort_values(ascending=False)
    return all[:5].index.tolist()


def plot_language_time_series(values, keys, username):
    language_data_plot = pd.DataFrame(values, index=keys)
    language_data_plot = np.log(language_data_plot)
    top_5 = get_top_5_language(language_data_plot)
    language_data_plot = pd.DataFrame(language_data_plot, columns=top_5, index=keys)
    fig = plt.figure(figsize=(10, 5))
    sns.lineplot(data=language_data_plot, legend=False, dashes=False)
    sns.scatterplot(
        data=language_data_plot,
    )
    plt.legend(loc='best', bbox_to_anchor=(1, 0.5), title='Top 5 Languages')
    plt.title(f"Top 5 Languages over time of {username}")
    plt.tight_layout()
    return fig


def language_proficiency(language_url):
    language_dict = {}
    languages = get_function(language_url)
    for language in languages:
        if language not in language_dict:
            language_dict[language] = languages[language]
        else:
            language_dict[language] += languages[language]
    if len(language_dict) == 0:
        return None
    return language_dict

def get_repo_metadata(username):
    repo_data = get_all_repo_metadata(username)
    df = pd.DataFrame(repo_data, columns=['name', 'description', 'branches_url', 'languages_url', 'stargazers_count',
                                          'watchers_count', 'forks', 'created_at', 'updated_at'])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.set_index("created_at")
    df['language'] = df['languages_url'].apply(language_proficiency)

    #Plot top 5 languages change overtime
    values = df['language'].dropna().tolist()
    keys = df['language'].dropna().index.tolist()
    top_5_plot = plot_language_time_series(values, keys, username)
    top_5_plot.show()

    #Count recently updated repo (30 days)
    recently_updated_count = count_recently_updated_repo(df['updated_at'].tolist())