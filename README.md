# Process First LLC Dashboard

## Overview
This dashboard provides a comprehensive interface for process flow visualization, data analytics, and report generation. Built using Dash and Python, it offers interactive components for managing and analyzing process data.

## Features
- **Process Flow Visualization**: Interactive node and edge management with real-time visualization
- **Data Analytics**: Upload and analyze JSON data with various chart types
- **Report Generation**: Generate comprehensive PDF reports from process data
- **Reusable Components**: Modular and reusable components for easy maintenance

## Installation
1. Clone the repository

2. Create a virtual environment:
   ```
   python -m venv env
   ```
3. Activate the environment:
   ```
   source env/bin/activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   gunicorn app:app -c gunicorn.conf.py
   ```
2. Access the dashboard at http://localhost:8050




## License
[MIT](https://choosealicense.com/licenses/mit/)