# AI-Powered Financial Data Analysis App

A Streamlit application that uses AI to analyze and visualize financial transaction data from various sources.

## Features

- **AI-Powered Column Mapping**: Intelligently identifies and standardizes columns from different financial sources.
- **User Authentication**: Secure login system to store user preferences and mappings.
- **Financial Insights**: Visualization and analysis of spending patterns, income, and savings.
- **Data Aggregation**: Flexible aggregation and summarization capabilities.
- **Export Options**: Export processed data in various formats (CSV, Excel, JSON).

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/financial-analysis-app.git
    cd financial-analysis-app
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up Firebase for authentication and storage:
    - Create a Firebase project at [firebase.google.com](https://firebase.google.com).
    - Enable Authentication and Firestore Database.
    - Generate a service account key and save it as `serviceAccountKey.json` in the project root.

4. Add your API keys:
    - For OpenAI or Hugging Face integration, update the keys in `config/settings.py`.
    - Or set them as environment variables.

## Running the App

Run the application with:
```bash
streamlit run main.py
```

## Project Structure

```
financial_analysis_app/
│
├── main.py                    # Main application entry point
├── requirements.txt           # Dependencies
├── serviceAccountKey.json     # Firebase credentials (not tracked by git)
│
├── config/
│   └── settings.py            # Configuration settings and constants
│
├── utils/
│   ├── data_loader.py         # Data loading utilities
│   ├── data_processor.py      # Data processing utilities
│   └── visualization.py       # Visualization utilities
│
├── services/
│   ├── ai_service.py          # AI mapping and analysis services
│   ├── auth_service.py        # Authentication services
│   └── storage_service.py     # Database storage services
│
└── components/
     ├── auth.py                # Authentication UI components
     ├── data_upload.py         # Data upload UI components
     ├── column_management.py   # Column mapping UI components
     ├── data_exploration.py    # Data exploration UI components
     ├── visualization.py       # Visualization UI components
     ├── aggregation.py         # Data aggregation UI components
     └── export.py              # Data export UI components
```

## Usage Guide

1. **Login/Create Account**: Log in or create a new account to save your data and preferences.

2. **Upload Data**: 
    - Upload your financial transaction files (CSV, Excel, JSON).
    - The AI will automatically analyze and suggest column mappings.

3. **Review and Confirm Mappings**:
    - Check the AI-suggested mappings.
    - Make any necessary adjustments.
    - Confirm mappings (these will be remembered for similar files in the future).

4. **Combine Files**:
    - Merge data from different sources into a unified dataset.
    - Apply preprocessing steps as needed.

5. **Explore and Analyze**:
    - View financial insights and patterns.
    - Perform univariate and bivariate analysis.
    - Create visualizations to better understand your financial data.

6. **Export Results**:
    - Export processed data in your preferred format.
    - Download reports and visualizations.

## Developer Notes

- The AI column mapping currently uses a pattern-based approach but can be enhanced by connecting to OpenAI or Hugging Face APIs.
- Firebase authentication is used in production mode, with a fallback to demo mode for easier development.
- The application is structured to be modular and extensible, making it easy to add new features.

### Setting Up the Project

1. **Create Directory Structure**:
    ```bash
    mkdir -p financial_analysis_app/{config,utils,services,components}
    ```

2. **Create Empty `__init__.py` Files**:
    ```bash
    touch financial_analysis_app/{utils,services,components}/__init__.py
    ```

3. **Copy Files**:
    - Copy each file into its respective directory.
    - Ensure you create the `serviceAccountKey.json` file for Firebase (or adjust the code to handle its absence).

4. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Run the Application**:
    ```bash
    cd financial_analysis_app
    streamlit run main.py
    ```