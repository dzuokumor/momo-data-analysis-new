# SMS Transaction Dashboard

A fullstack application for processing, categorizing, and visualizing SMS transaction data.

## Project Overview

This application parses XML SMS transaction data, categorizes messages into transaction types, stores them in a SQLite database, and provides an interactive dashboard for visualization and analysis. The current implementation successfully processes 906 transactions.

## Features

- **Data Processing**: Parse and categorize SMS messages from XML
- **Transaction Categories**:
  - Incoming Money
  - Payments to Code Holders
  - Transfers to Mobile Numbers
  - Bank Deposits
  - Airtime/Bill Payments
  - Cash Power Bill Payments
  - Transactions by Third Parties
  - Withdrawals from Agents
  - Bank Transfers
  - Internet and Voice Bundle Purchases
- **Dashboard**: Interactive visualization of transaction data
- **Search & Filter**: Find transactions by type, date, or amount

## Tech Stack

- **Backend**: Python for XML parsing and data processing
- **Database**: SQLite for data storage
- **Frontend**: HTML, CSS, JavaScript for dashboard interface
- **Visualization**: JavaScript charting libraries

## Getting Started

### Prerequisites

- Python 3.7+
- Web browser with JavaScript enabled
- XML data file containing SMS transactions

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sms-transaction-dashboard.git
   cd sms-transaction-dashboard
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Prepare your data:
   - Place your XML file in the `data/` directory

### Running the Application

1. Process the data:
   ```
   python scripts/process_data.py --input data/your_xml_file.xml
   ```

2. Open the dashboard:
   ```
   python -m http.server 8000
   ```

3. Visit `http://localhost:8000` in your browser

## Project Structure

```
sms-transaction-dashboard/
├── data/                # Data storage
│   └── transactions.xml # Input XML file
├── scripts/             # Processing scripts
│   ├── process_data.py  # Main data processing script
│   └── db_utils.py      # Database utilities
├── db/                  # Database files
│   └── transactions.db  # SQLite database
├── static/              # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── img/             # Images
├── index.html           # Main dashboard page
└── README.md            # This file
```

## Usage

### Data Processing

The application processes XML data with the following steps:
1. Extract SMS messages from XML
2. Categorize each message based on content patterns
3. Clean and normalize data fields
4. Store processed data in SQLite database

### Dashboard

The dashboard provides several features:
- Transaction overview with counts by type
- Charts visualizing transaction volume and distribution
- Search functionality for finding specific transactions
- Detailed view for individual transactions

## Known Limitations

- Currently processes 906 transactions successfully
- Direct database access from frontend (no API layer)
- Basic visualization capabilities

## Future Improvements

- Enhance data processing to handle more transaction formats
- Implement proper backend API
- Add authentication and access controls
- Expand visualization options
- Add export functionality for reports

## Contributors

- dzuokuhmor
- H3PHZY
- Glorycodess
- utatsineza


SEE REPORT HERE
https://docs.google.com/document/d/1QsPytyEvnzqSw1SOl1UCEC3yhkToMZQQOctVfyn8cgo/edit?usp=sharing
