import os
from dotenv import load_dotenv
import time
import smtplib
from email.message import EmailMessage

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
                
def send_stamps(dir_path):
    try:
        load_dotenv()   
        sender = os.getenv('SENDER')
        pwd = os.getenv('EMAIL_PWD')
        recipients = os.getenv('RECIPIENT')
        if not sender or not pwd or not recipients:
            raise ValueError("Sender/Pwd/Recipients are NoneTypes (Did you load dotenv?)")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender, pwd)
        emails = generate_email({
            'Window' : True,
            'FoH' : True,
            'Pending' : True,
            'Stations' : True
        }, sender, recipients, dir_path)
        server.send_message(emails[0])
        server.send_message(emails[1])
        server.close()
    except Exception as e:
        with open('email_errors.txt', 'w') as err_text:
            err_text.write(f'{time.strftime('%m_%d_%Y', time.localtime())} {time.strftime('%I:%M:%S %p')}: {e}\n')