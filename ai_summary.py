import openai
import os
import traceback
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
