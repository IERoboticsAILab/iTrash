"""
Analytics dashboard for iTrash system.
Streamlit-based dashboard for data visualization and analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import db_manager
from config.settings import AnalyticsConfig

# Page configuration
st.set_page_config(
    page_title="iTrash Analytics Dashboard",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def initialize_database():
    """Initialize database connection"""
    if not db_manager.is_connected:
        success = db_manager.connect()
        if not success:
            st.error("Failed to connect to database. Please check your MongoDB connection.")
            return False
    return True

def get_overview_metrics():
    """Get overview metrics"""
    try:
        # Get total classifications
        total_data = db_manager.get_image_data(limit=10000)
        total_classifications = len(total_data)
        
        # Get today's classifications
        today = datetime.now().strftime("%Y-%m-%d")
        today_data = db_manager.get_image_data(limit=10000, date_filter=today)
        today_classifications = len(today_data)
        
        # Get classification stats
        stats = db_manager.get_classification_stats()
        
        # Get most common class
        most_common_class = max(stats.items(), key=lambda x: x[1])[0] if stats else "None"
        
        return {
            "total_classifications": total_classifications,
            "today_classifications": today_classifications,
            "most_common_class": most_common_class,
            "classification_stats": stats
        }
    except Exception as e:
        st.error(f"Error getting overview metrics: {e}")
        return None

def create_classification_chart(stats):
    """Create classification distribution chart"""
    if not stats:
        return None
    
    df = pd.DataFrame(list(stats.items()), columns=['Class', 'Count'])
    
    fig = px.pie(
        df, 
        values='Count', 
        names='Class',
        title='Trash Classification Distribution',
        color_discrete_map={
            'blue': '#1f77b4',
            'yellow': '#ff7f0e',
            'brown': '#8b4513'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_daily_trend_chart(days=7):
    """Create daily trend chart"""
    try:
        daily_stats = db_manager.get_daily_stats(days)
        
        if not daily_stats:
            return None
        
        # Prepare data for plotting
        dates = []
        totals = []
        blue_counts = []
        yellow_counts = []
        brown_counts = []
        
        for day_data in daily_stats:
            date = day_data['_id']
            total = day_data['total']
            dates.append(date)
            totals.append(total)
            
            # Extract class counts
            blue_count = 0
            yellow_count = 0
            brown_count = 0
            
            for class_data in day_data['classes']:
                if class_data['class'] == 'blue':
                    blue_count = class_data['count']
                elif class_data['class'] == 'yellow':
                    yellow_count = class_data['count']
                elif class_data['class'] == 'brown':
                    brown_count = class_data['count']
            
            blue_counts.append(blue_count)
            yellow_counts.append(yellow_count)
            brown_counts.append(brown_count)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Total': totals,
            'Blue': blue_counts,
            'Yellow': yellow_counts,
            'Brown': brown_counts
        })
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Blue',
            x=df['Date'],
            y=df['Blue'],
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            name='Yellow',
            x=df['Date'],
            y=df['Yellow'],
            marker_color='#ff7f0e'
        ))
        
        fig.add_trace(go.Bar(
            name='Brown',
            x=df['Date'],
            y=df['Brown'],
            marker_color='#8b4513'
        ))
        
        fig.update_layout(
            title='Daily Classification Trends',
            xaxis_title='Date',
            yaxis_title='Number of Classifications',
            barmode='stack'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating daily trend chart: {e}")
        return None

def create_hourly_analysis():
    """Create hourly analysis chart"""
    try:
        # Get recent data
        data = db_manager.get_image_data(limit=1000)
        
        if not data:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Extract hour from timestamp
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        
        # Group by hour
        hourly_stats = df.groupby('hour')['predicted_class'].value_counts().unstack(fill_value=0)
        
        # Create heatmap
        fig = px.imshow(
            hourly_stats.T,
            title='Hourly Classification Heatmap',
            labels=dict(x='Hour of Day', y='Class', color='Count'),
            aspect='auto'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating hourly analysis: {e}")
        return None

def export_data():
    """Export data functionality"""
    st.subheader("Data Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_date = st.date_input(
            "Select date for export (leave empty for all data)",
            value=None
        )
    
    with col2:
        if st.button("Export to CSV"):
            if export_date:
                date_str = export_date.strftime("%Y-%m-%d")
                filename = f"itrash_data_{date_str}.csv"
            else:
                filename = "itrash_data_all.csv"
            
            success = db_manager.export_to_csv(filename, date_filter=date_str if export_date else None)
            
            if success:
                st.success(f"Data exported to {filename}")
                
                # Provide download link
                with open(filename, 'r') as f:
                    st.download_button(
                        label="Download CSV",
                        data=f.read(),
                        file_name=filename,
                        mime="text/csv"
                    )
            else:
                st.error("Failed to export data")

def main():
    """Main dashboard function"""
    st.markdown('<h1 class="main-header">🗑️ iTrash Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize database
    if not initialize_database():
        st.stop()
    
    # Sidebar
    st.sidebar.title("Dashboard Controls")
    
    # Date range selector
    st.sidebar.subheader("Date Range")
    days_back = st.sidebar.slider("Days to analyze", 1, 30, 7)
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Overview metrics
    st.header("📊 Overview")
    
    metrics = get_overview_metrics()
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Classifications</h3>
                <h2>{metrics['total_classifications']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Today's Classifications</h3>
                <h2>{metrics['today_classifications']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Most Common Class</h3>
                <h2>{metrics['most_common_class'].title()}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total = sum(metrics['classification_stats'].values())
            accuracy = "N/A"
            if total > 0:
                accuracy = f"{total} items"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Items</h3>
                <h2>{accuracy}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts
    st.header("📈 Analytics")
    
    # Classification distribution
    st.subheader("Classification Distribution")
    if metrics and metrics['classification_stats']:
        fig = create_classification_chart(metrics['classification_stats'])
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Daily trends
    st.subheader("Daily Trends")
    daily_fig = create_daily_trend_chart(days_back)
    if daily_fig:
        st.plotly_chart(daily_fig, use_container_width=True)
    
    # Hourly analysis
    st.subheader("Hourly Analysis")
    hourly_fig = create_hourly_analysis()
    if hourly_fig:
        st.plotly_chart(hourly_fig, use_container_width=True)
    
    # Data export
    st.header("📤 Data Export")
    export_data()
    
    # System status
    st.header("🔧 System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Database Status")
        if db_manager.is_connected:
            st.success("✅ Connected to MongoDB")
        else:
            st.error("❌ Not connected to MongoDB")
    
    with col2:
        st.subheader("Recent Activity")
        recent_data = db_manager.get_image_data(limit=5)
        if recent_data:
            for item in recent_data:
                st.text(f"{item.get('date', 'N/A')} {item.get('time', 'N/A')} - {item.get('predicted_class', 'N/A')}")
        else:
            st.text("No recent activity")

if __name__ == "__main__":
    main() 