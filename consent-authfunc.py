from jwcrypto import jwt, jwk
import time
import uuid
import requests
import urllib3
import pnz_utils
import pnz_constants
import curl
import json

tokenUrl = pnz_constants.tokenUrl
authoriseUrl = pnz_constants.authoriseUrl
clientId = pnz_constants.clientId
responseType = pnz_constants.responseType
scope = pnz_constants.scope
redirectUri = pnz_constants.redirectUri
loginUrl = "https://obabank.glueware.dev/mwnz-bank/v2.0/login"
consentUrl = "https://obabank.glueware.dev/mwnz-bank/v2.0/consent"
state = str(uuid.uuid4())
nonce = str(uuid.uuid4())
# Path to your certificate and private key
cert_path = 'C:/Users/64225/Desktop/pnz-client/selfsigned.crt'
key_path = 'C:/Users/64225/Desktop/pnz-client/private.key'

with open("private.pem", "rb") as pemfile:
   key = jwk.JWK.from_pem(pemfile.read(),b"yomama")

def create_request_object(consentId):
    now = int(time.time())
    exp = now + 600
    jti = str(uuid.uuid4())
    
    Token = jwt.JWT(    header={ 
                            "alg": "PS512",
                            "typ": "JWT",
                            "kid": "u9Cf1QIE40tYGpDcNWRJB2XL8dOKzTow" },
                        claims={
                            "client_id": clientId,
                            "response_type": responseType,
                            "scope" : scope,
                            "state": state,
                            "nonce": nonce,
                            "redirect_uri": redirectUri,
                            "claims": {
                                "id_token": {
                                    "ConsentId" :{
                                        "value": consentId,
                                        "essential": True
                                    }
                                }
                            }
                        },
                        default_claims={
                            "iat": now,
                            "exp": exp,
                            "jti": jti,
                            "aud": authoriseUrl,
                            "iss": clientId 
                        })

    Token.make_signed_token(key)
    return Token

def create_account_consent(accessToken):
    #consentAPIUrl = "https://api.apicentre.middleware.co.nz/open-banking-nz/v2.3/account-access-consents"
    consentAPIUrl = "https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/account-access-consents"
    requestData = { 
        "Data" : {
            "Consent": {
                "TransactionToDateTime": "2025-05-08T00:00:00-00:00",
                "ExpirationDateTime": "2025-05-08T00:00:00-00:00",
                "Permissions": [
                    "ReadAccountsDetail",
                    "ReadBalances",
                    "ReadBeneficiariesDetail",
                    "ReadDirectDebits",
                    "ReadParty",
                    "ReadPartyAuthUser",
                    "ReadOffers",
                    "ReadScheduledPaymentsDetail",
                    "ReadStandingOrdersDetail",
                    "ReadStatementsBasic",
                    "ReadStatementsDetail",
                    "ReadTransactionsDetail",
                    "ReadTransactionsCredits",
                    "ReadTransactionsDebits"
                ],
                "TransactionFromDateTime": "2012-05-03T00:00:00-00:00"
            }
        },
        "Risk": {
            "EndUserAppName": "This is my Testing App",
            "EndUserAppVersion": "App Ver0.0.1",
            "PaymentContextCode": "EcommerceServices",
            "MerchantName": "This is a merchant name that is long",
            "MerchantNZBN": "This is an NZBN number",
            "MerchantCategoryCode": "5967",
            "MerchantCustomerIdentification": "This is a special customer identifier",
            "GeoLocation": {
                "Latitude": "45.516136",
                "Longitude": "-73.656830"
            },
            "DeliveryAddress": {
                "AddressLine": [
                    "This is address line 1"
                ],
                "StreetName": "Main Street",
                "BuildingNumber": "12345",
                "PostCode": "12345",
                "TownName": "Some Town",
                "CountrySubDivision": "Some Subdivision",
                "Country": "CA"
            }
	    }
    }
    response = requests.post(
        url=consentAPIUrl,
        json=requestData,
        headers={
            'user-agent': 'MyApp 0.0.1',
            'Authorization': 'Bearer '+ accessToken,
            'x-fapi-customer-ip-address': '2.2.2.2',
            'x-fapi-interaction-id': str(uuid.uuid4())
            },
        cert=('selfsigned.crt', 'private.key')
    )
    
    # DEBUG code, print response parts...
    #
    #print(response.request.url)
    #print(response.request.body)
    #print(response.request.headers)
    # print(response.content)
    # print(response.headers)
    #print("HTTP Response: " + str(response.status_code))
    #print(response.json())

    #c = curl.parse(response, return_it=True)
    #print(c)
    
    respJson = response.json()
    return respJson

def authorise_consent(assertion, consentId):

    payload = {
        "scope": scope,
        "response_type": responseType,
        "redirect_uri": redirectUri,
        "client_id": clientId,
        "state": state,
        "nonce": nonce,
        "request": assertion
    }

    response = requests.get(authoriseUrl, 
                            params=payload, 
                            allow_redirects=False,
                            cert=('selfsigned.crt', 'private.key'))
    print(response.request.url)
    return response

# v2.0
#tokenUrl = "https://api-nomatls.apicentre.middleware.co.nz/middleware-nz-sandbox/v2.0/oauth/token"
# v2.1
# tokenUrl = "https://api-nomatls.apicentre.middleware.co.nz/middleware-nz-sandbox/v2.1/oauth/token"
# v2.2 & v2.3
# tokenUrl = "https://api-nomatls.apicentre.middleware.co.nz/oauth/v2.0/token"
Token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)
response = pnz_utils.get_client_credentials(Token, tokenUrl)
print(response)
print(response['token_type'])
print(response['access_token'])

# exit()
# Create a consent object using access token
consentResponse = create_account_consent(response['access_token'])
print(consentResponse['Data']['ConsentId'])

#exit()

# Start the account access authorisation
# consentId = 'ac_62d5fa5a3714140023c2cccf'
consentId = consentResponse['Data']['ConsentId']
assertion = create_request_object(consentId)
# print(assertion)
authResponse = authorise_consent(assertion, consentId)
print(authResponse.headers)
#exit()
# Switch automated consent, retrieve auth code
print(authResponse.headers['Location'])
redirectResponse = requests.get(authResponse.headers['Location'], allow_redirects=False)

consentResponse = session.post(consentUrl, params=consentPayload)