from openmail import OpenMail
import sys, json, socket

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <email>")
        sys.exit(1)

    socket.getaddrinfo('localhost', 8080)
    accounts = json.load(open("./src/python_scripts/accounts.json"))
    operation = sys.argv[1]
    #email_address = sys.argv[2]
    #password = sys.argv[3]
    email_address = accounts[0]["email"]
    password = accounts[0]["password"]
    if operation in ["login", "get_emails"]:
        success, message, data = OpenMail(email_address, password).get_emails()
    elif operation == "get_email_content":
        success, message, data = OpenMail(email_address, password).get_email_content(sys.argv[2])
    
    print(json.dumps({"success": success, "message": message, "data": data}))


    