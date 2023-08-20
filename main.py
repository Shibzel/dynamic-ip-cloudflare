import logging
import os
import time
from dotenv import load_dotenv

import requests


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

EMAIL = os.getenv("EMAIL")
TOKEN = os.getenv("TOKEN")
ZONE_ID = os.getenv("ZONE_ID")
DNS_RECORD_ID = os.getenv("DNS_RECORD_ID")

class FailedDNSRecordUpdate(Exception):
    def __init__(self, result: dict):
        errors = result["errors"]
        super().__init__(
            "\n".join(
                f"Failed to update DNS record with code {error['code']}: {error['message']}"
                for error in errors
            )
        )

def get_current_ip():
    logging.debug("Getting current IP.")
    r = requests.get('https://api.ipify.org')
    r.raise_for_status()
    return r.text

def _check_and_return_response(r: requests.Response):
    result = r.json()
    if r.status_code != 200:
        raise FailedDNSRecordUpdate(result)
    return result

def update_dns_record(new_ip: str, email: str, token: str, zone_id: str, dns_record_id: str):
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": token,
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{dns_record_id}"
    r = requests.get(url, headers=headers)
    result = _check_and_return_response(r)["result"]

    data = {
        "name": result["name"],
        "content": new_ip,
        "type": result["type"]
    }
    r = requests.put(url, headers=headers, json=data)
    _check_and_return_response(r)
 

if __name__ == '__main__':
    logging.info("Starting update loop.")
    last_ip = None
    while True:
        try:
            if (new_ip := get_current_ip()) == last_ip:
                continue
            r = update_dns_record(new_ip, EMAIL, TOKEN, ZONE_ID, DNS_RECORD_ID)
            logging.info(f"DNS record for {DNS_RECORD_ID} updated successfully. New IP: {new_ip}")
            last_ip = new_ip
        except Exception:
            logging.exception(f"An error occured:", exc_info=True)
        time.sleep(300)
