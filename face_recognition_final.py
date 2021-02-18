# -*- coding: utf-8 -*-
import face_recognition

# Load the jpg file into a numpy array


#check,sungjoon

import threading

 

import socket

 

from threading import Thread

 

from pyrebase import pyrebase

 

global video_capture

 

# firebase storage db

 

config = {

 

    "apiKey" : "AIzaSyAN-b9pCjCdvMkirrfkIWhWV99DZPdBFeM",

 

    "authDomain": "mirror-a9421.firbaseapp.com",

 

    "databaseURL" : "https://mirror-a9421.firebaseio.com/",

 

    "storageBucket" : "mirror-a9421.appspot.com"

 

}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()

HOST = '192.168.0.14' #'192.168.0.7'

PORT = 9009

 

 

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

 

sock.connect((HOST, PORT))

 

print("server connected")

def rcvMsg(sock):

 while True:

    try:

        data = sock.recv(1024)

        data = data.decode()

        print(data)
 
        msg_list = data.split(',')
       
        if 'check' in msg_list[0]:
            
            name = msg_list[1].split('\n')
            name = name[0]
            name = name.strip()
            
            try:
                os.remove(name + ".jpg")
                
            except:
                
                pass
            
            storage.child('pic_'+ name).download(name + ".jpg"," ")
            
            print("save complete")
            
            image = face_recognition.load_image_file(name + ".jpg")
            
            try:
                print("checking picture")
                face_locations = face_recognition.face_locations(image)
                
                if len(face_locations) == 1:
                    msg = "You can use this picture"
                    print("You can use this picture")
                else:
                    msg = "You can not use this picture"
                    print("You can not use this picture")
                    
            except:
                
                msg = "Failed to find face. Please take a photo again"
                print("Failed to find face. Please take a photo again")
                
                
            sock.send(msg.encode())
            
            try:
                os.remove(name + ".jpg")
            except:
                pass
                
       if not data:

          break

    except:

       pass
