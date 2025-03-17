import requests

noMtlsUrl = "https://api-nomatls.apicentre.middleware.co.nz/.well-known/openid-configuration"
mtlsUrl = "https://api.apicentre.middleware.co.nz/.well-known/openid-configuration"


response = requests.get(noMtlsUrl)
mtlsResponse = requests.get(mtlsUrl, cert=('selfsigned.crt', 'private.key'))

# No certificate, rejects with 400 (as expected)
# mtlsResponse = requests.get(mtlsUrl)

print("Non-MTLS endpoint OIDD metadata:")
print(response.content)
print("###############")
print("MTLS endpoint OIDD metadata:")
print(mtlsResponse.content)

data=response.json()

print(data['jwks_uri'])

keys = requests.get(data['jwks_uri'])
print("###############")
print("JWKS:")
print(keys.json())
