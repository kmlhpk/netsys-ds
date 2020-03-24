import sys
import datetime
import Pyro4

sys.excepthook = Pyro4.util.excepthook

class Client():
    def __init__(self):
        self.order = {}
        self.menu = {}

    def setMenu(self,menu):
        self.menu = menu
        return

    # Client maintains an order dictionary consisting of menu items and their quantities
    def addToOrder(self):
        print("Please select an item from the menu by typing its name exactly as displayed.")
        food = input()
        if food not in self.menu:
            print("Selection not recognised - please try again.")
            return
        
        print("Please select a quantity.")
        quantity = input()
        if not quantity.isdigit():
            print("Quantity must be a positive integer - please try again.")
            return
        quantity = int(quantity)
        if quantity <= 0:
            print("Quantity must exceed 0 - please try again.")
            return

        if food not in self.order:
            self.order[food] = quantity
        else:
            self.order[food] += quantity

        print("The current state of your order is:")
        for key in self.order:
            print(f" {self.order[key]} x {key} @ £{(self.menu[key]/100):.2f} = £{(self.order[key]*self.menu[key]/100):.2f}")

    # Client can reset the order, or forward it on to the server for "placing" (storage)
    def placeOrder(self):
        print("The current state of your order is:")

        if not self.order:
            print("Empty. Please add some items.")
            return (False,False)
        
        for key in self.order:
            print(f" {self.order[key]} x {key} @ £{(self.menu[key]/100):.2f} = £{(self.order[key]*self.menu[key]/100):.2f}")
        total = 0
        for key in self.order:
            total += (self.order[key] * self.menu[key])
        print(f"For a total cost of £{(total / 100):.2f}")

        print("Enter Y to place your order; enter N to continue shopping; enter R to reset your order")
        command = input()
        if command == "Y":
            print("Please enter a valid UK postcode")
            postcode = input()
            print("Please enter your house number or name")
            house = input()
            date = datetime.datetime.now()
            date = date.strftime("%Y-%m-%d")+"@"+date.strftime("%H:%M:%S")
            request = (date, self.order, total, postcode, house)
            self.order = {}
            return (True,request)
        elif command == "N":
            return (False,False)
        elif command == "R":
            self.order = {}
            return (False,False)
        else:
            print("Selection not recognised - please try again.")
            return (False,False)

    # Client can "suggest" (add) a food item, along with its price, to the server's menu offering
    def suggestFood(self):
        print("Please enter the name of your menu item suggestion")
        item = input()
        
        print("Please enter the price of your menu item suggestion, in pence (ie for a cost of £1.50, enter 150)")
        price = input()
        if not price.isdigit():
            print("Price must be a positive integer - please try again.")
            return
        price = int(price)
        if price <= 0:
            print("Price must exceed 0 - please try again.")

        print(f"Suggested {item} at a cost of £{(price/100):.2f}")
        request = [item, price]
        
        return request

print("---Welcome to Just Hungry!---")
# Establishes connection to frontend server via object proxy
try:
    frontend = Pyro4.Proxy("PYRONAME:module.frontend")
except:
    print("Couldn't connect to frontend server. Shutting client.")
    sys.exit(1)

c = Client()

# Gets starting menu
try:
    menu = frontend.getMenu()
    c.setMenu(menu)
except Exception:
    print("The server took too long to respond, or there was another error. Shutting client.")
    sys.exit(1)

# Interprets command and tries to execute it
while True:
    print("\nPlease select an option:")
    print(" -Enter MENU to see the menu.")
    print(" -Enter ADD to add to your order.")
    print(" -Enter VIEW to place or reset your order.")
    print(" -Enter SUGGEST to suggest a food item for our restaurants to add to the menu.")
    print(" -Enter ORDERS to see all orders made this session.")
    print(" -Enter QUIT to quit the client.")
    command = input()
    if command == "QUIT":
        sys.exit()
    elif command == "MENU":
        try:
            resp = frontend.getMenu()
            if resp == "FAIL":
                print("Menu request failed.")
            else:
                menu = resp
                c.setMenu(menu)
                print("\nMenu:")
                for key in menu:
                    price = menu[key]/100
                    print(f" {key}: £{price:.2f}")
        except Exception:
            print("The server took too long to respond, or there was another error. Exiting client.")
            sys.exit(1)
    elif command == "ADD":
        c.addToOrder()
    elif command == "VIEW":
        try:
            place = c.placeOrder()
            if place[0]:
                print(place)
                date = place[1][0]
                orderDict = place[1][1]
                total = place[1][2]
                postcode = place[1][3]
                house = place[1][4]
                resp = frontend.addOrder(date,orderDict,total,postcode,house)
                if resp == "FAIL-P":
                    print("Order placement failed - invalid postcode.")
                elif resp == "FAIL-S":
                    print("Order placement failed - server error.")
                else:
                    print("Order placed successfully! Order list:")
                    try:
                        resp = frontend.getOrders()
                        if resp == "FAIL":
                            print("Orders request failed.")
                        elif not resp:
                            print("No orders")
                        else:
                            orders = resp
                            # format = [date, self.order, total, postcode, house]
                            for o in orders:
                                try:
                                    print(f"Order placed on {o[0]}, delivered to house {o[4]} at postcode {o[3]}, cost {(o[2]/100):.2f}")
                                    for key in o[1]:
                                        print(f" {o[1][key]} x {key}")
                                except:
                                    print("Badly-formatted order")
                    except Exception:
                        print("The server took too long to respond, or there was another error. Exiting client.")
                        sys.exit(1)
        except Exception:
            print("The server took too long to respond, or there was another error. Exiting client.")
            sys.exit(1)
    elif command == "SUGGEST":
        try:
            request = c.suggestFood()
            resp = frontend.addFood(request[0],request[1])
            if resp == "FAIL":
                print("Menu suggestion failed.")
            else:
                print("Menu suggestion successful. Updating client menu.")
                try:
                    resp = frontend.getMenu()
                    if resp == "FAIL":
                        print("Menu request failed.")
                    else:
                        menu = resp
                        c.setMenu(menu)
                    print("\nMenu:")
                    for key in menu:
                        price = menu[key]/100
                        print(f" {key}: £{price:.2f}")
                except Exception:
                    print("The server took too long to respond, or there was another error. Exiting client.")
                    sys.exit(1)
        except Exception:
            print("The server took too long to respond, or there was another error. Exiting client.")
            sys.exit(1)
    elif command == "ORDERS":
        try:
            resp = frontend.getOrders()
            if resp == "FAIL":
                print("Orders request failed.")
            elif not resp:
                print("No orders")
            else:
                orders = resp
                # format = [date, self.order, total, postcode, house]
                for o in orders:
                    try:
                        print(f"Order placed on {o[0]}, delivered to house {o[4]} at postcode {o[3]}, cost {(o[2]/100):.2f}")
                        for key in o[1]:
                            print(f" {o[1][key]} x {key}")
                    except:
                        print("Badly-formatted order")
        except Exception:
            print("The server took too long to respond, or there was another error. Exiting client.")
            sys.exit(1)
    else:
        print("\nPlease enter a valid command.")