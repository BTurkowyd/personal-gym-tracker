import pyotp
import os
from dotenv import load_dotenv
import qrcode

if not os.path.exists('./.env'):
    random_key = pyotp.random_base32()

    with open('./.env', 'w') as file:
        file.write(f'OTP_RANDOM_KEY={random_key}')
else:
    load_dotenv('.env')
    random_key = os.environ.get('OTP_RANDOM_KEY')

uri = pyotp.totp.TOTP(random_key).provisioning_uri(name='DiscordWorkoutBot', issuer_name='BartoszTurkowyd')

qrcode.make(uri).save('QRCode.png')
