import sys
import Pyro4
import postcodes_io_api
import requests
import json
import random

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Server():
    def __init__(self,name):
        # Backend knows its own name for propagation purposes
        self.name = name
        # Backend starts with a basic menu
        self.menu = {"Pizza":1000,"Curry":700,"Burger":800,"Kebab":600,"Chips":300}
        self.orders = []

    # This function is used to maintain redundancy by replicating data into all other servers
    def propagate(self):
        print("Propagating...")
        backs = {}
        try:
            with Pyro4.locateNS(host="localhost") as ns:
                backs = ns.list(metadata_all={"backend"})
            if len(backs) < 2:
                print("Only one backend server registered - nowhere to propagate data to.")
                return
            print(backs)
            for key in backs:
                if key != self.name:
                    print(f"dealing with {key}")
                    with Pyro4.Proxy("PYRONAME:"+key) as server:
                        print("Made Server")
                        server.setMenu(self.menu)
                        print("set menu")
                        server.setOrders(self.orders)
                        print("set orders")
            print("Propagated")
            return
        except:
            print("Server error: could not propagate data to secondaries.")
            return

    def getName(self):
        return self.name

    def getMenu(self):
        return self.menu

    def setMenu(self,menu):
        self.menu = menu
        return

    def getOrders(self):
        return self.orders

    def setOrders(self,orders):
        self.orders = orders
        return
    
    def addFood(self,food,price):
        self.menu[food] = price
        self.propagate()
        return

    def addOrder(self,date,orderDict,total,postcode,house):
        print("Checking PC")
        if not self.checkPostcode(postcode):
            print("Invalid postcode supplied - order not stored.")
            return "FAIL"
        print("Adding order")
        self.orders.append([date,orderDict,total,postcode,house])
        return "OK"

    def ping(self):
        print("ping")
        return

    def checkPostcode(self,post):
        PIOFail = False
        GTDFail = False
        validPostcode = False

        # Tries Postcodes.io first
        try:
            api = postcodes_io_api.Api()
            validPostcode = api.is_postcode_valid(post)
        except:
            print("There was an error accessing the Postcodes IO API.")
            PIOFail = True

        # If Postcodes.io fails, tries GetTheData's postcode checker
        if PIOFail:
            try:
                url = "http://api.getthedata.com/postcode/" + post
                res = requests.get(url)
                if res:
                    json = res.json()
                    if json["status"] != "match":
                        validPostcode = False
                    else:
                        validPostcode = True
                else: 
                    print("There was an error accessing the GetTheData API.")
                    GTDFail = True
            except: 
                print("There was an error accessing the GetTheData API.")
                GTDFail = True

        # If both fail, assumes postcode is invalid
        if  PIOFail and GTDFail:
            print("Both postcode validation services have failed - assume postcode is invalid")
            validPostcode = False
        return validPostcode

def main():
    Pyro4.config.COMMTIMEOUT = 60.0
    try: 
        with Pyro4.locateNS(host="localhost") as ns:
            with Pyro4.Daemon() as daemon:
                name = f"module.server.{random.randint(1000000000,9999999999)}"
                uri = daemon.register(Server(name))
                ns.register(name, uri, metadata={"backend"})

                try:
                    print("Backend server accepting requests")
                    daemon.requestLoop()
                finally:
                    print("Backend server shutting down")
                    ns.remove(name)
    except:
        print("ERROR: Could not start backend server.")
        ns.remove(name)

if __name__=="__main__":
    main()