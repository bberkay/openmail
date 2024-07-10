from openmail import OpenMail
import sys, json, socket

if __name__ == "__main__":
    #if len(sys.argv) < 2:
    #    print("Usage: python main.py <email>")
    #    sys.exit(1)

    accounts = json.load(open("./src/python_scripts/accounts.json"))
    email_address = accounts[0]["email"]
    password = accounts[0]["password"]
    #email_address = sys.argv[1]
    #password = sys.argv[2]
    socket.getaddrinfo('localhost', 8080)
    if(len(sys.argv) == 2):
        success, message, data = OpenMail(email_address, password).get_email_content(sys.argv[1])
        print(json.dumps({"success": success, "message": message, "data": data}))
    else:
        success, message, data = OpenMail(email_address, password).get_emails()
        print(json.dumps({"success": success, "message": message, "data": data}))


    