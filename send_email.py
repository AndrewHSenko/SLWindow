import time
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv()

sender = os.getenv('SENDER')
pwd = os.getenv('SPWD')
receivers = os.getenv('RECEIVERS')
header = time.strftime('%m_%d_%Y', time.localtime())

def update_header():
    # print('email header updated')
    global header
    header = time.strftime('%m_%d_%Y', time.localtime())
    
def sanity_email():
    # print('sanity email started')
    msg = EmailMessage()
    msg['Subject'] = header
    msg['From'] = sender
    msg['To'] = sender
    msg.set_content('Report successfully sent! :D')
    # print('sanity email done')
    return msg

def generate_email(filename, recipients):
    # print('generate_email started')
    msg = EmailMessage()
    msg['Subject'] = time.strftime('%A, %b %d, %Y', time.localtime()) + ' Sandwich Report'
    msg['From'] = sender
    msg['To'] = recipients
    msg.preamble = 'Not a MIME-readable recipient. That\'s ok!\n'
    # print('right before with open')
    path = "G:/Window Data/" + time.strftime('%m_%Y') + '/' + time.strftime('%m_%d_%Y') + '/'
    with open(path + filename[0], 'rb') as fp:
        msg.add_attachment(fp.read(), maintype='text', subtype='plain', filename=header + ' Summary') # Change to pdf
    with open(path + filename[1], 'rb') as fp:
        msg.add_attachment(fp.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=header + ' Spreadsheet and Graph.xlsx')
#    with open(filename[1], 'rb') as fp: # For spreadsheet
#        msg.add_attachment(fp.read(), maintype='
    # print('generate_email done')
    return msg
    
def send_email(): # Add try/except clauses
    # print('send_stamps started')
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(sender, pwd)
    # print('login successful')
    email_msg = generate_email([header + '_Summary.txt', header + '.xlsx'], receivers)
    # print('generate_email activated')
    server.send_message(email_msg)
    # print('email_msg sent')
    server.send_message(sanity_email())
    # print('sanity email sent')
    # print('emails sent')
    server.close()

if __name__ == '__main__':
    print('send_email running')
    send_email()