# README.md

Python client for PNZ (sandbox) API

## Setup

1. Run `python -m venv .venv`
2. Run `pip install -r requirements.txt`

## Order of use

To use the scripts directly, use (assuming a python venv is established):

1. `py consent_auth.py` -> this gets a ConsentId
2. `py exchange_code_for_token.py`
3. Any of `get-accounts.py`, `get-balances.py` etc
4. Modify `get_consents.py`, using the previously generated ConsentId

## Useful utils

Run netcat with `nc -kl 8765` to create a network listener to debug HTTP requests
