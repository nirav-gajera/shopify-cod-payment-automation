# Operations Runbook & Troubleshooting

## Common Error Resolutions

| Issue | Potential Cause | Actionable Resolution |
| :--- | :--- | :--- |
| **HTTP 401 Unauthorized** | Invalid Shopify API Client ID or Client Secret. | Verify that credentials in your `.env` file match those in the Shopify Admin panel custom app settings. |
| **HTTP 403 Forbidden** | API client is missing required scopes. | Ensure the custom app has API scopes `read_orders` and `write_orders` enabled and authorized. |
| **`[SKIP] No 'OrderId' column`** | Excel sheet does not have an `OrderId` column. | Rename the header column in the Excel file to match `OrderId` exactly, or update `mark_as_paid.py` to match the custom column header. |
| **Shopify API Rate Limits** | Script is sending requests too quickly. | Shopify's GraphQL API is governed by leaky bucket limits. For exceptionally large order volumes, introduce a sleep interval in the script loop. |
| **`ImportError: No module named...`** | Dependencies are not installed in the execution environment. | Run `pip install requests python-dotenv openpyxl` in the active environment. |

## Recovery Commands
To verify if the connection to Shopify works without processing all orders, run:
```bash
python test_shopify.py
```
To verify if a specific order exists and view its raw details, run:
```bash
python find_order.py
```
