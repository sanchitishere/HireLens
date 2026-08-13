<div align="center">
  <h1>🧭 HireLens</h1>
  <p><strong>Intelligent Talent & Recruitment Platform</strong></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
  [![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
</div>

<hr>

Welcome to **HireLens**! A beautifully designed, simple, and clean Streamlit application that streamlines your recruitment tracking and talent management.

## ✨ Features

- **📊 Interactive Dashboard:** Track recruitment metrics with beautiful visualizations.
- **☁️ Google API Integration:** Seamless connectivity for data management.
- **🧑‍💼 Talent & Candidate Views:** Dedicated interfaces for both HR managers and candidates.
- **🔒 Secure Authentication:** Role-based login and access control.

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- **Python 3.8** or higher
- **Streamlit**

### 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sanchitishere/HireLens.git
   cd HireLens
   ```

2. **Create a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration (Google API)

This application uses Google APIs. You must provide a `credentials.json` file in the root directory to make it work!

1. Head over to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the relevant APIs for your project.
4. Navigate to **APIs & Services > Credentials** and create an **OAuth client ID** (Application type: *Desktop App*).
5. Download the JSON file, rename it to `credentials.json`, and place it in the root folder of this project.

> 💡 *Note: On your first run, a browser window will automatically open to authenticate your Google account, and a `token.json` file will be generated to save your session.*

---

## 💻 Usage

Ready to go? Run the Streamlit app:
```bash
streamlit run main.py
```

### 🔑 Demo Credentials
For testing purposes, the application accepts the following default credentials (unless overridden via Streamlit secrets):

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin / HR** | `admin` | `admin123` |
| **Candidate** | `candidate` | `candidate123` |

---

<div align="center">
  <i>Built with ❤️ using Streamlit</i>
</div>
