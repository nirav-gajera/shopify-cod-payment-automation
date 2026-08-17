import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOP = os.getenv("SHOPIFY_SHOP")
CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")

GRAPHQL_URL = (
    f"https://{SHOP}.myshopify.com/admin/api/2026-07/graphql.json"
)


def get_access_token():
    """Get a fresh Shopify access token."""

    token_url = (
        f"https://{SHOP}.myshopify.com/admin/oauth/access_token"
    )

    response = requests.post(
        token_url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )

    response.raise_for_status()

    data = response.json()

    print("Token scopes:", data.get("scope"))

    return data["access_token"]


def find_order(order_number):
    """Find a Shopify order by its visible order number."""

    access_token = get_access_token()

    query = """
    query FindOrder($query: String!) {
        orders(first: 10, query: $query) {
            nodes {
                id
                name
                createdAt
            }
        }
    }
    """

    variables = {
        "query": f"name:{order_number}"
    }

    response = requests.post(
        GRAPHQL_URL,
        headers={
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token,
        },
        json={
            "query": query,
            "variables": variables,
        },
    )

    print("HTTP status:", response.status_code)

    data = response.json()

    print("Response:")
    print(data)

    return data


if __name__ == "__main__":
    find_order("6689")