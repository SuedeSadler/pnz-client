import requests
import json
import pnz_pay_tokens
import uuid

accessToken = pnz_pay_tokens.accessToken

#payUrl = 'https://api.apicentre.middleware.co.nz/open-banking-nz/v2.3/domestic-payments'
payUrl = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/domestic-payments'

with open("pay-consentid.txt", "r") as consentfile:
    consentID = consentfile.read()

requestData = { 
    "Data": {
        "Initiation": {
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
        },
        "ConsentId": consentID
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
    url=payUrl,
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

print("HTTP status: " + str(response.status_code))
print("Payment Status: "+ response.json()['Data']['Status'])
print(response.json())
