import requests

# Define the base URLs for accounts, balances, and transactions
accounts_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/accounts'
balances_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/balances'
transactions_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/transactions'

def get_accounts(accessToken):
    try:
        # Fetch account details
        response = requests.get(accounts_url, 
            headers={
                'Authorization': 'Bearer ' + accessToken,
                'user-agent': 'MyApp 0.0.1' 
            }, 
            cert=('selfsigned.crt', 'private.key')
        )
        
        if response.status_code == 200:
            accounts_data = response.json()
            accounts_with_balances_and_transactions = []

            # For each account, fetch balance and transaction details
            for account in accounts_data.get('Data', {}).get('Account', []):
                account_id = account.get('AccountId')
                
                # Get account balance
                balance_response = requests.get(f"{balances_url}/{account_id}",
                    headers={
                        'Authorization': 'Bearer ' + accessToken,
                        'user-agent': 'MyApp 0.0.1'
                    },
                    cert=('selfsigned.crt', 'private.key')
                )
                
                # Check if balance response is valid JSON
                try:
                    balance_data = balance_response.json() if balance_response.status_code == 200 else {}
                except ValueError as e:
                    print(f"Error parsing balance JSON for account {account_id}: {e}")
                    balance_data = {}

                # Get account transactions
                transactions_response = requests.get(f"{transactions_url}/{account_id}",
                    headers={
                        'Authorization': 'Bearer ' + accessToken,
                        'user-agent': 'MyApp 0.0.1'
                    },
                    cert=('selfsigned.crt', 'private.key')
                )
                
                # Check if transactions response is valid JSON
                try:
                    transactions_data = transactions_response.json() if transactions_response.status_code == 200 else {}
                except ValueError as e:
                    print(f"Error parsing transactions JSON for account {account_id}: {e}")
                    transactions_data = {}

                # Append account with balances and transactions
                accounts_with_balances_and_transactions.append({
                    'account': account,
                    'balance': balance_data,
                    'transactions': transactions_data
                })

            return accounts_with_balances_and_transactions

        else:
            print(f"Failed to fetch accounts: {response.status_code} - {response.text}")
            return {'error': 'Failed to fetch accounts', 'status_code': response.status_code}
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {'error': str(e)}
