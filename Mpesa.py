import requests
import base64
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

class MpesaAPI:
    def __init__(self):
        self.business_shortcode = os.getenv('MPESA_BUSINESS_SHORTCODE')
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL')
        
        # API endpoints
        self.auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    def get_access_token(self):
        """Get access token from Safaricom"""
        try:
            auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}"}
            
            response = requests.get(self.auth_url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            result = response.json()
            return result.get('access_token')
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return None

    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_str.encode()).decode(), timestamp

    def initiate_stk_push(self, phone_number, amount, reference):
        """
        Initiate STK push to customer's phone
        
        Args:
            phone_number (str): Customer's phone number (format: 254XXXXXXXXX)
            amount (int): Amount to be paid
            reference (str): Unique reference for the transaction
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {
                    "success": False,
                    "message": "Failed to get access token"
                }

            password, timestamp = self.generate_password()
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,  # Customer phone number
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,  # Customer phone number
                "CallBackURL": f"{self.callback_url}",
                "AccountReference": reference,
                "TransactionDesc": f"Payment for {reference}"
            }
            
            response = requests.post(self.stk_push_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ResponseCode') == "0":
                return {
                    "success": True,
                    "message": "STK push initiated successfully",
                    "checkout_request_id": result.get('CheckoutRequestID'),
                    "merchant_request_id": result.get('MerchantRequestID')
                }
            else:
                return {
                    "success": False,
                    "message": result.get('ResponseDescription', 'STK push failed')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def verify_transaction(self, checkout_request_id):
        """
        Verify transaction status
        
        Args:
            checkout_request_id (str): The CheckoutRequestID from STK push response
        """
        pass