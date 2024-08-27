import httpx
import pdfplumber
import cv2
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
from urllib.parse import urlparse, parse_qs


def get_link(input):
    #QR unshij bga heseg
    image_pil = cv2.imread(input)
    image = np.array(image_pil)

    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph close
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours and filter for QR code
    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        x,y,w,h = cv2.boundingRect(approx)
        area = cv2.contourArea(c)
        ar = w / float(h)
        if len(approx) == 4 and area > 1000 and (ar > .85 and ar < 1.3):
            cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 3)
            ROI = original[y:y+h, x:x+w]


    zoom_factor = 3 

    height, width = ROI.shape[:2]

    new_height = int(height * zoom_factor)
    new_width = int(width * zoom_factor)


    zoomed_ROI = cv2.resize(ROI, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    gray = cv2.cvtColor(zoomed_ROI, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    decoded_objects = decode(thresh)

    if decoded_objects:
        for obj in decoded_objects:
            return obj.data.decode('utf-8')

def get_token():
    #Access token avj bga heseg

    url = "https://api.khanbank.com/v3/auth/token?grant_type=client_credentials"

    authorization_value = "NUlBR2FsNFpNcTVMNWJJWjVoRjVIWFBDMkRvWlBjM0c6a1I4MWF0bVZyRkFLd3RzOA=="

   
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Basic {authorization_value}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://verify.khanbank.com",
        "Referer": "https://verify.khanbank.com/",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows"
    }

    # Body content (if needed)
    data = {}

    # Send the POST request
    response = httpx.post(url, headers=headers, data=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        json_data = response.json()
        token = json_data['access_token']
        return token
    else:
        return f"Request failed with status code: {response.status_code}"
    
def get_id(id, token):
    url = f"https://api.khanbank.com/v3/signature/document/findDsignatureDocumentsQrCode?qrCode={id}"

    # Define the headers
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Origin": "https://verify.khanbank.com",
        "Referer": "https://verify.khanbank.com/",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "g-recaptcha": "09AMAEUMDhxdlffQVdb4K4W09IPM4SmBm-_0t686VsyxNllNAZtS_3aQUVxiE_JyXo50A_t5IKMHw3GKM73vz2eQFUcXT3gaSCDCm96Q"
    }

    # Send the GET request
    response = httpx.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        json_info = response.json()
        for item in json_info:
                # Check if 'id' is in the dictionary
                if 'id' in item:
                    doc_id = item['id']
        return doc_id

    else:
        return f"Request failed with status code: {response.status_code}"


def get_pdf(input):
    link = get_link(input)
    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    code = query_params.get('code', [None])[0]

    token = get_token()
    id = get_id(code, token)

    url = f"https://api.khanbank.com/v3/signature/document/getDsignaturePdf/{id}"


    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "Content-Length": "0",
        "Origin": "https://verify.khanbank.com",
        "Referer": "https://verify.khanbank.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "g-recaptcha": "09AJEC9jtm9wz1trbEkInYjmXfrnxIhaW0Xt1j6eLMzVlb8Aue-TK-66Q_0EMROKeyaP7I7vM2bXoZ4YX0A9nzFSBRFXfJWCw0y3P_Wg",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    try:
        response = httpx.post(url, headers=headers)
        response.raise_for_status() 
        if response.status_code == 200:
            data = response.content
            with open(f"{code}.pdf", "wb") as file:
                file.write(data)
            return f'{code} done'
            
        else:
            print(f"Failed to retrieve the PDF. Status code: {response.status_code}")
            print(f"Response content: {response.text}")
    except httpx.RequestError as e:
        print(f"An HTTP error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



path = 'Screenshot 2024-08-21 115435.png'



print(get_pdf(path))