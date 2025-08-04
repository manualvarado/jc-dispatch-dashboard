# Trucking Made Successful Data Setup Guide

## 📁 Folder Structure

Place your Trucking Made Successful data files in this folder with the following structure:

```
Trucking_Made_Successful_Data/
├── README.md (this file)
├── market_data.csv (or .xlsx)
├── dead_zones_data.csv (or .xlsx)
├── market_rates_by_state.csv (or .xlsx)
├── driver_fc_mapping.csv (or .xlsx)
└── full_load_history.csv (or .xlsx)
```

## 📊 Required File Formats

### 1. Market Data File (`market_data.csv`)
**Purpose**: Load volume data by state
**Format**: Trucking Made Successful format
**Required Columns**:
- `id` - Unique identifier
- `metadata` - Metadata array (usually empty)
- `name` - State name (e.g., "California", "Texas")
- `value` - Load volume or market data value

**Example**:
```csv
id,metadata,name,value
1,[],Alabama,[5599]
6,[],California,[2250]
48,[],Texas,[5260]
```

### 2. Dead Zones Data (`dead_zones_data.csv`)
**Purpose**: Dead zone analysis with market rates
**Format**: Trucking Made Successful format
**Required Columns**:
- `id` - Unique identifier
- `metadata` - Metadata array (usually empty)
- `name` - State name (e.g., "California", "Texas")
- `value` - Market rate or profitability score

**Example**:
```csv
id,metadata,name,value
1,[],Alabama,[3.453]
6,[],California,[5.19]
48,[],Texas,[3.264]
```

### 3. Market Rates by State (`market_rates_by_state.csv`)
**Purpose**: State-specific market rate analysis
**Format**: Trucking Made Successful format
**Required Columns**:
- `id` - Unique identifier
- `metadata` - Metadata array (usually empty)
- `name` - State name (e.g., "California", "Texas")
- `value` - Market rate per mile

**Example**:
```csv
id,metadata,name,value
1,[],Alabama,[3.453]
6,[],California,[5.19]
48,[],Texas,[3.264]
```

### 4. Driver-FC Mapping (`driver_fc_mapping.csv`)
**Purpose**: Map drivers to dispatchers
**Required Columns**:
- `DRIVER_ID` - Driver identifier
- `FC_ID` - Dispatcher identifier
- `DRIVER_NAME` - Driver name
- `FC_NAME` - Dispatcher name

**Example**:
```csv
DRIVER_ID,FC_ID,DRIVER_NAME,FC_NAME
2530,109,RAUDEL LEON MONTERO,JULIAN CRUZ
2832,87,ALIEN CUESTA FIGUEROA,ALEJANDRO ARISTIZABAL
```

### 5. Full Load History (`full_load_history.csv`)
**Purpose**: Complete historical load data
**Required Columns**: Same as your main load data file

## 🚀 How to Use

1. **Prepare your data files** in the formats shown above
2. **Place them in this folder** (`Trucking_Made_Successful_Data/`)
3. **Upload them through the dashboard sidebar**:
   - Go to the "📊 Reference Data" section
   - Upload each file using the appropriate uploader
   - The dashboard will automatically process and display the data

## 📈 Dashboard Integration

Once uploaded, the Trucking Made Successful data will enhance:

### **KPI 4: Dead Zone Deliveries**
- Enhanced with market rates from your data
- Side-by-side comparison of dead deliveries vs market rates
- Profitability analysis for each state

### **KPI 14: Market Analysis**
- Market rate comparisons across states
- Load-to-truck ratio analysis
- Dead zone profitability scoring

## 🔧 Data Requirements

- **File formats**: CSV, Excel (.xlsx, .xls)
- **Encoding**: UTF-8 recommended
- **Date formats**: YYYY-MM-DD or MM/DD/YYYY
- **State codes**: Use standard 2-letter state codes (CA, TX, NY, etc.)

## 📝 Notes

- Column names are case-sensitive
- Missing data will be handled gracefully
- The dashboard will show previews of uploaded data
- You can upload files individually or all at once

## 🆘 Troubleshooting

If files don't load properly:
1. Check column names match exactly
2. Verify file format (CSV/Excel)
3. Ensure no special characters in column names
4. Check that required columns are present 