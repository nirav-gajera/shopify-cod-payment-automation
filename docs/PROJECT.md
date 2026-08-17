# Project Technical Specifications

## System Requirements
- Python 3.10+
- Internet access (for Shopify API requests)
- OS: OS-independent (Windows, macOS, Linux)

## Technology Stack Matrix
- **Core Language:** Python
- **API Protocol:** GraphQL (Shopify Admin API)
- **HTTP Client:** `requests`
- **Excel Parser:** `openpyxl`
- **Environment Management:** `python-dotenv`

## Setup Guide

### 1. Install Dependencies
Ensure you have python and pip installed. Run:
```bash
pip install requests python-dotenv openpyxl
```

### 2. Configure Environment variables
Create a `.env` file at the root:
```env
SHOPIFY_SHOP=your-shop-subdomain
SHOPIFY_CLIENT_ID=your_client_id
SHOPIFY_CLIENT_SECRET=your_client_secret
```

### 3. Execution
- Run bulk update:
  ```bash
  python mark_as_paid.py
  ```
