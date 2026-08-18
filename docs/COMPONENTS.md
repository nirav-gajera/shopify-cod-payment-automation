# UI Component Architecture

## User Interface Status
This project now features a Flask-powered graphical user interface (GUI) for ease of use.

## Web Dashboard (`templates/index.html`)
The main interface is a single-page HTML application structured with custom CSS and vanilla JavaScript.

### Core Components
1. **Upload Zone:** A drag-and-drop area for users to easily upload `.xlsx` invoice files. It supports clicking to browse files as well.
2. **File Previews:** Once uploaded, files are parsed and displayed as cards showing the filename, number of orders, and a toggleable preview table showing the first 50 rows of data to verify extraction.
3. **Processing Summary:** A metrics bar that dynamically updates during processing to show counts for:
   - **Paid:** Successfully updated orders.
   - **Already Paid:** Orders that were already marked as paid.
   - **Not Found:** Orders that couldn't be located in Shopify.
   - **Errors:** Orders that encountered an error during update.
4. **Real-Time Log Console:** A terminal-like display area (`div#log-console`) that streams live updates from the Flask server via Server-Sent Events (SSE). It logs each step (authentication, querying, updating) with color-coded badges (success, error, warning).

## Legacy Terminal Output
The original CLI interface remains available. It outputs standard logs detailing script progress (authentication, processing orders, summary) when invoked directly via `python mark_as_paid.py`.
