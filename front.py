import sys
import Pyro4
import random as rd

sys.excepthook = Pyro4.util.excepthook

@Pyro4.expose
class Front():
    def __init__(self):
        # Frontend server maintains a list of all backend servers it sees when it starts a request
        self.backendList = []
        self.backendListCreate()

    def backendListCreate(self):
        self.backendList = []
        backs = {}
        with Pyro4.locateNS(host="localhost") as ns:
            backs = ns.list(metadata_all={"backend"})
            if not backs:
                print("No backend servers found! Closing frontend server.")
                ns.remove("module.frontend")
                sys.exit(1)
            for key in backs:
                self.backendList.append(key)
    
    def primaryUpdate(self):
        print("Failed to connect to primary backend server. Changing primary.")
        self.backendList.append(self.backendList.pop(0))

    def failSim(self):
        # Simulates failure by changing what the frontend considers to be the Primary Backend Server 15% of the time (ie 15% failure rate)
        if rd.uniform(0,1) < 0.15:
            print("Simulated backend failure:")
            self.primaryUpdate()

    def getMenu(self):
        self.backendListCreate()
        self.failSim()
        for i in range(len(self.backendList)):
            try:
                with Pyro4.Proxy("PYRONAME:"+self.backendList[0]) as server:
                    menu = server.getMenu()
                    print("Server was happy")
                    server.propagate()
                    return menu
            except:
                print("Server wasn't happy")
                self.primaryUpdate()
        print("Ran out of backends")
        return "FAIL"
    
    def getOrders(self):
        self.backendListCreate()
        self.failSim()
        for i in range(len(self.backendList)):
            try:
                with Pyro4.Proxy("PYRONAME:"+self.backendList[0]) as server:
                    orders = server.getOrders()
                    print("Server was happy")
                    server.propagate()
                    return orders
            except:
                print("Server wasn't happy")
                self.primaryUpdate()
        print("Ran out of backends")
        return "FAIL"

    def addFood(self,food,price):
        self.backendListCreate()
        self.failSim()
        for i in range(len(self.backendList)):
            try:
                with Pyro4.Proxy("PYRONAME:"+self.backendList[0]) as server:
                    server.addFood(food,price)
                    print("Server was happy")
                    server.propagate()
                    return "OK"
            except:
                print("Server wasn't happy")
                self.primaryUpdate()
        print("Ran out of backends")
        return "FAIL"

    def addOrder(self,date,orderDict,total,postcode,house):
        self.backendListCreate()
        self.failSim()
        for i in range(len(self.backendList)):
            try:
                with Pyro4.Proxy("PYRONAME:"+self.backendList[0]) as server:
                    resp = server.addOrder(date,orderDict,total,postcode,house)
                    if resp == "OK":
                        print("Server was happy")
                        server.propagate()
                        return "OK"
                    else:
                        print("Server returned bad postcode")
                        return "FAIL-P"
            except:
                print("Server wasn't happy")
                self.primaryUpdate()
        print("Ran out of backends")
        return "FAIL-S"

def main():
    Pyro4.config.COMMTIMEOUT = 60.0
    try: 
        with Pyro4.locateNS(host="localhost") as ns:
            with Pyro4.Daemon() as daemon:
                # Removes any existing frontend
                try:
                    ns.remove("module.frontend")
                except:
                    pass

                uri = daemon.register(Front())
                ns.register("module.frontend", uri)

                try:
                    print("Frontend server accepting requests")
                    daemon.requestLoop()
                finally:
                    print("Frontend server shutting down")
                    ns.remove("module.frontend")
    except:
        print("ERROR: Could not start frontend server.")

if __name__=="__main__":
    main()