from openmail import OpenMail
import sys, json, socket

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python main.py <email>")
        sys.exit(1)

    socket.getaddrinfo('localhost', 8080)
    accounts = json.load(open("./src/python_scripts/accounts.json"))
    operation = sys.argv[1]
    #email_address = sys.argv[2]
    #password = sys.argv[3]
    email_address = accounts[0]["email"]
    password = accounts[0]["password"]

    success, message, data = False, "", None
    if operation == "login":
        success, message, data = OpenMail(email_address, password).get_emails()
    elif operation == "get_emails":
        success, message, data = OpenMail(email_address, password).get_emails(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif operation == "get_folders":
        success, message, data = OpenMail(email_address, password).get_folders()
    elif operation == "mark_email":
        success, message = OpenMail(email_address, password).mark_email(sys.argv[2], sys.argv[3], sys.argv[4])
    elif operation == "delete_email":
        success, message = OpenMail(email_address, password).delete_email(sys.argv[2], sys.argv[3])
    elif operation == "move_email":
        success, message = OpenMail(email_address, password).move_email(sys.argv[2], sys.argv[3], sys.argv[4])
    elif operation == "get_email_content":
        success, message, data = OpenMail(email_address, password).get_email_content(sys.argv[2])
    
    print(json.dumps({"success": success, "message": message, "data": data}))


    