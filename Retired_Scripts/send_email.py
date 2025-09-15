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

# def update_header():
    # print('email header updated')
  #  global header
   # header = time.strftime('%m_%d_%Y', time.localtime())
    
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
    with open('something.txt', 'a') as f:
        f.write('right before with open\n')
    path = "G:/Window Data/" + time.strftime('%m_%Y') + '/' + time.strftime('%m_%d_%Y') + '/'
    with open(path + filename[0], 'rb') as fp:
        msg.add_attachment(fp.read(), maintype='text', subtype='plain', filename=header + ' Summary') # Change to pdf
    with open(path + filename[1], 'rb') as fp:
        msg.add_attachment(fp.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=header + ' Window Spreadsheet and Graph.xlsx')
    with open(path + filename[2], 'rb') as fp:
        msg.add_attachment(fp.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=header + ' FoH Spreadsheet and Graph.xlsx')
    with open('something.txt', 'a') as f:
        f.write('generate_email done\n')
    return msg
    
def send_email(): # Add try/except clauses
    # print('send_stamps started')
    with open('something.txt', 'a') as f:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender, pwd)
        f.write('login successful\n')
        email_msg = generate_email([header + '_Summary.txt', header + '_Window.xlsx', header + '_FoH.xlsx'], receivers)
        f.write('generate_email activated\n')
        server.send_message(email_msg)
        f.write('email_msg sent\n')
        server.send_message(sanity_email())
        f.write('sanity email sent\n')
        f.write('emails sent')
        server.close()

if __name__ == '__main__':
    with open('something.txt', 'a') as f:
        f.write('send_email running\n')
    send_email()