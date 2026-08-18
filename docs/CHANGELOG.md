# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - 2026-08-18

### Added
- Interactive Web UI dashboard (`templates/index.html`) with drag-and-drop file upload.
- Flask backend (`app.py`) to manage API endpoints and web server.
- Real-time logging streaming via Server-Sent Events (SSE).
- Support for concurrent/background file processing with queue management.

## [1.0.0] - 2026-08-17
- Initial codebase release.
- Core script `mark_as_paid.py` to process Excel invoices and mark orders as paid.
- Utility script `find_order.py` to search orders.
- Connection test script `test_shopify.py`.
- Full project documentation suite and `AGENTS.md` contract.
