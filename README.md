# HireLens
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, clean Streamlit UI for a recruitment & talent platform.

## Features
- Interactive dashboard for recruitment tracking
- Integration with Google APIs
- Candidate and Talent management views

## Prerequisites
- Python 3.8+
- [Streamlit](https://streamlit.io/)

## Installation

1. Clone the repository and navigate into the project directory:
   ```bash
   git clone <repository-url>
   cd hirelens
   ```

2. Create a virtual environment and activate it (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

This application uses Google APIs. You must provide a `credentials.json` file in the root directory.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the relevant APIs for your project.
4. Go to **APIs & Services > Credentials** and create an **OAuth client ID** (Application type: Desktop App).
5. Download the JSON file, rename it to `credentials.json`, and place it in the root folder of this project.

*Note: On your first run, a browser window will open to authenticate your Google account, and a `token.json` file will be generated automatically to save your session.*

## Usage

Run the Streamlit app:
```bash
streamlit run main.py
```

## Demo Credentials
For testing purposes, the application accepts the following default credentials (unless overridden via Streamlit secrets):
- Admin: `admin` / `admin123`
- Candidate: `candidate` / `candidate123`

