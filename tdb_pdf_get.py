import requests
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
    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    code = query_params.get('code', [None])[0]

    url = f"https://www.cardcentre.mn/verify/pdfjs-2.9.359-legacy/web/viewFile.php?CODE={code}"
    
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "www.cardcentre.mn",
        "Referer": f"https://www.cardcentre.mn/verify/pdfjs-2.9.359-legacy/web/viewer.html?file=viewFile.php?CODE={code}",
        "Sec-Ch-Ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "Sec-Ch-Ua-Mobile": "?0",
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Get the filename from the Content-Disposition header, or use a default name
        filename = response.headers.get('Content-Disposition', 'downloaded.pdf').split('filename=')[-1].strip('"')
        
        # Save the PDF
        with open(f'{code}.pdf', 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return f"PDF downloaded successfully: {filename}"
        
    except requests.exceptions.RequestException as e:
        return f"Error downloading PDF: {e}"
        

path = 'huulga4.pdf'

print(get_pdf(path))