# UI Component Architecture

## User Interface Status
This project is a CLI (Command-Line Interface) tool and does **not** feature any graphical user interface (GUI) or web components.

## Terminal Output Structure
The interface consists of standard output (stdout) logs detailing current script progress:
- **Authentication phase:** Prints "Access token obtained."
- **File parsing phase:** Prints "Found X file(s) in orders/" followed by specific file names.
- **Process order phase:** Displays order numbers, fetched GID, status, and outcome (e.g. `Marked as paid!`, `already PAID, skipping`, `NOT FOUND`, `ERROR: ...`).
- **Summary phase:** Tabular counts of total files processed:
  - Paid
  - Already Paid
  - Not Found
  - Errors
