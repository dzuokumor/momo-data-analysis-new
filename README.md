# Momo Data Analysis

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
                 Search funtionality by date, transaction type, and amount range.

## Tech Stack

- **Backend**: Python for XML parsing and data processing
- **Database**: SQLite for data storage
- **Frontend**: HTML, CSS, JavaScript for dashboard interface
- **Visualization**: JavaScript charting libraries

## Getting Started

### Prerequisites

- Python 3.11+
- Python interpreter configured in IDE
- Web browser with JavaScript enabled
- XML data file containing SMS transactions

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/momo-data-analysis-new.git
   cd momo-data-analysis-new
   ```
   
2. Create Virtual Environment:
   ```
   python -m venv venv
   .venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Prepare your data:
   - Place your XML file in the `data/` directory

### Running the Application

1. Process the data:
   Navigate to the transaction_parser.py file

2. Run the file

3. Run the app.py file:
   ```
   Navigate to the project root.
   Run: python -m backend.app 
   ```

4. Visit `http://localhost:5000` in your browser

## Project Structure

```
MOMO-DATA-ANALYSIS/
│
├── __pycache__/
├── .idea/
├── .venv/
│
├── backend/
│
├── data/
│   ├── modified_sms_v2.xml
│
├── database/
│   ├── clean_database.py
│   ├── momo.db
│
├── frontend/
│   ├── static/
│   │   ├── images/
│   │   ├── main.css
│   │   ├── main.js
│   │   ├── summary.js
│   │
│   ├── templates/
│       ├── index.html
│       ├── summary.html
│
├── log/
│
├── __init__.py
├── .gitignore
├── README.md

```

## Usage

### Data Processing

The application processes XML data with the following steps:
1. Extract SMS messages from XML
2. Categorize each message based on content patterns
3. Clean and normalize data fields
4. Store processed data in SQLite database

### Dashboard

The dashboard and summary tiles provide several features:
- Total transactions, Total income, Total expenses, and Average balance.
- Recent transactions
- Charts visualizing transaction types, top senders, and top recipients.
- Top sender, top recepients, transaction volume, and busiest time.
- Search functionality.

## Known Limitations

- Currently processes 906 transactions successfully

## Future Improvements

- Enhance data processing to handle more transaction formats
- Add authentication and access controls
- Expand visualization options
- Add export functionality for reports

## Contributors

dzuokumor

Note: This project is a revised and individual continuation of a previous group repository: [momo-data-analysis](https://github.com/dzuokumor/momo-data-analysis). Code sections originally written by me have been carried over and enhanced, while parts contributed by my teammates have been completely restructured. Key improvements include dynamic backend fetching using Flask and advanced frontend interactions, ensuring originality and eliminating concerns around code reuse or plagiarism.

SEE REPORT [HERE](https://drive.google.com/file/d/1BUBpaUhThlP38rS1R7fljQYcZ822JZlM/view?usp=sharing)
