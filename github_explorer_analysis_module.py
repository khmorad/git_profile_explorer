import requests as r
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
import datetime
import os
from functools import lru_cache
from flask import session
from dotenv import load_dotenv

load_dotenv('.env')
repo_url = "https://api.github.com/"
token = os.getenv("git_hub_project")


@lru_cache(maxsize=64)
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


@lru_cache(maxsize=64)
# User profile
def get_profile_score(username):
    url = repo_url + "users/" + username
    metadata_list = ['bio', 'location', 'email', 'blog', 'twitter_username', 'company', 'hireable']
    data = get_function(url)
    profile_result = {}
    for metadata in metadata_list:
        profile_result[metadata] = 1 if data[metadata] != '' else 0
    return profile_result


@lru_cache(maxsize=64)
def get_all_repo_metadata(username):
    url = repo_url + "users/" + username + '/repos'
    data = get_function(url)
    # recently_updated_repo_count = count_recently_updated_repo(data)
    return data


def count_recently_updated_repo(data: list):
    recent_range = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=30)  # Mark recent as 30 days range
    count = 0
    for repo in data:
        # Count number of date time
        if pd.to_datetime(repo['updated_at'], utc=True) > recent_range:
            count += 1
    return count


def get_top_5_language(language_series: pd.Series):
    all = language_series.sum().sort_values(ascending=False)
    return all[:5].index.tolist()


def get_language_time_series(values, keys):
    language_data_plot = pd.DataFrame(values, index=keys)
    language_data_plot = np.log(language_data_plot)
    top_5 = get_top_5_language(language_data_plot)
    language_data_plot = pd.DataFrame(language_data_plot, columns=top_5, index=keys)
    # fig = plt.figure(figsize=(10, 5))
    # sns.lineplot(data=language_data_plot, legend=False, dashes=False)
    # sns.scatterplot(
    #     data=language_data_plot,
    # )
    # plt.legend(loc='best', bbox_to_anchor=(1, 0.5), title='Top 5 Languages')
    # plt.title(f"Top 5 Languages over time of {username}")
    # plt.tight_layout()
    return language_data_plot


@lru_cache(maxsize=256)
def get_language_data(url):
    return get_function(url)

def language_proficiency(language_url):
    language_dict = {}
    languages = get_language_data(language_url)
    for language in languages:
        if language not in language_dict:
            language_dict[language] = languages[language]
        else:
            language_dict[language] += languages[language]
    if len(language_dict) == 0:
        return None
    return language_dict


def get_repo_analysis_data(username):
    repo_data = get_all_repo_metadata(username)
    df = pd.DataFrame(repo_data, columns=['name', 'description', 'branches_url', 'languages_url', 'stargazers_count',
                                          'watchers_count', 'forks', 'created_at', 'updated_at'])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.set_index("created_at")
    one_year_ago = pd.Timestamp.today(tz='UTC') - pd.DateOffset(years=1)
    df = df[df.index >= one_year_ago]
    df['language'] = df['languages_url'].apply(language_proficiency)

    # Top 5 languages change overtime
    values = df['language'].dropna().tolist()
    keys = df['language'].dropna().index.tolist()
    time_series_data = get_language_time_series(values, keys)
    time_series_data.sort_index(inplace=True, ascending=True)
    # Convert index to ISO 8601 time format suitable for Chart.js
    time_series_data.index = time_series_data.index.strftime('%Y-%m-%d')
    time_series_data.reset_index(inplace=True)

    # print(time_series_data)

    # Count recently updated repo (30 days)
    # recently_updated_count = count_recently_updated_repo(df['updated_at'].tolist())
    output_dict = {}
    for col in time_series_data.columns:
        output_dict[col] = time_series_data[col].tolist()
    return output_dict
