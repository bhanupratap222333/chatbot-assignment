import os
from twilio.rest import Client

sid = 'AC8f0ddaddeefe971d54e98f4fb703547a'
authToken= 'fb2b8071ea15fd4d42644c066952af73'

Client = Client(sid, authToken)

def diet_preference():
    account_sid = os.environ[sid]
    auth_token = os.environ[authToken]
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            body='Thank you for submitting your order. To finalize your payment, please tap below to call or visit our website.',
            from_='whatsapp:+14155238886',
            to='whatsapp:+919137103906'
        )

    print(message.sid)