import smtplib
import random
import string

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def SendEMail(toaddr, subject, body, attachment_path, 
              fromaddr, frompassword, fromsmtp, fromport):
    # Image key
    imagekey = ''.join(
                    random.choice(
                        string.ascii_uppercase +
                        string.ascii_lowercase +
                        string.digits
                    ) for _ in range(20))

    # Config
    fromaddr = fromaddr
    frompassword = frompassword

    # Make a new email
    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = fromaddr
    msgRoot['To'] = toaddr
    msgRoot['Subject'] = subject

    # Alternative version
    msgAlternative = MIMEMultipart('alernative')
    msgRoot.attach(msgAlternative)

    # Add an inline image to the text
    msgText = body + '<br><img src="cid:' + imagekey + '">'
    msgAlternative.attach(MIMEText(msgText, 'html'))

    # Prepare image
    fp = open(attachment_path, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    msgImage.add_header('Content-ID', '<' + imagekey + '>')
    msgRoot.attach(msgImage)

    # Connect to server
    s = smtplib.SMTP(fromsmtp, fromport)
    s.starttls()
    s.login(fromaddr, frompassword)
    s.sendmail(fromaddr, toaddr, msgRoot.as_string())
    s.quit()

    return(1)
