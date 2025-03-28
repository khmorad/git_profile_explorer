# GitHub Profile Explorer

## Authors

- Author #1: Yar Moradpour
- Author #2: Eddie Nguyen

## Project Description

### 📘 Project Description

**GitHub Profile Explorer** built with Python gives users access to detailed information for visible GitHub profiles through visual presentations. Through its usage of the official [GitHub REST API](https://docs.github.com/en/rest) this application gains access to retrieve essential data which includes user profile information and public repository details. The application enhances user experience by utilizing web scraping methods to gather additional information which the API fails to disclose such as pinned repositories and contribution graphs alongside recent public profiles events.

The application presents this data in a clean, responsive layout through a Flask-powered web interface. Users can search for any GitHub username, view the profile's avatar, name, bio, location, and GitHub statistics, and explore a list of public repositories with options to:

- Sort by stars or last update date
- Filter by language or repository name

Web-scraped content like contribution graphs and activity feeds offers further insight into the user’s coding behavior and public involvement

## Project Outline / Plan

- Use Flask to build a simple web interface for input and output display.
- Fetch public GitHub user data using the GitHub REST API.
- Scrape additional details such as the contribution graph and pinned repositories.
- Display user profile info and repositories with sorting/filtering options.
- Build modular Python scripts to handle API calls, scraping, and template rendering.

## Interface Plan

The application uses Flask to provide a clean and responsive web interface. It includes:

- A homepage with an input field for entering a GitHub username
- A search button to trigger data retrieval
- A results page that displays:
  - User profile information (avatar, name, bio, etc.)
  - Public repositories with sort and filter options
  - Scraped data such as contribution graph and recent activity
- All dynamic content is rendered using Jinja2 templates

## Data Collection and Storage Plan

GitHub user data is collected from the GitHub REST API using the `requests` library in Python. Additional data not exposed by the API (e.g., contribution graphs, pinned repositories) is obtained via web scraping using `BeautifulSoup`. No persistent storage is used in this project; all data is fetched in real-time per user request. Future plans may involve adding caching or local storage for performance optimization.

## Data Analysis and Visualization Plan

Data analysis includes sorting repositories by popularity (star count) and activity (last updated date). Repository languages and star distribution may also be summarized. Visualization components can include charts for top languages or activity over time, using libraries like `matplotlib` or `plotly`. The contribution graph, extracted from the user’s profile page, provides a visual summary of commit activity over the past year.

## Project Sprit Plan

| Sprint | Dates           | Task(s)                                                                                   | Status      |
| ------ | --------------- | ----------------------------------------------------------------------------------------- | ----------- |
| 1      | Mar 28 – Apr 3  | - Set up Flask project <br> - Create project structure <br> - Add .gitignore and LICENSE  | In progress |
| 2      | Apr 4 – Apr 10  | - Create homepage with input form <br> - Connect GitHub API and fetch user info           | Not started |
| 3      | Apr 11 – Apr 17 | - Display user profile (avatar, name, bio, stats) <br> - Fetch and list repositories      | Not started |
| 4      | Apr 18 – Apr 24 | - Add sorting/filtering for repositories <br> - Add repository cards to template          | Not started |
| 5      | Apr 25 – May 1  | - Implement web scraping for contribution graph and pinned repos                          | Not started |
| 6      | May 2 – May 8   | - Display scraped data (activity feed, graph) <br> - Refine UI and templates              | Not started |
| 7      | May 9 – May 15  | - Final testing and debugging <br> - Polish layout and responsiveness <br> - Write README | Not started |
