from flask import Flask, request, redirect, jsonify, session, render_template, json
import requests
import uuid
import pnz_utils
import pnz_constants
import consent_auth
import get_accounts_bulk
from jwcrypto import jwk
import traceback
from OpenSSL import crypto

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for session management

# OAuth Config
tokenUrl = pnz_constants.tokenUrl
authoriseUrl = pnz_constants.authoriseUrl
clientId = pnz_constants.clientId
redirectUri = pnz_constants.redirectUri
cert_path = 'C:/Users/64225/Desktop/pnz-client/selfsigned.crt'
key_path = 'C:/Users/64225/Desktop/pnz-client/private.pem'

# Define the base URLs for accounts, balances, and transactions
accounts_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/accounts'
balances_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/balances'
transactions_url = 'https://api-nomatls.apicentre.middleware.co.nz/open-banking-nz/v2.3/transactions'

# Load private key for JWT signing
with open(key_path, "rb") as pemfile:
    key = jwk.JWK.from_pem(pemfile.read(), b"yomama")
    
# Redirect URL after successful OAuth flow
@ app.route('/')
def home():
    """Home page with a button to connect the bank account."""
    access_token = session.get('access_token')
    #return render_template("home.html", access_token=access_token)
    
    if access_token:
        return render_template('home.html', access_token=access_token)
    else:
        return render_template('home.html', access_token=None)

@app.route("/callback", methods=["POST"])
def callback():
    """Exchanges an authorization code for an access token."""
    try:
        # Extract the code and id_token from the POST data
        data = request.get_json()
        auth_code = data.get('code')
        id_token = data.get('id_token')

        if not auth_code:
            return jsonify({'error': 'Authorization code missing'}), 400

        # Create client assertion (assuming pnz_utils handles this)
        Token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)

        # Exchange authorization code for access token
        requestData = {
            "grant_type": "authorization_code",
            "code": auth_code,
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

        if response.status_code != 200:
            print("Error response:", response.text)  # Log the error response
            return jsonify({'error': 'Failed to exchange authorization code', 'details': response.text}), response.status_code

        token_data = response.json()
        
        # Store access token in session
        session['access_token'] = token_data.get('access_token')

        print('Access token obtained:', token_data)

        return jsonify({"message": "Success", "access_token": token_data.get("access_token")})

    except Exception as e:
        print("Exception occurred:", traceback.format_exc())  # Print full traceback
        return jsonify({'error': 'Token exchange failed', 'message': str(e)}), 500

@app.route('/accounts')
def display_accounts():
    access_token = session.get('access_token')  # Fetch the access token from session
    
    # If no access token is found, return an error or redirect to OAuth flow
    if not access_token:
        return redirect('/authorize')  # Redirect to the authorize route to get the access token

    # Fetch account details using the access token
    accounts_data = get_accounts_bulk.get_accounts(access_token)
    
    # If there is an error fetching accounts, return it
    if 'error' in accounts_data:
        return jsonify(accounts_data), 500
    
    # Render the accounts page with the accounts data
    return render_template('accounts_page.html', accounts=accounts_data)

@app.route("/authorize")
def authorize():
    """Handles OAuth flow by obtaining user consent and authorization code."""
    try:
        # Generate client assertion JWT
        Token = pnz_utils.create_client_assertion(key, clientId, tokenUrl)

        # Obtain client credentials (access token for consent)
        token_response = pnz_utils.get_client_credentials(Token, tokenUrl)
        access_token = token_response.get('access_token')
        
        
        if not access_token:
            return jsonify({'error': 'Failed to get client credentials'}), 500

        # Create consent object
        consent_response = consent_auth.create_account_consent(access_token)
        consent_id = consent_response['Data']['ConsentId']

        # Start authorization process
        assertion = consent_auth.create_request_object(consent_id)
        auth_response = consent_auth.authorise_consent(assertion, consent_id)

        # Redirect user to the bank's login & consent page
        return redirect(auth_response.headers['Location'])

    except Exception as e:
        return jsonify({'error': 'Authorization failed', 'message': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout the user by clearing session data."""
    session.pop('access_token', None)  # Remove the access token
    return redirect('/')

if __name__ == "__main__":
    app.run(port=8765, debug=True)
