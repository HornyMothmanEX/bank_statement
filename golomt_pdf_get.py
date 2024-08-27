import requests
import base64
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
        
def get_pdf(input):
    link = get_link(input)
    code = link.split('/')[-1]

    
    # URL to send the request to
    url = "https://www.egolomt.mn/api/utility/document/download?language=mn"  # Replace with your actual URL

    # JSON payload
    payload = {
        "header": {
            "languageId": "001",
        },
        "body": {
            "qrCode": "A7A35F86D6764A31A5D1691C6813211E"
        }
    }

    # Custom headers
    headers = {
        'Content-Type': 'application/json'
    }


    # Send the POST request with cookies
    response = requests.post(url, json=payload, headers=headers)

    # Print the response
    print("Status Code:", response.status_code)
    # print("Response Body:", response.text)

    try:
        response_json = response.json()
    except ValueError:
        response_json = None  # Handle the case where the response isn't JSON
        

    decoded_data = base64.b64decode(response_json['entity'])

    with open(f"{code}.pdf", "wb") as pdf_file:
        pdf_file.write(decoded_data)

    return f"{code}.PDF file created successfully."
    


path = 'golomt_qr.pdf'

print(get_pdf(path))