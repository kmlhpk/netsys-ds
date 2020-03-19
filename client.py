import sys
import datetime
import Pyro4

def getOrders():
    pass

def placeOrder():
    print("Please select an item of food by inputting the corresponding digit:\n 1 Pizza\n 2 Curry\n 3 Burger\n 4 Kebab\n 5 Chips")
    itemNo = input()
    item = ""
    if itemNo == "1":
        item = "pizza"
    elif itemNo == "2":
        item = "curry"
    elif itemNo == "3":
        item = "burger"
    elif itemNo == "4":
        item = "kebab"
    elif itemNo == "5":
        item = "chips"
    else:
        print("Invalid item number - please try again.")
        return

    print("Please select a quantity")
    quantity = input()
    if not quantity.isdigit():
        print("Quantity must be a positive integer - please try again.")
        return
    quantity = int(quantity)
    if quantity <= 0:
        print("Quantity must exceed 0 - please try again.")
        return

    print("Please enter a UK postcode (our delivery drivers are magic - if you supply a valid postcode, they will work out your house number automatically!)")
    postcode = input()
    # TODO APPEND TIME
    request = [item, quantity, postcode]
    # TODO MAKE THE REQUEST GO SOMEWHERE
    print(request)
    return

print("---Welcome to Just Hungry!---\n")

while True:
    print("\nPlease select an option:")
    print(" -Enter PLACE to place an order.")
    print(" -Enter ORDERS to see all orders made this session.")
    print(" -Enter QUIT to quit the client.")
    command = input()
    # Interprets command and tries to execute it
    if command == "QUIT":
        sys.exit()
    elif command == "ORDERS":
        try:
            getOrders()
        except Exception:
            print("The server took too long to respond, or there was another error. Exiting client.")
            sys.exit(1)
    elif command == "PLACE":
        try:
            placeOrder()
        except Exception:
            print("The server took too long to respond, or there was another error. Exiting client.")
            sys.exit(1)
    else:
        print("\nPlease enter a valid command.")