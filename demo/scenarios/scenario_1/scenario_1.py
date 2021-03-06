import requests
import json
import urllib
import os
import sys
import time

ORDER_HOST = os.environ['DRONIZONE_ORDER_SERVICE_HOST']
ORDER_PORT = os.environ['DRONIZONE_ORDER_SERVICE_PORT']

WAREHOUSE_HOST = os.environ['DRONIZONE_WAREHOUSE_SERVICE_HOST']
WAREHOUSE_PORT = os.environ['DRONIZONE_WAREHOUSE_SERVICE_PORT']

FLEET_HOST = os.environ['DRONIZONE_FLEET_SERVICE_HOST']
FLEET_PORT = os.environ['DRONIZONE_FLEET_SERVICE_PORT']

NOTIFICATION_HOST = os.environ['DRONIZONE_NOTIFICATION_SERVICE_HOST']
NOTIFICATION_PORT = os.environ['DRONIZONE_NOTIFICATION_SERVICE_PORT']

order_service_url="http://"+ORDER_HOST+":"+ORDER_PORT+"/orders/"
warehouse_service_url="http://"+WAREHOUSE_HOST+":"+WAREHOUSE_PORT+"/warehouse/"
fleet_service_url="http://"+FLEET_HOST+":"+FLEET_PORT+"/fleet/"
notification_service_url="http://"+NOTIFICATION_HOST+":"+NOTIFICATION_PORT+"/notifications/"

headers = {
    'Content-Type': 'application/json',
     'Accept': 'application/json'
}

def printJsonOrder(order):
    try :
        print("Détail de la commande: ")
        print("Id : "+str(order["orderId"]))
        print("Customer id : "+str(order["customer_id"]))
        print("Price : "+str(order["price"]))
        print("Status : "+order["processingState"])
        print("Items : "+str(order["items"]))
        print("Deliver adress : "+order["delivery_address"])
    except :
        a=1

def printJsonDrone(drone):
    try :
        print("Détail du drone: ")
        print("Id : "+str(drone["id"]))
        print("Battery : "+drone["batteryState"])
        print("Status : "+drone["status"])
        if drone["order"] is None :
            print("Order : None")
        else :
            print("Order : "+str(drone["order"]["orderId"]))
    except :
        a=1

# Creation d'un article
articleJson = {"idItem":123,"price":2.0}
print("En tant que gerant du stock, je cree un article d'id 123 de prix 2 euros")
print("Route HTTP : "+warehouse_service_url+"items, parametre : "+json.dumps(articleJson))
r=requests.post(warehouse_service_url+"items",data=json.dumps(articleJson), headers=headers)
print("Reponse : "+r.text)

print("---------------------------")

# Creation d'un drone
droneJson = {"batteryState":"FULL","status":"AVAILABLE","id":1}
print("En tant que gerant des drones, je cree un drone en stipulant son etat (etat de la batterie : pleine, status : disponible")
print("Route HTTP : "+fleet_service_url+"drones, parametre : "+json.dumps(droneJson))
r=requests.post(fleet_service_url+"drones",data=json.dumps(droneJson), headers=headers)
print("Reponse : "+r.text)
droneJson = json.loads(r.text)
printJsonDrone(droneJson)

print("---------------------------")

# Creation d'une commande en passant la liste d'articles qu'on veut qu'elle contienne
#articleJsonList = [{"idItem":123,"price":2.0}]
#print("En tant que client, je cree une nouvelle commande en passant la liste d'article que je veux commander en parametre")
#print("Route HTTP : "+order_service_url+", parametre : "+json.dumps(articleJsonList))
#r=requests.post(order_service_url,data=json.dumps(articleJsonList), headers=headers)
#orderJson = json.loads(r.text) #recuperation de la commande cree et enregistrer
#print("Reponse : "+r.text)
#print("L'id de la commande est " + str(orderJson["orderId"]))

#Création d'une commande en passant une commande entière
orderJson = {"items":[{"idItem":123,"price":2.0}],"processingState":"PENDING","customer_id":0,"price":2.0,"delivery_address":"Université Nice Sophia"}
print("En tant que client, je cree une nouvelle commande")
print("Route HTTP : "+order_service_url+"new, parametre : "+json.dumps(orderJson))
r=requests.post(order_service_url+"new",data=json.dumps(orderJson), headers=headers)
orderJson = json.loads(r.text) #recuperation de la commande cree et enregistrer
print("Reponse : "+r.text)
print("L'id de la commande est " + str(orderJson["orderId"]))

print("---------------------------")

#Verification de l'etat de la commande
print("En tant que client, je veux verifier que ma commande a bien ete creee")
print("Route HTTP : "+order_service_url+str(orderJson["orderId"]))
r=requests.get(order_service_url+str(orderJson["orderId"]))
print("Reponse : "+r.text)
printJsonOrder(json.loads(r.text))

print("---------------------------")

# Affichage des commandes en attente de preparation
print("En tant que gerant du stock, je veux savoir quel sont les commandes à preparer")
print("Route HTTP : "+warehouse_service_url+"orders/")
r=requests.get(warehouse_service_url+"orders/")
print("Reponse : "+r.text)
orderList = json.loads(r.text)
print("Il y a "+str(len(orderList))+" commandes en attente d'emballage")
for order in orderList :
    printJsonOrder(order)

print("---------------------------")

# Packing de la nouvelle commande
print("En tant que gerant du stock, je veux renseigner le fait que la commande a ete emballee et qu'elle peut être recupere par un drone")
print("Route HTTP : "+warehouse_service_url+"orders/pack/"+str(orderJson["orderId"]))
r=requests.put(warehouse_service_url+"orders/pack/"+str(orderJson["orderId"]))
print("Reponse : "+r.text)
printJsonOrder(json.loads(r.text))

print("Le service warehouse transmet automatiquement les informations de la commande au service fleet pour qu'il assigne un drone à la commande")

print("---------------------------")

# Verification de l'etat des drones
print("En tant que gerant des drones, je veux savoir quel est l'etat actuel de tous les drones")
print("Route HTTP : "+fleet_service_url+"drones")
r=requests.get(fleet_service_url+"drones")
print("Reponse : "+r.text)
dronerList = json.loads(r.text)
print("Il y a "+str(len(dronerList))+" drones")
for drone in dronerList :
    printJsonDrone(drone)

print("---------------------------")

#Verification de l'etat de la commande
print("En tant que client, je veux verifier que ma commande est bien en cours de livraison")
print("Route HTTP : "+order_service_url+str(orderJson["orderId"]))
r=requests.get(order_service_url+str(orderJson["orderId"]))
print("Reponse : "+r.text)
printJsonOrder(json.loads(r.text))

print("---------------------------")

print("Attente que la commande arrive")
delivering = True
while(delivering):
    r=requests.get(order_service_url+str(orderJson["orderId"]))
    orderJson = json.loads(r.text)
    if(orderJson["processingState"] != "DELIVERING"):
        delivering=False    

print("Le drone prévient le service fleet qu'il est en train de finir sa livraison")
print("Le service fleet prévient le service notification qu'il doit envoyer une notification au client")

print("---------------------------")

# Affichage de la notification
print("En tant que client, je reçois une notification m'indiquant que mon colis est en cours de livraison")
print("Route HTTP : "+notification_service_url+str(orderJson["orderId"]))
r=requests.get(notification_service_url+str(orderJson["orderId"]))
print("Reponse : "+r.text)

print("---------------------------")

#Verification de l'etat de la commande
print("En tant que client, je veux verifier que ma commande a bien été livrée")
print("Route HTTP : "+order_service_url+str(orderJson["orderId"]))
r=requests.get(order_service_url+str(orderJson["orderId"]))
print("Reponse : "+r.text)
printJsonOrder(json.loads(r.text))

print("---------------------------")

# Verification de l'état du drone
print("En tant que gerant des drones, je veux savoir quel est l'etat actuel de la batteries de tous les drones")
print("Route HTTP : "+fleet_service_url+"drones/1")
r=requests.get(fleet_service_url+"drones/1")
print("Reponse : "+r.text)
droneJson = json.loads(r.text)
printJsonDrone(json.loads(r.text))

