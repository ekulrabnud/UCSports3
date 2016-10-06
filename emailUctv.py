from smtplib import SMTP_SSL as SMTP
import logging, logging.handlers, sys
from email.mime.text import MIMEText

me = "ldunbar@unitedcenter.com"

def send_message():
    text = '''
            Hello,

            This is an example of how to use email in Python 3.

            Sincerely,

            My name
            '''        
    message = MIMEText(text, 'plain')
    message['Subject'] = "Email Subject" 
   

    # Email that you want to send a message
    message['To'] = me

    try:
        # You need to change here, depending on the email that you use.
        # For example, Gmail and Yahoo have different smtp. You need to know what it is.
        connection = SMTP('webmail.unitedcenter.com')
        connection.set_debuglevel(True)

        # Attention: You can't put for example: 'your_address@email.com'.
        #            You need to put only the address. In this case, 'your_address'.
        connection.login(user,pass)

        try:
            #sendemail(<from address>, <to address>, <message>)
            connection.sendmail(my_email, my_email, message.as_string())
        finally:
            connection.close()
    except Exception as exc:
        logger.error("Error sending the message.")
        logger.critical(exc)
        sys.exit("Failure: {}".format(exc))

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    send_message()