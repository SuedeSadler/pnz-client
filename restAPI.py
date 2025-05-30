from flask import Flask, request, jsonify
import requests
import pnz_utils
import pnz_constants
import consent_auth
import get_accounts_bulk
from jwcrypto import jwk
from flask_cors import CORS
import traceback
from OpenSSL import SSL
from OpenSSL import crypto
from pyngrok import ngrok



# Initialize context
context = SSL.Context(SSL.TLSv1_2_METHOD)

# Provide the path to your private key and certificate
context.use_privatekey_file('private.pem')

# If your private key is password protected
context.set_passwd_cb(lambda *args: 'yomama')  # Replace 'yomama' with the correct password if needed

# Optionally, load certificate if you have one
# context.use_certificate_file('path_to_certificate.pem')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow API access from Expo frontend

# OAuth Config
tokenUrl = pnz_constants.tokenUrl
authoriseUrl = pnz_constants.authoriseUrl
clientId = pnz_constants.clientId
redirectUri = pnz_constants.redirectUri
cert_path = 'C:/Users/64225/Desktop/pnz-client/selfsigned.crt'
key_path = 'C:/Users/64225/Desktop/pnz-client/private.pem'
password = b'yomama'
# Function to load the encrypted private key
def load_private_key(key_path, password):
    try:
        with open(key_path, "rb") as pemfile:
            private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, pemfile.read(), password)
        return private_key
    except Exception as e:
        print(f"Error loading private key: {str(e)}")
        return None

# Load the private key using OpenSSL
private_key = load_private_key(key_path, password)

# Convert the OpenSSL private key to PEM format
pem_data = crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key)

# Now load the key using jwcrypto
key = jwk.JWK.from_pem(pem_data)


@app.route("/")
def home():
    """Health check endpoint for API"""
    return jsonify({"message": "API is running"})


@app.route("/callback", methods=["POST"])
def callback():
    """Exchanges an authorization code for an access token and returns JSON."""
    try:
        data = request.get_json()
        auth_code = data.get('code')
        id_token = data.get('id_token')
        
         # Log the received data to see what's coming from the front-end
        print("=== Received Data from Frontend ===")
        print(f"Authorization Code: {auth_code}")
        print(f"ID Token: {id_token, data}")
        print("===================================")

        if not auth_code:
            return jsonify({'error': 'Missing authorization code or ID token'}), 400
        

        # Create client assertion
        token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)

        # Exchange authorization code for access token
        requestData = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirectUri,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": token.serialize()
        }
        
        response = requests.post(
            url=tokenUrl,
            data=requestData,
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                    'user-agent': 'MyApp 0.0.1'},
            cert=('selfsigned.crt', 'private.key')
        )

        if response.status_code != 200:
            return jsonify({'error': 'Failed to exchange authorization code', 'details': response.text}), response.status_code

        token_data = response.json()
        return jsonify(token_data)

    except Exception as e:
        return jsonify({'error': 'Token exchange failed', 'message': str(e)}), 500


@app.route("/accounts", methods=["GET"])
def get_accounts():
    """Returns account data as JSON (requires access token in headers)."""
    access_token = request.headers.get("Authorization")
    print(access_token)
    if not access_token:
        return jsonify({"error": "Missing access token"}), 401

    accounts_data = get_accounts_bulk.get_accounts(access_token)
    if "error" in accounts_data:
        return jsonify(accounts_data), 500

    return jsonify(accounts_data)


@app.route("/authorize", methods=["POST"])
def authorize():
    """Initiates the authorization process and returns the consent URL."""
    try:
        token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)
        token_response = pnz_utils.get_client_credentials(token, tokenUrl)
        access_token = token_response.get("access_token")

        if not access_token:
            return jsonify({"error": "Failed to get client credentials"}), 500

        # Create consent object
        consent_response = consent_auth.create_account_consent(access_token)
        consent_id = consent_response["Data"]["ConsentId"]

        # Start authorization process
        assertion = consent_auth.create_request_object(consent_id)
        auth_response = consent_auth.authorise_consent(assertion, consent_id)

        return jsonify({"auth_url": auth_response.headers["Location"]})

    except Exception as e:
        return jsonify({"error": "Authorization failed", "message": str(e)}), 500

# Open an ngrok tunnel to your Flask app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8765, debug=True, ssl_context=('selfsigned.crt', 'private.key'))
