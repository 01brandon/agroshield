import qrcode
import io
import base64
from django.conf import settings

def generate_qr_code(batch_id, listing_id):
    # generates a qr code that links to the batch traceability page
    url = f'{settings.FRONTEND_URL}/trace/{batch_id}'

    qr = qrcode.QRCode(
        version         = 1,
        error_correction= qrcode.constants.ERROR_CORRECT_L,
        box_size        = 10,
        border          = 4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img    = qr.make_image(fill_color='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # encode as base64 for storage or return as data uri
    encoded = base64.b64encode(buffer.read()).decode('utf-8')
    data_uri = f'data:image/png;base64,{encoded}'

    return data_uri, url
