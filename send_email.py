import os
import base64
from dotenv import load_dotenv
import time
import smtplib
from email.message import EmailMessage

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = ['https://mail.google.com/']

def generate_email(send_files, sender, recipients, dir_path):
    try:
        header = '11_28_2025' # time.strftime('%m_%d_%Y', time.localtime())
        msg = EmailMessage()
        msg['Subject'] = time.strftime('%A, %b %d, %Y', time.localtime()) + ' SL Report'
        msg['From'] = sender
        msg['To'] = recipients
        msg.preamble = 'Not a MIME-readable recipient. That\'s ok!\n'
        if send_files['Window']:
            file_name = f'{header}_Window.xlsx'
            with open(f'{dir_path}/{file_name}', 'rb') as fp:
                msg.add_attachment(fp.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)
        if send_files['FoH']:
            file_name = f'{header}_FoH.xlsx'
            with open(f'{dir_path}/{file_name}', 'rb') as fp:
                msg.add_attachment(fp.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)
        if send_files['Pending']:
            file_name = f'{header}_Pending.xlsx'
            with open(f'{dir_path}/{file_name}', 'rb') as fp:
                msg.add_attachment(fp.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)
        if send_files['Stations']:
            file_name = f'{header}_Stations.xlsx'
            with open(f'{dir_path}/{file_name}', 'rb') as fp:
                msg.add_attachment(fp.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)
        sanity_msg = EmailMessage()
        sanity_msg['Subject'] = header + ' Confirmation'
        sanity_msg['From'] = sender
        sanity_msg['To'] = sender
        sanity_msg.set_content('Report successfully sent! :D') 
        return [msg, sanity_msg]
    except Exception as e:
        with open('email_errors.txt', 'w') as err_text:
            err_text.write(f'{header} {time.strftime('%I:%M:%S %p')}: {e}\n')
        
def login(creds, CREDS_PATH, TOKE_PATH):
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKE_PATH, 'w') as token:
            token.write(creds.to_json())
        return creds
    except Exception as e:
        with open('email_errors.txt', 'w') as err_text:
            err_text.write(f'{time.strftime('%m_%d_%Y', time.localtime())} {time.strftime('%I:%M:%S %p')}: {e}\n')

def send_stamps(dir_path):
    try:
        load_dotenv()
        CREDS_PATH = os.getenv('CREDS_PATH')
        TOKE_PATH = os.getenv('TOKE_PATH')
        if not TOKE_PATH or not CREDS_PATH:
            raise ValueError("Token/Credentials are NoneTypes (Did you load dotenv?)")
        creds = None
        if os.path.exists(TOKE_PATH):
            creds = Credentials.from_authorized_user_file(TOKE_PATH, SCOPES)
        if not creds or not creds.valid:
            access_token = login(creds, TOKE_PATH)
        sender = os.getenv('SENDER')
        recipients = os.getenv('RECIPIENT')
        if not sender or not recipients:
            raise ValueError("Sender/Recipients are NoneTypes (Did you load dotenv?)")
        auth_info = f"user={sender}\1auth=Bearer {access_token}\1\1"
        auth_str = base64.b64encode(auth_info.encode()).decode()
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.docmd("AUTH", "XOAUTH2 " + auth_str)
            emails = generate_email({
                'Window' : True,
                'FoH' : True,
                'Pending' : True,
                'Stations' : True
            }, sender, recipients, dir_path)
            server.send_message(emails[0])
            server.send_message(emails[1])
    except Exception as e:
        with open('email_errors.txt', 'w') as err_text:
            err_text.write(f'{time.strftime('%m_%d_%Y', time.localtime())} {time.strftime('%I:%M:%S %p')}: {e}\n')