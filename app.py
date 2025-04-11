from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    user_data = None
    languages = None

    if request.method == 'POST':
        username = request.form['username']
        
        # Simulated data; replace this with GitHub API calls later
        user_data = {
            "username": username,
            "name": "John Doe",
            "bio": "Full Stack Developer",
            "location": "San Francisco",
            "public_repos": 42
        }
        languages = {
            "Python": 12,
            "JavaScript": 7,
            "HTML": 4,
            "Java": 3
        }
    return render_template('dashboard.html', user_data=user_data, languages=languages)

if __name__ == '__main__':
    app.run(debug=True)
