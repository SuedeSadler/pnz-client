import requests
import json
import pnz_tokens

#aaUrl = 'https://api.apicentre.middleware.co.nz/open-banking-nz/v2.3/transactions'
aaUrl = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/party'
#aaUrl = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/accounts/OBA-99-1545-7950282-03/party'

accessToken = pnz_tokens.accessToken

def get_party(accessToken):
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
party = get_party(accessToken)

json_party = json.loads(party.content)
print(json.dumps(json_party, indent=2))
