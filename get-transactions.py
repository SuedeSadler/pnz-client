import requests
import json
import pnz_tokens

#aaUrl = 'https://api.apicentre.middleware.co.nz/open-banking-nz/v2.3/transactions'
aaUrl = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/transactions'

accessToken = pnz_tokens.accessToken

def get_transactions(accessToken):
    url = aaUrl
    response = requests.get(url, 
        headers={
            'Authorization': 'Bearer '+ accessToken,
            'user-agent': 'MyApp 0.0.1' 
        },
        cert=('selfsigned.crt', 'private.key')
    )
    return response
    # respJson = response.json()
    # return respJson

# balances = get_balances('7483be3bdab643cab68acd9afb83591153d5b1d116554f45b9087a5d3a610a81')
transactions = get_transactions(accessToken)

json_transactions = json.loads(transactions.content)
print(json.dumps(json_transactions, indent=2))
