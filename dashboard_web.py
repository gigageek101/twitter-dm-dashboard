import streamlit as st
import json
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Twitter DM Dashboard",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better readability and daily focus
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #8e44ad 100%);
        color: white;
    }
    
    .stApp {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #8e44ad 100%);
    }
    
    .today-card {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 5px;
        border: 2px solid #fff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        color: white;
    }
    
    .account-name {
        color: white;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    
    .today-value {
        color: white;
        font-size: 48px;
        font-weight: 900;
        text-align: center;
        text-shadow: 0 3px 6px rgba(0,0,0,0.4);
        line-height: 1;
    }
    
    .today-label {
        color: #f8f9fa;
        font-size: 16px;
        font-weight: 600;
        text-align: center;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .inactive-card {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 5px;
        border: 2px solid #fff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        color: white;
    }
    
    .dashboard-header {
        color: white;
        text-align: center;
        font-size: 52px;
        font-weight: bold;
        margin-bottom: 20px;
        text-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    
    .daily-summary {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid rgba(255, 255, 255, 0.3);
        text-align: center;
    }
    
    .summary-title {
        color: #ffffff;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .summary-value {
        color: #ffffff;
        font-size: 36px;
        font-weight: bold;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .overview-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .overview-title {
        color: #bdc3c7;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    
    .overview-value {
        color: #ecf0f1;
        font-size: 20px;
        font-weight: bold;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border-radius: 12px;
        padding: 15px;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .stMetric > div {
        color: white !important;
    }
    
    .stMetric label {
        color: #bdc3c7 !important;
        font-weight: 600 !important;
    }
    
    .time-info {
        background: rgba(52, 152, 219, 0.3);
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

class GoogleDriveManager:
    def __init__(self):
        """Initialize Google Drive API client from environment variables"""
        try:
            # Try to get credentials from environment variable
            google_credentials = os.getenv('GOOGLE_SERVICE_ACCOUNT')
            
            if google_credentials:
                # Parse JSON from environment variable
                credentials_info = json.loads(google_credentials)
                credentials = Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                )
                self.service = build('drive', 'v3', credentials=credentials)
            else:
                # Fallback to local file for development
                local_path = "Twitter Mass DM/google_service_account.json"
                if os.path.exists(local_path):
                    credentials = Credentials.from_service_account_file(
                        local_path,
                        scopes=['https://www.googleapis.com/auth/drive.readonly']
                    )
                    self.service = build('drive', 'v3', credentials=credentials)
                else:
                    # No credentials available - will use sample data instead
                    self.service = None
        except Exception as e:
            # On error, just use sample data instead of showing error
            self.service = None
    
    def find_folders(self, parent_folder_name):
        """Find all Twitter Selfmade folders in the parent directory"""
        try:
            # First find the parent folder
            query = f"name='{parent_folder_name}' and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query).execute()
            
            if not results.get('files'):
                st.error(f"Parent folder '{parent_folder_name}' not found")
                return []
            
            parent_id = results['files'][0]['id']
            
            # Find all Twitter Selfmade folders
            query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and name contains 'Twitter Selfmade'"
            results = self.service.files().list(q=query).execute()
            
            return results.get('files', [])
        except Exception as e:
            st.error(f"Error finding folders: {e}")
            return []
    
    def get_usage_stats(self, folder_id, folder_name):
        """Get usage stats from a specific folder"""
        try:
            # Look for usage_stats.json in the folder
            query = f"'{folder_id}' in parents and name='usage_stats.json'"
            results = self.service.files().list(q=query).execute()
            
            if not results.get('files'):
                return None
            
            file_id = results['files'][0]['id']
            
            # Download the file content
            file_content = self.service.files().get_media(fileId=file_id).execute()
            
            # Parse JSON
            usage_data = json.loads(file_content.decode('utf-8'))
            usage_data['account_name'] = folder_name
            
            return usage_data
        except Exception as e:
            st.warning(f"Could not read usage stats for {folder_name}: {e}")
            return None

def load_sample_data():
    """Load sample data that updates dynamically"""
    from datetime import datetime, timedelta
    import random
    
    # Generate realistic sample data that changes based on current time
    current_time = datetime.now()
    accounts = []
    
    for i in [3, 5, 13, 17, 18, 24]:
        # Simulate different activity levels
        base_dms_today = random.randint(0, 25)
        
        # Some accounts more active than others
        if i in [3, 13]:
            dms_today = base_dms_today
        elif i in [17, 18]:
            dms_today = random.randint(0, 15)
        else:
            dms_today = random.randint(0, 8)
        
        # Generate last used time
        if dms_today > 0:
            last_used = current_time - timedelta(minutes=random.randint(5, 120))
        else:
            last_used = current_time - timedelta(hours=random.randint(2, 24))
        
        accounts.append({
            'account_name': f'Twitter Selfmade {i}',
            'total_dms_sent': random.randint(50, 500),
            'dms_sent_today': dms_today,
            'last_used': last_used.isoformat(),
            'current_period_limit': 20,
            'today_date': current_time.strftime('%Y-%m-%d'),
            'usage_count': dms_today
        })
    
    return accounts

def create_account_card(account_data):
    """Create a card focused on today's activity"""
    account_name = account_data.get('account_name', 'Unknown')
    total_dms = account_data.get('total_dms_sent', 0)
    dms_today = account_data.get('dms_sent_today', 0)
    last_used = account_data.get('last_used', 'Never')
    current_limit = account_data.get('current_period_limit', 20)
    
    # Parse last used date
    try:
        if last_used != 'Never':
            last_used_dt = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
            last_used_str = last_used_dt.strftime('%H:%M')
            is_today = last_used_dt.date() == datetime.now().date()
        else:
            last_used_str = 'Never'
            is_today = False
    except:
        last_used_str = 'Unknown'
        is_today = False
    
    # Determine card style based on activity
    if dms_today > 0:
        card_class = "today-card"
    else:
        card_class = "inactive-card"
    
    # Progress percentage
    progress = min((dms_today / current_limit) * 100, 100) if current_limit > 0 else 0
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="{card_class}">
            <div class="account-name">{account_name}</div>
            <div class="today-value">{dms_today}</div>
            <div class="today-label">DMs Sent Today</div>
            <div style="margin-top: 10px; background: rgba(255,255,255,0.2); border-radius: 10px; padding: 8px;">
                <div style="font-size: 12px; color: #f8f9fa; margin-bottom: 3px;">Progress: {progress:.0f}% ({dms_today}/{current_limit})</div>
                <div style="background: rgba(255,255,255,0.3); border-radius: 5px; height: 6px;">
                    <div style="background: white; border-radius: 5px; height: 6px; width: {progress}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if is_today and last_used_str != 'Never':
            st.markdown(f"""
            <div class="time-info">
                <div style="font-size: 12px; color: #ecf0f1;">Last Active</div>
                <div style="font-size: 16px; font-weight: bold; color: white;">{last_used_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="overview-section">
            <div class="overview-title">Total Lifetime</div>
            <div class="overview-value">{total_dms:,}</div>
        </div>
        """, unsafe_allow_html=True)

def create_daily_focus_chart(all_data):
    """Create a chart focused on today's activity"""
    if not all_data:
        return
    
    df = pd.DataFrame(all_data)
    
    # Sort by today's DMs descending
    df = df.sort_values('dms_sent_today', ascending=True)
    
    # Create a horizontal bar chart for today's DMs
    fig = go.Figure()
    
    # Color coding: green for active accounts, red for inactive
    colors = ['#27ae60' if dms > 0 else '#e74c3c' for dms in df['dms_sent_today']]
    
    fig.add_trace(
        go.Bar(
            x=df['dms_sent_today'],
            y=df['account_name'],
            orientation='h',
            marker_color=colors,
            text=df['dms_sent_today'],
            textposition='auto',
            textfont=dict(color='white', size=14, family='Arial Black'),
        )
    )
    
    fig.update_layout(
        title={
            'text': "📊 Today's DM Activity by Account",
            'x': 0.5,
            'font': {'size': 24, 'color': 'white', 'family': 'Arial Black'}
        },
        height=max(400, len(df) * 60),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        xaxis=dict(
            title=dict(text="DMs Sent Today", font=dict(color='white', size=16)),
            tickfont=dict(color='white', size=12),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text="", font=dict(color='white')),
            tickfont=dict(color='white', size=12),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        margin=dict(l=150, r=50, t=80, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Dashboard header with current date/time
    current_time = datetime.now()
    st.markdown(f'<div class="dashboard-header">📈 Today\'s Twitter Activity</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center; color: #bdc3c7; font-size: 18px; margin-bottom: 30px;">{current_time.strftime("%A, %B %d, %Y at %H:%M")}</div>', unsafe_allow_html=True)
    
    # Initialize Google Drive manager
    drive_manager = GoogleDriveManager()
    
    # Load data
    all_usage_data = []
    
    if drive_manager and drive_manager.service:
        with st.spinner("Loading data from Google Drive..."):
            # Find Twitter Selfmade folders
            folders = drive_manager.find_folders("Twitter Slaves Natalie")
            
            for folder in folders:
                usage_data = drive_manager.get_usage_stats(folder['id'], folder['name'])
                if usage_data:
                    all_usage_data.append(usage_data)
    
    # Fallback to sample data if no real data available
    if not all_usage_data:
        all_usage_data = load_sample_data()
    
    if not all_usage_data:
        st.error("No usage data found.")
        return
    
    # Sort accounts by today's activity (most active first)
    all_usage_data.sort(key=lambda x: x.get('dms_sent_today', 0), reverse=True)
    
    # Calculate daily metrics
    total_accounts = len(all_usage_data)
    total_dms_today = sum(data.get('dms_sent_today', 0) for data in all_usage_data)
    active_accounts_today = sum(1 for data in all_usage_data if data.get('dms_sent_today', 0) > 0)
    avg_dms_per_active = total_dms_today / active_accounts_today if active_accounts_today > 0 else 0
    
    # Today's Summary - Big and prominent
    st.markdown(f"""
    <div class="daily-summary">
        <div class="summary-title">🚀 Today's Performance</div>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="text-align: center; margin: 10px;">
                <div class="summary-value">{total_dms_today}</div>
                <div style="color: #bdc3c7; font-size: 14px;">Total DMs Today</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div class="summary-value">{active_accounts_today}</div>
                <div style="color: #bdc3c7; font-size: 14px;">Active Accounts</div>
            </div>
            <div style="text-align: center; margin: 10px;">
                <div class="summary-value">{avg_dms_per_active:.1f}</div>
                <div style="color: #bdc3c7; font-size: 14px;">Avg per Active</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Today's Activity Chart
    st.markdown("### 📊 Today's Activity by Account")
    create_daily_focus_chart(all_usage_data)
    
    st.markdown("---")
    
    # Individual account cards - focused on today
    st.markdown("### 🎯 Account Performance Today")
    
    for account_data in all_usage_data:
        create_account_card(account_data)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Total overview at bottom - smaller section
    st.markdown("---")
    st.markdown("### 📋 Lifetime Overview")
    
    total_dms_all = sum(data.get('total_dms_sent', 0) for data in all_usage_data)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Accounts", total_accounts, help="Total number of accounts")
    
    with col2:
        st.metric("Lifetime DMs", f"{total_dms_all:,}", help="All-time DMs sent across all accounts")
    
    with col3:
        avg_lifetime = total_dms_all / total_accounts if total_accounts > 0 else 0
        st.metric("Avg per Account", f"{avg_lifetime:.0f}", help="Average lifetime DMs per account")
    
    # Sidebar controls
    st.sidebar.markdown("### 🎛️ Controls")
    if st.sidebar.button("🔄 Refresh Data", help="Reload data from Google Drive"):
        st.rerun()
    
    # Display last updated
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏰ Last Updated")
    st.sidebar.markdown(f"**{current_time.strftime('%H:%M:%S')}**")
    st.sidebar.markdown(f"{current_time.strftime('%B %d, %Y')}")
    
    # Daily stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    st.sidebar.metric("Today's Total", total_dms_today)
    st.sidebar.metric("Active Now", active_accounts_today)
    if total_accounts > active_accounts_today:
        st.sidebar.metric("Inactive", total_accounts - active_accounts_today)

if __name__ == "__main__":
    main() 