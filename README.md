# Shopify COD Order — Mark as Paid Automation

Automates marking **Cash-on-Delivery (COD) orders as Paid** in any Shopify store, by reading delivered order numbers from Excel invoice files and calling the Shopify GraphQL Admin API.

Works with **any Shopify store** and **any logistics provider** that exports order data to `.xlsx` files.

---

## The Problem This Solves

### Before This Automation

When you use a logistics partner for COD deliveries, they periodically send **batch Excel invoice files** listing all orders that were delivered and cash collected. To reconcile these in Shopify, you had to:

1. Open the Shopify admin panel
2. Search for each order number one by one
3. Manually click **"Mark as Paid"** for every order
4. Repeat across dozens or hundreds of orders and multiple invoice files

This was **slow, repetitive, and error-prone** — a process that could take hours when dealing with large invoice batches.

### After This Automation

Run the local web app or a single Python command → upload your invoice files via the interactive dashboard, and all delivered COD orders are automatically found and marked as paid in Shopify via the **GraphQL Admin API**. What used to take hours now takes minutes.

---

## Project Structure

```text
shopify-cod-mark-paid/
├── .env                  # Your Shopify credentials (never commit this)
├── app.py                # Main Flask web app and API endpoints
├── find_order.py         # Utility: look up a Shopify order by number (debugging)
├── mark_as_paid.py       # Legacy CLI automation script
├── templates/
│   └── index.html        # Interactive drag-and-drop web dashboard
└── orders/               # Drop your logistics invoice .xlsx files here (for CLI)
    ├── invoice_batch_1.xlsx
    └── ...
```

---

## Prerequisites

- Python 3.10+
- A Shopify store with a **custom app** configured with:
  - `read_orders` scope
  - `write_orders` scope
  - `read_all_orders` scope

---

## Setup

### Step 1 — Create a Shopify Custom App

1. Go to your Shopify Admin → **Settings → Apps and sales channels → Develop apps**
2. Click **Create an app**, give it a name (e.g. `COD Mark Paid Bot`)
3. Under **Configuration**, enable API scopes: `read_orders`, `write_orders`
4. Under **API credentials**, copy your **Client ID** and **Client Secret**

### Step 2 — Install Dependencies

```bash
pip install Flask requests python-dotenv openpyxl
```

### Step 3 — Configure `.env`

Create a `.env` file in the project root:

```env
SHOPIFY_SHOP=your-store-subdomain
SHOPIFY_CLIENT_ID=your_client_id
SHOPIFY_CLIENT_SECRET=your_client_secret
API_VERSION=2026-07
```

> `SHOPIFY_SHOP` is the subdomain only — e.g. for `mystore.myshopify.com`, use `mystore`.

### Step 4 — Prepare Your Excel Files

You can upload your logistics invoice `.xlsx` files directly via the **Web Dashboard**, or drop them into the `orders/` folder if using the CLI.

The script looks for a column named **`OrderId`** in each sheet containing the Shopify order numbers (e.g. `1001`, `1002`).

**Example expected Excel structure:**

| Service_Provider_Name | Order_Date | AWB_No | Amount | **OrderId** | Delivery_Date |
|---|---|---|---|---|---|
| DHL | 08-01-2026 | 77685982931 | 499 | **1001** | 08-05-2026 |
| BlueDart | 08-02-2026 | 77685983690 | 528 | **1002** | 08-06-2026 |

> If your logistics provider uses a different column name, update the check in `collect_order_numbers()` inside `mark_as_paid.py`:
> ```python
> if h.lower() == "orderid":   # ← change "orderid" to match your column header
> ```

---

## How It Works — Step by Step

```
Web UI / Excel Files  →  Read OrderIds  →  Find Order (GraphQL)  →  Mark as Paid (GraphQL)
```

### Step 1 — Authentication

The script authenticates with Shopify using OAuth client credentials to get a fresh access token:

```
POST https://<your-shop>.myshopify.com/admin/oauth/access_token
```

### Step 2 — Read Order Numbers from Excel

For each `.xlsx` file in the `orders/` folder, the script:
- Opens the workbook
- Locates the `OrderId` column (case-insensitive)
- Collects all order numbers, deduplicating across files

### Step 3 — Find Order in Shopify (GraphQL Query)

For each order number, it queries the Shopify GraphQL Admin API to get the internal order GID and current payment status:

```graphql
query FindOrder($query: String!) {
    orders(first: 1, query: $query) {
        nodes {
            id
            name
            displayFinancialStatus
        }
    }
}
```

Variables sent: `{ "query": "name:#1001" }`

Returns:
- **GID** — e.g. `gid://shopify/Order/6557315858590`
- **Financial status** — e.g. `PENDING`, `PAID`, `PARTIALLY_PAID`

### Step 4 — Mark as Paid (GraphQL Mutation)

If the status is **not** already `PAID`, the script calls the `orderMarkAsPaid` mutation:

```graphql
mutation OrderMarkAsPaid($input: OrderMarkAsPaidInput!) {
    orderMarkAsPaid(input: $input) {
        order {
            id
            name
            displayFinancialStatus
        }
        userErrors {
            field
            message
        }
    }
}
```

The order is instantly updated to **PAID** in Shopify.

---

## Usage

### 1. Web Interface (Recommended)

Run the Flask web server to use the interactive dashboard:

```bash
python app.py
```

Open `http://localhost:8080` in your browser. Drag and drop your `.xlsx` invoice files, click "Process", and watch the real-time logs stream in.

---

### 2. CLI — Test a Single Order Number

Verify your credentials and setup work before running in bulk:

```bash
python mark_as_paid.py --order 1001
```

Output:
```
Access token obtained.
Processing order #1001 ...
  GID    : gid://shopify/Order/6557315858590
  Status : PENDING
  -> Marked as paid! New status: PAID

Result: success
```

---

### 3. CLI — Test a Specific Excel File

Process just one invoice file to verify before running all:

```bash
python mark_as_paid.py --file "orders\invoice_batch_1.xlsx"
```

Output:
```
Access token obtained.

File: invoice_batch_1.xlsx
--------------------------------------------------
Processing order #1001 ...
  GID    : gid://shopify/Order/6557315858590
  Status : PENDING
  -> Marked as paid! New status: PAID
Processing order #1002 ...
  -> already PAID, skipping.
...
  Summary -> Paid: 3  Already paid: 1  Not found: 0  Errors: 0
```

---

### 4. CLI — Process All Files (Full Batch Run)

Mark all orders from all invoice files in the `orders/` folder:

```bash
python mark_as_paid.py
```

Output:
```
Access token obtained.
Found 48 file(s) in orders/

File: invoice_batch_1.xlsx
--------------------------------------------------
...

==================================================
TOTAL SUMMARY
==================================================
  Paid         : 112
  Already paid : 5
  Not found    : 2
  Errors       : 0
```

---

## Command Reference

| Command | Description |
|---|---|
| `python app.py` | **Start the Web Dashboard** |
| `python mark_as_paid.py` | Process **all** `.xlsx` files in `orders/` |
| `python mark_as_paid.py --file "orders\file.xlsx"` | Process a **specific file** |
| `python mark_as_paid.py --order 1001` | Process a **single order number** |
| `python mark_as_paid.py -f "orders\file.xlsx"` | Short flag for `--file` |
| `python mark_as_paid.py -o 1001` | Short flag for `--order` |
| `python find_order.py` | Debug: look up raw order data for a given order number |

---

## Result Statuses Explained

| Status | Meaning |
|---|---|
| `success` | Order found and marked as paid ✓ |
| `already_paid` | Order was already `PAID` — safely skipped |
| `not_found` | No order with that number exists in Shopify |
| `error` | Shopify returned a `userErrors` response (e.g. order is cancelled or archived) |

---

## Customization

| What to change | Where |
|---|---|
| Column name for order numbers | `mark_as_paid.py` → `h.lower() == "orderid"` |
| Shopify API version | `mark_as_paid.py` → `GRAPHQL_URL` (`2026-04`) |
| Invoice files folder | `mark_as_paid.py` → `ORDERS_DIR` |

---

## API Reference

- [Shopify GraphQL — `orderMarkAsPaid` mutation](https://shopify.dev/docs/api/admin-graphql/2026-04/mutations/orderMarkAsPaid)
- [Shopify GraphQL — `orders` query](https://shopify.dev/docs/api/admin-graphql/2026-04/queries/orders)
- [Shopify Custom Apps guide](https://help.shopify.com/en/manual/apps/app-types/custom-apps)

---

## Security Notes

- Add `.env` to `.gitignore` — never commit credentials
- The access token is fetched fresh on every run; it is short-lived
- Only `PENDING` orders can be marked as paid — cancelled/archived orders will return a `userErrors` response and be logged as `error`
