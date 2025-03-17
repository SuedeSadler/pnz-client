from jwcrypto import jwt, jwk
import time
import uuid
import requests
import urllib3
import pnz_utils
import pnz_constants

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

with open("private.pem", "rb") as pemfile:
   key = jwk.JWK.from_pem(pemfile.read(),b"passphrase")

def create_request_object(consentId):
    now = int(time.time())
    exp = now + 600
    jti = str(uuid.uuid4())
    
    Token = jwt.JWT(    header={ 
                            "alg": "PS512",
                            "typ": "JWT",
                            "kid": "4321" },
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

def create_payment_consent(accessToken):
    #consentAPIUrl = "https://api.apicentre.middleware.co.nz/open-banking-nz/v2.3/domestic-payment-consents"
    consentAPIUrl = "https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/domestic-payment-consents"
    requestData = { 
        "Data": {
            "Consent": {
            "InstructedAmount": {
                "Amount": "5.00",
                "Currency": "NZD"
            },
            "InstructionIdentification": "8902dac9-51c4-40be-b41a-c3d36d42707c",
            "RemittanceInformation": {
                "Reference": {
                "CreditorReference": {
                    "Reference": "credRef1",
                    "Particulars": "credPart1",
                    "Code": "credCode1"
                },
                "CreditorName": "CreditorName 123"
                }
            },
            "CreditorAccount": {
                "Identification": "99-3100-0023158-00",
                "SchemeName": "BECSElectronicCredit",
                "SecondaryIdentification": "d88f76df-2a33-47fc-a818-7c1bd8a3fd",
                "Name": "Some name that is long and includes blanks"
            },
            "DebtorAccount": {
                "SchemeName": "BECSElectronicCredit",
                "Identification": "99-1545-7950282-00",
                "Name": "Debtor Account",
                "SecondaryIdentification": "1f8e3ca8-7494-11ea-a1de-777f1f637"
            },
            "DebtorAccountRelease": True,
            "EndToEndIdentification": "7f39b63a-e13e-48d7-ab52-f98028fa8cf3",
            "CreditorAgent": {
                "Identification": "IDXXXXXX",
                "SchemeName": "BICFI"
            }
            }
        },
        "Risk": {
            "EndUserAppName": "This is an app name that is long and includes blanks",
            "EndUserAppVersion": "App Version3.0",
            "PaymentContextCode": "EcommerceServices",
            "MerchantName": "This is a merchant name that is long and includes blanks",
            "MerchantNZBN": "This is an NZBN number of some type",
            "MerchantCategoryCode": "5967",
            "MerchantCustomerIdentification": "This is a special customer identifier that is long and includes blanks",
            "GeoLocation": {
            "Latitude": "45.516136",
            "Longitude": "-73.656830"
            },
            "DeliveryAddress": {
            "AddressType": "DeliveryTo",
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
            'x-fapi-interaction-id': str(uuid.uuid4()),
            'x-idempotency-key': str(uuid.uuid4())
            },
            cert=('selfsigned.crt', 'private.key')
    )
    # print(response.request.url)
    # print(response.request.body)
    # print(response.request.headers)
    # print(response.content)

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
                            headers={
                                'user-agent': 'MyApp 0.0.1'
                            },
                            cert=('selfsigned.crt', 'private.key'))
    print(response.request.url)
    return response


Token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)
response = pnz_utils.get_client_credentials(Token, tokenUrl)
# print(response['token_type'])
# print(response)

# Create a consent object using access token
consentResponse = create_payment_consent(response['access_token'])
print(consentResponse['Data']['ConsentId'])

if consentResponse['Data']['ConsentId'] != '':
    with open('pay-consentid.txt', 'w') as consentfile:
        consentfile.write(consentResponse['Data']['ConsentId'])

# Start the account access authorisation
# consentId = 'ac_62d5fa5a3714140023c2cccf'
consentId = consentResponse['Data']['ConsentId']
assertion = create_request_object(consentId)
# print(assertion)
authResponse = authorise_consent(assertion, consentId)
print(authResponse.headers)

# Switch automated consent, retrieve auth code
if True:
    print(authResponse.headers['Location'])
    redirectResponse = requests.get(authResponse.headers['Location'], allow_redirects=False)


    # print("redirect response:")
    # print(redirectResponse.content)
    
    ## Login
    parseUrl = urllib3.util.parse_url(authResponse.headers['Location'])
    obaRequest = parseUrl.query.split('=')[1]

    session = requests.Session()
    # print(parseUrl[5].split('=')[1])
    loginPayload = {
        "username": "user01",
        "password": "password",
        "SubmitType": "allow",
        "oba_request": obaRequest
    }

    loginResponse = session.post(loginUrl, params=loginPayload, allow_redirects=False)

    # print(loginResponse.headers)

    # consentGetURL = "https://obabank.glueware.dev/auth/consent?oba_request=" + obaRequest
    getConsentResponse = session.get("https://obabank.glueware.dev" + loginResponse.headers['Location'])
    #print(getConsentResponse.content)


    ## Grant consent
    # Note: accounts format to work around Sandbox limitation
    consentPayload = {
        "debtorAccount": '{"Identification":"99-1545-7950282-00","SchemeName":"BECSElectronicCredit","Name":"CurrentAccount","SecondaryIdentification":"ID2-99-1545-7950282-00","AccountId":"OBA-99-1545-7950282-00","TpAccountId":"OBA-99-1545-7950282-00"}',
        "SubmitType" : "allow",
        "oba_request": obaRequest
    }

    consentResponse = session.post(consentUrl, params=consentPayload)
    # consentResponse = session.post("http://elfin:8765", data=consentPayload)
    
    print("### Consent Response ###")
    print(consentResponse.json())

    redirectUrl = urllib3.util.parse_url(consentResponse.json()['redirect'])

    authCode = redirectUrl.fragment.split('&')[0].split('=')[1]

    print("Auth code: " + authCode)

    with open("pay-authcode.txt", "w") as authcodefile:
      authcodefile.write(authCode)
