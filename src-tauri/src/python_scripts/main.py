from openmail import OpenMail
import sys, json, socket

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <email>")
        sys.exit(1)

    accounts = json.load(open("./src/python_scripts/accounts.json"))
    email_address = sys.argv[1]
    socket.getaddrinfo('localhost', 8080)
    password = [i["password"] for i in accounts if i["email"] == email_address][0]
    success, message, data = OpenMail(email_address, password).get_emails()
    print(json.dumps({"success": success, "message": message, "data": data}))


    