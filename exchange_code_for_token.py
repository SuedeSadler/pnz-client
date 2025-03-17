from jwcrypto import jwk
import uuid
import requests
import pnz_utils
import pnz_constants

tokenUrl = pnz_constants.tokenUrl
authoriseUrl = pnz_constants.authoriseUrl
clientId = pnz_constants.clientId
responseType = pnz_constants.responseType
scope = pnz_constants.scope
redirectUri = pnz_constants.redirectUri
state = str(uuid.uuid4())
nonce = str(uuid.uuid4())

with open("private.pem", "rb") as pemfile:
   key = jwk.JWK.from_pem(pemfile.read(),b"yomama")

with open("authcode.txt", "r") as authcodefile:
    authCode = authcodefile.read()

def get_access_token_from_code(Token, code):

    requestData={   "grant_type":"authorization_code",
                    "code": code,
                    "redirect_uri": redirectUri,
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

token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)
# response = get_access_token_from_code(token, 'acf34d36c3a6450c88c0db3aea28bb418b76e45199d446f58036d1067fdce3f9')
response = get_access_token_from_code(token, authCode)
print(response.json())



if response.status_code == requests.codes.ok:
    respJson = response.json()
    with open("pnz_tokens.py", "w") as tokenfile:
        tokenfile.write("accessToken = \""+ respJson['access_token']+"\"\n")
        tokenfile.write("refreshToken = \""+ respJson['refresh_token']+"\"\n")
