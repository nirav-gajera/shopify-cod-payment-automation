# Deployment & Infrastructure

## Environment Matrix
| Environment | Execution Platform | Environment Variables Configuration |
|---|---|---|
| Development | Local workstation | `.env` file |
| Production | Local workstation or scheduled task runner (e.g. Windows Task Scheduler / Cron job) | System environment variables or local `.env` |

## Infrastructure Requirements
- **Runtime:** Python 3.10+
- **Network Routing:** outbound HTTPS access to `*.myshopify.com` on port `443`
- **File System:** Read/write permissions for `orders/` directory and project root (for reading `.env`).

## Automated Scheduling (Optional Production Setup)
To run this automation periodically, schedule a task to run the python command:
- **Linux/macOS:** Configure a cron job targeting `python mark_as_paid.py` running in the correct virtual environment.
- **Windows:** Create a task in Windows Task Scheduler targeting `python.exe` with arguments `mark_as_paid.py` and setting the working directory to the project root.
