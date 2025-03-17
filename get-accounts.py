import requests
import json
import pnz_tokens

accessToken  =pnz_tokens.accessToken

#aaUrl = 'https://api.apicentre.middleware.co.nz/open-banking-nz/v2.3/accounts'
aaUrl = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/accounts'

def get_accounts(accessToken):
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

accounts = get_accounts(accessToken)

json_accounts = json.loads(accounts.content)
print(json.dumps(json_accounts, indent=2))
