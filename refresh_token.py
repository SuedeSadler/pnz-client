from jwcrypto import jwk
import uuid
import requests
import pnz_utils
import pnz_constants
import pnz_tokens

tokenUrl = pnz_constants.tokenUrl
authoriseUrl = pnz_constants.authoriseUrl
clientId = pnz_constants.clientId
responseType = pnz_constants.responseType
scope = pnz_constants.scope
redirectUri = pnz_constants.redirectUri
state = str(uuid.uuid4())
nonce = str(uuid.uuid4())

with open("private.pem", "rb") as pemfile:
   key = jwk.JWK.from_pem(pemfile.read(),b"passphrase")

def request_refresh(Token, refreshToken):
    requestData={   "grant_type":"refresh_token",
                    "refresh_token": refreshToken,
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": Token.serialize()  
                }


    response = requests.post(
        url=tokenUrl,
        data=requestData,
        headers={'Content-Type': 'application/x-www-form-urlencoded',
            'user-agent': 'MyApp 0.0.1'},
            cert=('selfsigned.crt', 'private.key')
    )
    # print(response.request.url)
    # print(response.request.body)
    # print(response.request.headers)
    # print(response.headers)    
    # print(response.content)
    return response

# Doesn't work, no introspection in sandbox
def introspect(assertion, token):
    requestData={   
                    "token": token,
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": assertion.serialize()  
                }
    
    response = requests.post(
        url=introspectUrl,
        data=requestData,
        headers={'Content-Type': 'application/x-www-form-urlencoded',
            'user-agent': 'MyApp 0.0.1'},
    )

    respJson = response.json()
    return respJson

# refreshToken = "41fc75d4936f49a1ac8cbfc19a8f7b3ec024e2303cf140519ff6aa79bd078343"
refreshToken = pnz_tokens.refreshToken
Token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)
response = request_refresh(Token, refreshToken)
# response = introspect(Token, refreshToken)
print(response.json())

if response.status_code == requests.codes.ok:
    respJson = response.json()
    with open("pnz_tokens.py", "w") as tokenfile:
        tokenfile.write("accessToken = \""+ respJson['access_token']+"\"\n")
        tokenfile.write("refreshToken = \""+ respJson['refresh_token']+"\"\n")
