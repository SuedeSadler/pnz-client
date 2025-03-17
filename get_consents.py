from jwcrypto import jwt, jwk
import time
import uuid
import requests
import pnz_constants
import pnz_utils

tokenUrl = pnz_constants.tokenUrl
authoriseUrl = pnz_constants.authoriseUrl
clientId = pnz_constants.clientId
responseType = pnz_constants.responseType
scope = pnz_constants.scope
redirectUri = pnz_constants.redirectUri
aacUrl = 'https://api.apicentre.middleware.co.nz/open-banking-nz/v2.3/account-access-consents/'
state = str(uuid.uuid4())
nonce = str(uuid.uuid4())

with open("private.pem", "rb") as pemfile:
   key = jwk.JWK.from_pem(pemfile.read(),b"yomama")

def get_account_access_consent(accessToken, consentId):
    url = aacUrl + consentId
    response = requests.get(url, 
        headers={
            'Authorization': 'Bearer '+ accessToken,
            'user-agent': 'MyApp 0.0.1' 
        },
        cert=('selfsigned.crt', 'private.key')
    )
    # print(response)
    respJson = response.json()
    return respJson

Token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)
response = pnz_utils.get_client_credentials(Token, tokenUrl)
#print(response['token_type'])

# Update this for requested consent
consentId = 'aac_63fe834b2e46cd00233ea9d0'

consent = get_account_access_consent(response['access_token'], consentId)

print(consent)
