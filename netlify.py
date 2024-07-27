import hashlib
import json
import requests
import traceback
import time

NETLIFY_BASE_URL = "https://api.netlify.com/api/v1"

# Your Netlify site ID (replace with your actual site ID)
NETLIFY_SITE_ID = "50193ff3-bb44-4b8f-8040-09d2e8598f58"

# Your Personal Access Token (PAT) for Netlify
NETLIFY_PAT = "nfp_5RDJxPNX3yHGJ9odty6NGvdSJxeZqhEGc7d5"

def upload_trade_to_netlify(data: bytes):
    try:
        headers = {
            "Authorization": f"Bearer {NETLIFY_PAT}",
            "Content-Type": "application/json",
        }

        sha1 = hashlib.sha1(data)
        digest = sha1.digest()

        response = requests.post(
            f"{NETLIFY_BASE_URL}/sites/{NETLIFY_SITE_ID}/deploys",
            json={"files": {"/calctrades.json": digest.hex()}},
            headers=headers,
        )

        deploy_data = []

        if response.status_code == 200:
            deploy_data = response.json()
            if len(deploy_data["required"]) != 1 or deploy_data["required"][0] != digest.hex():
                print("Unexpected digest received when creating deploy. The data has probably not changed since the last deployment.")
                return
            
            print("Deploy created successfully!")

        else:
            print(f"Error creating deploy: {response.status_code} - {response.text}")
            return
        
        deploy_id = deploy_data["id"]
        headers["Content-Type"] = "application/octet-stream"

        response = requests.put(
            f"{NETLIFY_BASE_URL}/deploys/{deploy_id}/files/calctrades.json",
            data=data,
            headers=headers,
        )

        if response.status_code == 200:           
            print("File uploaded successfully!")

        else:
            print(f"Error uploading file: {response.status_code} - {response.text}")

        headers["Content-Type"] = "application/json"

        response = requests.post(
            f"{NETLIFY_BASE_URL}/purge",
            json={"site_id": NETLIFY_SITE_ID},
            headers=headers,
        )

        if response.status_code == 202:           
            print("Cache purged successfully!")

        else:
            print(f"Error purging cache: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()

def upload_data_to_netlify(data: bytes):
    try:
        headers = {
            "Authorization": f"Bearer {NETLIFY_PAT}",
            "Content-Type": "application/json",
        }

        sha1 = hashlib.sha1(data)
        digest = sha1.digest()

        response = requests.post(
            f"{NETLIFY_BASE_URL}/sites/{NETLIFY_SITE_ID}/deploys",
            json={"files": {"/data.json": digest.hex()}},
            headers=headers,
        )

        deploy_data = []

        if response.status_code == 200:
            deploy_data = response.json()
            if len(deploy_data["required"]) != 1 or deploy_data["required"][0] != digest.hex():
                print("Unexpected digest received when creating deploy. The data has probably not changed since the last deployment.")
                return
            
            print("Deploy created successfully!")

        else:
            print(f"Error creating deploy: {response.status_code} - {response.text}")
            return
        
        deploy_id = deploy_data["id"]
        headers["Content-Type"] = "application/octet-stream"

        response = requests.put(
            f"{NETLIFY_BASE_URL}/deploys/{deploy_id}/files/data.json",
            data=data,
            headers=headers,
        )

        if response.status_code == 200:           
            print("File uploaded successfully!")

        else:
            print(f"Error uploading file: {response.status_code} - {response.text}")

        headers["Content-Type"] = "application/json"

        response = requests.post(
            f"{NETLIFY_BASE_URL}/purge",
            json={"site_id": NETLIFY_SITE_ID},
            headers=headers,
        )

        if response.status_code == 202:           
            print("Cache purged successfully!")

        else:
            print(f"Error purging cache: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()

def fetch_itemdata():
    url = "https://enchanting-quokka-6f1232.netlify.app/data.json"
    nocache_url = f"{url}?nocache={int(time.time())}"

    try:
        response = requests.get(nocache_url)
        response.raise_for_status()  # Raise an exception if the response status is not OK

        json_data = response.json()
        return json_data

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    
def fetch_prevdata():
    github_url = "https://raw.githubusercontent.com/solimons/solimons/main/calctrades.json"
    response = requests.get(github_url)
    if response.status_code == 200:
        data = response.json()
        return data.get("trades", [])
    else:
        print(f"Error fetching GitHub data: {response.status_code} - {response.text}")
        return []

def get_trade_data():
    url = "https://solario.ws/public-api/trades"
    nocache_url = f"{url}?nocache={int(time.time())}"

    try:
        response = requests.get(nocache_url)
        response.raise_for_status()  # Raise an exception if the response status is not OK

        json_data = response.json()
        return json_data

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    github_trades = set(fetch_prevdata())
    solario_trades = get_trade_data()
    itemdata = fetch_itemdata()

    for trade in solario_trades:
        print(trade)
        if isinstance(trade, dict):
            trade_id = trade.get("id")
            if trade_id not in github_trades:
                recvalue = 0
                sendvalue = 0
                recitems = len(trade.get("recipient_items", []))
                senditems = len(trade.get("sender_items", []))

                for item in trade.get("recipient_items", []):
                    recvalue += itemdata.get(str(item))['value']
                for item in trade.get("sender_items", []):
                    sendvalue += itemdata.get(str(item))['value']
                i_send = sendvalue/recitems
                i_rec = recvalue/senditems

                for item in trade.get("recipient_items", []):
                    itemdata.get(str(item))["prev"].append(i_send)
                    totalprev = 0
                    prevamount = 0
                    for prev_value in itemdata.get(str(item))["prev"]:
                        totalprev += prev_value
                        prevamount += 1
                    itemdata.get(str(item))['value'] = totalprev/prevamount
                
                for item in trade.get("sender_items", []):
                    itemdata.get(str(item))["prev"].append(i_rec)
                    totalprev = 0
                    prevamount = 0
                    for prev_value in itemdata.get(str(item))["prev"]:
                        totalprev += prev_value
                        prevamount += 1
                    itemdata.get(str(item))['value'] = totalprev/prevamount
    return itemdata
            

if __name__ == "__main__":
    upload_data_to_netlify(main().encode('utf-8'))

