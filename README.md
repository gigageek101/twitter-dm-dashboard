# Twitter DM Dashboard

A beautiful dashboard to monitor DM statistics across your Twitter accounts with real-time Google Drive integration.

## Features

- 📊 **Real-time Statistics**: View total DMs sent and today's DMs for each account
- 🎨 **Beautiful UI**: Blue-purple gradient design with glassmorphism effects
- ☁️ **Google Drive Integration**: Automatically reads usage_stats.json files from Google Drive
- 📈 **Analytics Charts**: Visual representation of DM performance across accounts
- 🔄 **Auto-refresh**: Real-time data updates
- 📱 **Responsive Design**: Works on desktop and mobile

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google Drive Setup
The dashboard uses your existing Google service account credentials from:
`Twitter Mass DM/google_service_account.json`

Make sure this file has access to your Google Drive folders.

### 3. Folder Structure
The dashboard looks for usage_stats.json files in:
```
G:/My Drive/Reddit Exchange/Twitter Slaves Natalie/
├── Twitter Selfmade 3/
│   └── usage_stats.json
├── Twitter Selfmade 13/
│   └── usage_stats.json
├── Twitter Selfmade 17/
│   └── usage_stats.json
└── ...
```

## Usage

### Option 1: First Time Setup (Windows)
```bash
run_dashboard.bat
```
This will install all dependencies and start the dashboard.

### Option 2: Quick Start (After First Setup)
```bash
start_dashboard.bat
```
This just starts the dashboard without reinstalling dependencies.

### Option 3: Manual Command
```bash
streamlit run dashboard.py
```

**Important:** Always use `streamlit run` command, NOT `python dashboard.py`

The dashboard will automatically open in your default browser at `http://localhost:8501`

### Troubleshooting Common Issues

1. **"Missing ScriptRunContext" warnings**: These are normal and can be ignored
2. **ModuleNotFoundError**: Run `run_dashboard.bat` to install missing dependencies
3. **Dashboard not opening**: Make sure you're using `streamlit run` not `python`
4. **Port already in use**: Close any existing dashboard instances or use `streamlit run dashboard.py --server.port 8502`

## Data Format

Each `usage_stats.json` file should contain:
```json
{
  "today_date": "2025-08-19",
  "last_used": "2025-08-25T01:15:46.745110",
  "dms_sent_today": 17,
  "total_dms_sent": 320,
  "last_reset": "2025-08-25T01:00:49.313538",
  "current_period": "2025-08-25 01",
  "current_period_limit": 20,
  "usage_count": 12
}
```

## Dashboard Sections

- **Summary**: Overview of all accounts (total accounts, total DMs, today's DMs)
- **Analytics**: Bar charts showing DM performance across accounts
- **Account Details**: Individual cards for each account with detailed stats

## Troubleshooting

1. **No data found**: Check that your Google Drive paths are correct and the service account has access
2. **Google Drive errors**: Verify your service account credentials are valid
3. **Missing accounts**: Ensure usage_stats.json files exist in each account folder

## Auto-refresh

Use the "🔄 Refresh Data" button in the sidebar to reload data from Google Drive.

The dashboard shows the last updated timestamp in the sidebar. 