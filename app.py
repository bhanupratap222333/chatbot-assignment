from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
import datetime
# import functions_
import os
from twilio.rest import Client

client = MongoClient('mongodb+srv://nitinsingh:Hl7vRDh6FTOchgup@foodnest.8kvfjxp.mongodb.net/')
db = client['whatsapp_db']
collection = db['whatsapp_db']


#==============================================
sid = 'AC8f0ddaddeefe971d54e98f4fb703547a'
authToken= 'fb2b8071ea15fd4d42644c066952af73'
def diet_preference(sid, authToken):
    # Initialize the Twilio Client
    client = Client(sid, authToken)

    # Create a dictionary with quick reply options
    quick_reply_options = [
        {'content_type': 'text', 'title': 'Option 1', 'payload': '1'}
        # {'content_type': 'text', 'title': 'Option 2', 'payload': '2'}
    ]

    # Create and send a WhatsApp message with quick replies
    message = client.messages.create(
        body='Thank you for submitting your order. To finalize your payment, please tap below to call or visit our website.',
        from_='whatsapp:+14155238886',
        to='whatsapp:+919137103906',
        persistent_action=[
            {
                'type': 'reply',
                'payload': option['payload'],
                'title': option['title'],
            } for option in quick_reply_options
        ]
    )

    print(message.sid)
    return message

#==============================================

app = Flask(__name__)

@app.route("/sms", methods=['POST'])
def reply():
    num = request.form.get('From')
    num = num.replace("whatsapp:", "")
    msg_text = request.form.get('Body')
    
    user_data = collection.find_one({"phone_number": num})

    msg = MessagingResponse()

    if user_data is None:
        collection.insert_one({"phone_number": num, "status": "new"})               
        msg.message("It seems you are a new user")

    else:
        if user_data["status"] == "new":
            if msg_text.lower() == "yes":
                collection.update_one(
                    {"phone_number": num},
                    {"$set": {"status": "input", "last": datetime.datetime.now().timestamp()}}
                )
                msg.message("What's your name & Age")
            
            elif msg_text.lower() == "no":
                msg.message("You should type 'yes'")
            else:
                msg.message("Invalid input. Please enter 'yes'")

        elif user_data["status"] == "input":
            user_input = msg_text.strip().split(",")

            if len(user_input) == 2:
                try:
                    user_age = int(user_input[1])
                    user_name = user_input[0].lower()
                    msg.message(f"Nice to meet you {user_name}, you are {user_age} years old")
                    collection.update_one(
                        {"phone_number": num},
                        {"$set": {"status": "name_input","name":user_name,"age":user_age}}
                    )

                    msg.message("What's your street/area address, city, district, state, and pin code? Please provide them separated by commas(','), e.g., street, district, city, state, pincode.")

                    collection.update_one(
                        {"phone_number": num},
                        {"$set": {"status": "address_input"}}
                    )
                    # msg.message("Do you have any dietary preferences(Veg/Non-veg/)")
                    
                except ValueError:
                    msg.message("Invalid age. Please enter a valid age as a number.")

            else:
                msg.message("Invalid input. Please enter a valid input in the format: name, age")

        elif user_data["status"] == "address_input":
            address_input = msg_text.strip().lower().split(",")

            if len(address_input) == 5:
                try:
                    street, district, city, state, pincode = map(str.strip, address_input)
                    msg.message(f"Got it! Your address is:\nStreet: {street}\nDistrict: {district}\nState: {state}\nCity: {city}\nPin Code: {pincode}")

                    collection.update_one(
                        {"phone_number": num},
                        {"$set": {"status": "complete", "address": {"street": street, "district": district, "state": state, "city": city, "pincode": pincode}}}
                    )
                    diet_preference(sid, authToken)
                except ValueError:
                    msg.message("Invalid address input. Please enter a valid input.")
                
                

            else:
                msg.message("Invalid address input. Please enter a valid input in the format: street, district, city, state, pincode")

    return Response(str(msg), content_type='application/xml')

if __name__ == "__main__":
    app.run(debug=True)


#Name
#Age
#Address(street,city,district,state,pincode)
#Phone number
#Diet presence
#disease

#OrderID
#payment option
#Amount