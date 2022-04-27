import socket
import threading
import keyboard
import tkinter as tk
import bluetooth
import time

class App:
    def __init__(self):
        self.screen = tk.Tk()

        self.devices = {}
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

        self.index = 0
        self.connected = False
        self.continuer = False
        self.mode_auto = True
        self.display()


    def display(self):

        self.screen.title("BST MOBILE")
        self.screen.geometry("720x480")
        self.screen.protocol("WM_DELETE_WINDOW",self.quit) #Quitter via la croix

        self.state = tk.Label(self.screen, text="Statut : Non connecté")
        self.state.pack(side="top")

        self.listb = tk.Listbox(self.screen,width=100)
        self.listb.pack()
        self.listb.insert(0,"Recherche d'appareil bluetooth...")

        self.auto = tk.Button(self.screen, text="Mode auto : Activé", command=self.auto_switch)
        self.auto.pack()

        self.discover()

        connect = tk.Button(self.screen,text="Connect",command=self.connect)
        connect.pack(side="left")


        disconnect = tk.Button(self.screen,text="Disconnect", command=self.disconnect)
        disconnect.pack(side="right")


        self.screen.mainloop()


    def discover(self):
        x=threading.Thread(target=self.pre_discover)
        x.start()

    def pre_discover(self):
        nearby_devices = bluetooth.discover_devices(lookup_names=True)#Scan des appareils

        self.listb.delete(0, tk.END)
        for mac,name in nearby_devices:
            self.devices[name]=mac
            self.listb.insert(self.index,name)
            self.index+=1


    def connect(self):

        name = self.listb.selection_get()
        mac = self.devices[name]

        if self.connected == False:

            try:
                print(name)
                self.socket.connect((mac,1))#connexion
                self.state["text"] = "Statut : Connecté à "+name
                self.connected = True
                self.continuer = True
                self.lauc()

            except Exception as e:
                print(e)
                self.state["text"] = "Statu : Erreur de connexion, réessayez"

        else:

            self.state["text"] = "Statut : Déjà connecté "

    def disconnect(self):
        if self.connected:
            self.socket.send(bytes('a','UTF-8')) #envoie de la commande pour passer en mode auto
            self.socket.close()

            #création d'un nouveau socket pour une éventuelle reco car on ne peut pas réutiliser le même socket

            self.socket=socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

            self.connected = False
            self.continuer = False

            self.state["text"] = "Satut : Non connecté"
            self.tr.join()

    def lauc(self):

        self.tr = threading.Thread(target=self.pre_lauc)
        self.tr.start()

    def pre_lauc(self):

        dico={"haut":'2',"bas":'3',"droite":'4',"gauche":'5'}

        while self.continuer:
            for name in dico.keys():
                if keyboard.is_pressed(name):
                    text=dico[name]
                    print(text)
                    self.socket.send(bytes(text, 'UTF-8'))
                    time.sleep(0.1)

    def auto_switch(self):

        if self.connected:

            if self.mode_auto:

                self.mode_auto = False
                self.socket.send(bytes('b','UTF-8'))
                self.auto["text"] = "Mode auto : Désactivé"

            else:

                self.mode_auto = True
                self.socket.send(bytes('a','UTF-8'))
                self.auto["text"] = "Mode auto : Activé"

    def quit(self):

        if self.connected:

            self.disconnect()

        self.screen.destroy()


App()