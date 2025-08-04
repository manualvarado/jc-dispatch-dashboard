# JC Dispatch Operational & Performance Dashboard

A comprehensive Streamlit dashboard for analyzing JC Freight operations, driver performance, and market insights.

## 🚀 Live Dashboard

**Production Dashboard:** https://jc-freight-dashboard.streamlit.app/  
**New Dispatch Dashboard:** [Coming Soon - Deploy to Streamlit Cloud]

## 📊 Features

### 🟢 Full-Week Active Drivers Analysis
- Identifies drivers with sustained activity throughout the week
- Timeline visualization of driver activity spans
- Performance metrics and RPM analysis
- Geographic distribution of deliveries

### 📈 Key Performance Indicators (KPIs)
1. **Weekly Earnings Evolution per Dispatcher** - Track earnings trends with stacked bar charts
2. **Weekly Billing per Driver by Dispatcher** - Monitor driver billing performance
3. **Rate per Mile Distribution** - Violin plots showing RPM distribution patterns
4. **Destination Market Quality Analysis** - Geographic market analysis with quality scoring
5. **Idle Days per Driver per Dispatcher** - Track driver utilization efficiency
6. **Hours Prebooked** - Analyze booking lead times
7. **Latest Booking Time per Dispatcher** - Monitor booking patterns
8. **Load Cancellations** - Track cancellation rates with color-coded visualization
9. **Additional Performance Metrics** - Revenue analysis with week-over-week comparisons

## 🛠️ Installation

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/jc-dispatch-dashboard.git
cd jc-dispatch-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run jc_dispatch_dashboard.py
```

## 📁 Project Structure

```
jc-dispatch-dashboard/
├── jc_dispatch_dashboard.py      # Main dashboard application
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── .streamlit/                   # Streamlit configuration
│   └── config.toml              # Theme and server settings
└── Trucking_Made_Successful_Data/ # Reference data files
```

## 🎨 Features

### Dark Blue Theme
- Professional dark blue color scheme
- Custom dropdown styling with dark blue fonts
- Enhanced visual hierarchy and contrast

### Interactive Visualizations
- **Timeline Charts** - Driver activity spans
- **Violin Plots** - RPM distribution analysis
- **Choropleth Maps** - Geographic data visualization
- **Stacked Bar Charts** - Multi-dimensional data analysis
- **Line Charts** - Trend analysis over time

---

**Built with ❤️ for JC Freight Operations**
