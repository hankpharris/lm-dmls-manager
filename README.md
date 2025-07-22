# DMLS Powder Tracking Manager

A Python application for tracking powder usage and recycling in metal powder and laser DMLS printer systems.

## Features
- Track powder usage and recycling
- SQLite database with Peewee ORM
- PyQt6 GUI interface

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure
- `main.py` - Application entry point
- `database/` - Database models and setup
- `gui/` - PyQt6 GUI components
- `models/` - Peewee ORM models
- `utils/` - Utility functions

## Development
This application uses:
- Python 3.8+
- PyQt6 for GUI
- Peewee ORM for database operations
- SQLite for data storage 