from jwcrypto import jwt, jwk
import time
import uuid
import requests

def create_client_assertion(key, clientId, tokenUrl):

    now = int(time.time())
    exp = now + 600
    jti = str(uuid.uuid4())

    Token = jwt.JWT(    header={ 
                            "alg": "PS512",
                            "typ": "JWT",
                            "kid": "u9Cf1QIE40tYGpDcNWRJB2XL8dOKzTow" },
                        claims={},
                        default_claims={
                            "iat": now,
                            "exp": exp,
                            "jti": jti,
                            "sub": clientId,
                            "aud": tokenUrl,
                            "iss": clientId 
                        })

    Token.make_signed_token(key)
    #print("Generated JWT:", Token.serialize())
    return Token

def get_client_credentials(Token, tokenUrl):

    requestData={   "grant_type":"client_credentials",
                    "scope": "openid accounts payments",
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
    respJson = response.json()
    return respJson
