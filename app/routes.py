from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import requests
import boto3
from .pmty_func import redirectToAuth
load_dotenv()

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/trigger', methods=['POST'])
def trigger():
    Auth_variable = redirectToAuth()
    print("Auth_variable:", Auth_variable)  # Debugging line
    return Auth_variable

@main.route('/oauth/callback')
def oauth_callback():
    code = request.args.get("spapi_oauth_code")
    state = request.args.get("state")
    # state variable has to be matched with the env one 
    print("Code:", code)
    print("State:", state)

    if not code:
        return "Authorization code not found in request."

    # Step 1: Exchange code for access + refresh token
    token_url = "https://api.amazon.com/auth/o2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
    auth_payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("REDIRECT_URI"),
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET")
    }

    initial_response = requests.post(token_url, data=auth_payload, headers=headers)
    if initial_response.status_code != 200:
        return f"Token exchange failed: {initial_response.status_code}\n{initial_response.text}"

    tokens = initial_response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token") 

    print("Refresh Token:", refresh_token)
    print("Access Token:", access_token)

    #  Step 2: Refresh the access token
    # refresh_payload = {
    #     "grant_type": "refresh_token",
    #     "refresh_token": refresh_token,
    #     "client_id": os.getenv("CLIENT_ID"),
    #     "client_secret": os.getenv("CLIENT_SECRET")
    # }

    # refresh_response = requests.post(token_url, data=refresh_payload, headers=headers)
    # if refresh_response.status_code != 200:
    #     return f"Refresh failed: {refresh_response.status_code}\n{refresh_response.text}"

    # print(refresh_response.json())
    # refreshed_access_token = refresh_response.json().get("access_token")
    # print("Refreshed Access Token:", refreshed_access_token)

    #  Step 3: Use refreshed access token to call SP-API
    # endpoint = 'https://sellingpartnerapi-eu.amazon.com'
    # api_response = requests.get(
    #     f"{endpoint}/sellers/v1/sellers",
    #     headers={
    #         "x-amz-access-token": refreshed_access_token,
    #         "accept": "application/json"
    #     },
    # )

    # url = "https://sellingpartnerapi-eu.amazon.com/sellers/v1/account"

    headers={
            "x-amz-access-token": access_token,
            "accept": "application/json"
        }

    # response = requests.get(url, headers=headers)

    # data = response.json()
    # print("#"*50)
    # print("userDataResponse =", data)

    endpoint = 'https://sellingpartnerapi-eu.amazon.com'
    marketplace_id = "A21TJRUUN4KGV"

    # Calculate date 30 days ago (or adjust as needed)
    created_after = (datetime.now() - timedelta(days=30)).isoformat()

    request_params = {
        "MarketplaceIds": marketplace_id,
        "CreatedAfter": created_after,
    }

    
    orders_response = requests.get(
        f"{endpoint}/orders/v0/orders",
        headers={
            "x-amz-access-token": access_token,
            "Content-Type": "application/json"
        },
        params=request_params
    )
    orders_response.raise_for_status()  # Raise an exception for bad status codes
    print(orders_response.json())

    endpoint = 'https://sellingpartnerapi-eu.amazon.com'
    marketplace_id = "A21TJRUUN4KGV"

    request_params = {
        "marketplaceIds": marketplace_id,  
        "keywords": "crackShield",  
        "includedData": "summaries",  
        "pageSize": 10,  
    }

    # Sending the request for catalogItems
    catalogItems_response = requests.get(
        f"{endpoint}/catalog/2022-04-01/items",
        headers={
            "x-amz-access-token": access_token,
            "Content-Type": "application/json",
        },
        params=request_params  
    )

    print("catalogItems", catalogItems_response.json())

    endpoint = 'https://sellingpartnerapi-eu.amazon.com'

    response = requests.get(
        f"{endpoint}/sellers/v1/marketplaceParticipations",
        headers={
            "x-amz-access-token": access_token,
            "Content-Type": "application/json"
        },
    )

    print("seller", response.json())
    data = response.json()
    store_name = data['payload'][0]['storeName']

    # if "errors" in data:
    #     return jsonify({"error": "Error fetching user data", "details": data}), 400
    # else:
    #     # marketplace = data["payload"][0]["marketplace"]
    #     username = data["payload"]["primaryContact"]["name"]
    return render_template("seller.html", data=store_name)
