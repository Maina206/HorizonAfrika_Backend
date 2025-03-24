import requests
import base64
from datetime import datetime
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import json

load_dotenv()

class MpesaAPI:
    def __init__(self):
        self.business_shortcode = "174379"
        self.passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        
        self.callback_url = "https://67d9-105-163-158-252.ngrok-free.app"
        
        self.auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    def get_access_token(self):
        try:
            auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
            headers = {'Authorization': f'Basic {auth}'}
            response = requests.get(self.auth_url, headers=headers)
            response.raise_for_status()
            return response.json()['access_token']
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get access token: {str(e)}")

    def generate_password(self, timestamp):
        data_to_encode = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode()).decode()

    def initiate_stk_push(self, phone_number, amount, reference):
        try:
            access_token = self.get_access_token()
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self.generate_password(timestamp)

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": f"{self.callback_url}/api/mpesa-callback",
                "AccountReference": reference[:20],
                "TransactionDesc": "Package Payment"[:20]
            }

            response = requests.post(self.stk_push_url, json=payload, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'message': 'STK push initiated successfully',
                    'checkout_request_id': response_data.get('CheckoutRequestID'),
                    'merchant_request_id': response_data.get('MerchantRequestID')
                }
            else:
                return {
                    'success': False,
                    'message': response_data.get('ResponseDescription', 'Failed to initiate STK push')
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Failed to initiate STK push: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }