import requests
import json

# Define the base URLs for accounts, balances, and transactions
accounts_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/accounts'
balances_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/accounts'
transactions_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/accounts'

def get_accounts(accessToken):
    try:
        print("\n🔍 Fetching account details...")

        # Fetch account details
        response = requests.get(
            accounts_url, 
            headers={
                'Authorization': f'Bearer {accessToken}',
                'user-agent': 'MyApp 0.0.1' 
            }, 
            cert=('selfsigned.crt', 'private.key')
        )

        #print(f"➡️ GET {accounts_url}")
        #print(f"⬅️ Response ({response.status_code}): {response.text[:500]}")  # Print first 500 chars of response

        if response.status_code == 200:
            accounts_data = response.json()
            accounts_with_balances_and_transactions = []

            for account in accounts_data.get('Data', {}).get('Account', []):
                account_id = account.get('AccountId')

                print(f"\n🔍 Fetching balance for Account ID: {account_id}")
                balance_url = f"{balances_url}/{account_id}/balances"

                balance_response = requests.get(
                    balance_url,
                    headers={
                        'Authorization': f'Bearer {accessToken}',
                        'user-agent': 'MyApp 0.0.1'
                    },
                    cert=('selfsigned.crt', 'private.key')
                )

                print(f"➡️ GET {balance_url}")
                print(f"⬅️ Response ({balance_response.status_code}): {balance_response.text[:500]}")

                try:
                    balance_data = balance_response.json() if balance_response.status_code == 200 else {}
                except ValueError as e:
                    print(f"⚠️ Error parsing balance JSON for {account_id}: {e}")
                    balance_data = {}

                print(f"✅ Parsed balance data for {account_id}: {json.dumps(balance_data, indent=2)[:500]}")

                print(f"\n🔍 Fetching transactions for Account ID: {account_id}")
                transactions_url_full = f"{transactions_url}/{account_id}/transactions"

                transactions_response = requests.get(
                    transactions_url_full,
                    headers={
                        'Authorization': f'Bearer {accessToken}',
                        'user-agent': 'MyApp 0.0.1'
                    },
                    cert=('selfsigned.crt', 'private.key')
                )

                print(f"➡️ GET {transactions_url_full}")
                print(f"⬅️ Response ({transactions_response.status_code}): {transactions_response.text[:500]}")

                try:
                    transactions_data = transactions_response.json() if transactions_response.status_code == 200 else {}
                except ValueError as e:
                    print(f"⚠️ Error parsing transactions JSON for {account_id}: {e}")
                    transactions_data = {}

                # 🔥 Extract transactions & sort by BookingDateTime
                transactions_list = transactions_data.get('Data', {}).get('Transaction', [])

                sorted_transactions = sorted(
                    transactions_list, 
                    key=lambda x: x.get('BookingDateTime', ''), 
                    reverse=True  # Newest transactions first
                )

                recent_transactions = sorted_transactions[:10]  # Get top 10

                print(f"✅ Most recent transactions for {account_id}: {json.dumps(recent_transactions, indent=2)[:1000]}")

                # Append data
                accounts_with_balances_and_transactions.append({
                    'account': account,
                    'balance': balance_data,
                    'transactions': recent_transactions  # Only 10 most recent transactions
                })

            print("\n✅ All accounts, balances, and transactions fetched successfully!")
            #print(accounts_with_balances_and_transactions)
            return accounts_with_balances_and_transactions

        else:
            print(f"❌ Failed to fetch accounts: {response.status_code} - {response.text}")
            return {'error': 'Failed to fetch accounts', 'status_code': response.status_code}

    except Exception as e:
        print(f"🔥 Exception occurred: {str(e)}")
        return {'error': str(e)}