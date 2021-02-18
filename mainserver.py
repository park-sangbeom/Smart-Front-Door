import socketserver
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import threading
from pyrebase import pyrebase
import os
import sys
import urllib.request
import pygame
import time

 

# firebase db

cred = credentials.Certificate("mirror-a9421-firebase-adminsdk-a2um7-42aa70ceea.json")   # firebase db key

firebase_admin.initialize_app(cred,{

    'databaseURL' : "https://mirror-a9421.firebaseio.com/"

})

 
# firebase storage key

config = {   

 

    "apiKey" : "AIzaSyAN-b9pCjCdvMkirrfkIWhWV99DZPdBFeM",

 

    "authDomain": "mirror-a9421.firbaseapp.com",

 

    "databaseURL" : "https://mirror-a9421.firebaseio.com/",

 

    "storageBucket" : "mirror-a9421.appspot.com"

 

}

firebase = pyrebase.initialize_app(config)

 
storage = firebase.storage()

 
HOST = ''

 

PORT = 9009

 
lock = threading.Lock() # syncronized 동기화 진행하는 스레드 생성

 
class UserManager: # 사용자관리 및 채팅 메세지 전송을 담당하는 클래스

 
                   # ① 채팅 서버로 입장한 사용자의 등록

                   # ② 채팅을 종료하는 사용자의 퇴장 관리

 
                   # ③ 사용자가 입장하고 퇴장하는 관리

 

                   # ④ 사용자가 입력한 메세지를 채팅 서버에 접속한 모두에게 전송

 

   def __init__(self):

      self.users = {} # 사용자의 등록 정보를 담을 사전 {사용자 이름:(소켓,주소),...}

   def addUser(self, username, conn, addr): # 사용자 ID를 self.users에 추가하는 함수

##      if username in self.users: # 이미 등록된 사용자라면

 
##         conn.send('이미 등록된 사용자입니다.\n'.encode())

##         return None

 

      # 새로운 접속

      lock.acquire() # 스레드 동기화를 막기위한 락


      self.users[username] = (conn, addr)

      lock.release() # 업데이트 후 락 해제


      self.sendMessageToAll('[%s] 접속' %username)

      print('*** 접속 수 [%d]' %len(self.users))

      return username

   def removeUser(self, username): #사용자를 제거하는 함수

      if username not in self.users:

         return

 
      lock.acquire()

 
      del self.users[username]

      lock.release()


      self.sendMessageToAll('[%s] 접속 종료' %username)

      print('--- 접속 수 [%d]' %len(self.users))

   def messageHandler(self, username, msg): # 전송한 msg를 처리하는 부분

      if msg[0] != '/': # 보낸 메세지의 첫문자가 '/'가 아니면

         self.sendMessageToAll('%s' %(msg))


         return

      if msg.strip() == '/quit': # 보낸 메세지가 'quit'이면

         self.removeUser(username)

 
         return -1


   def sendMessageToAll(self, msg):   # 이제 여기서 아두이노랑 라즈베리로 신호 보낼거 코드 짜기

 
       msg_list = ['0','0']


       if 'gzip' in msg:   # from phone

 
          msg = msg[233:]

          print("[receive]"+ msg)      

 

          if ',' in msg:

 

             msg_list = msg.split(',')

       else:               # from camera.py

          print("[receive]"+ msg)

          for conn, addr in self.users.values():

               conn.send(msg.encode())

               

          if ',' in msg:

             msg_list = msg.split(',')


       if('recog_word' in msg_list[0]):

 

           ref = db.reference('recog_word/' + msg_list[1])

           

           word = ref.get()

           client_id = "6escqnyccv"

           client_secret = "gtN7dBGpkqpuiZe42m9yiYIjoEHIO0Fb918iHdnx"

           encText = urllib.parse.quote(word)

           data = "speaker=mijin&speed=0&text=" + encText;

           url = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"

           request = urllib.request.Request(url)

           request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)

           request.add_header("X-NCP-APIGW-API-KEY",client_secret)

           response = urllib.request.urlopen(request, data=data.encode('utf-8'))

           rescode = response.getcode()

           if(rescode==200):

               print("TTS mp3 저장")

               response_body = response.read()

               with open('voice_'+msg_list[1]+'.mp3', 'wb') as f:

                   f.write(response_body)

           else:

               print("Error Code:" + rescode)

           f.close()

           for conn, addr in self.users.values():

               conn.send(msg.encode())

           return 0

          

 

       elif('recog_voice' in msg_list[0]):

          name = msg_list[1]

          full_filename = 'voice_' + name + '.mp3'

 

          storage.child('voice_' + name).download(full_filename, " ")

          print("[send]" + msg)

          for conn, addr in self.users.values():

 

               conn.send(msg.encode())

 

          return 0

 

       elif('enter' in msg_list[0]):

          name = msg_list[1]

          ref = db.reference('face/' + name)

          data = ref.get()

          data = data[2:len(data)-2]

          data = list(data.replace(",",""))

          for i in data:
              print("[send]" + i)

              for conn, addr in self.users.values():  # 이 코드 대신에 아두이노 시리얼 코드로 

                   conn.send((i+'\n').encode()) 

          music_file = 'voice_' + name + '.mp3'   # mp3 or mid file

 

          file_list = os.listdir(os.getcwd())

 

          if (music_file in file_list):

 
               freq = 16000    # sampling rate, 44100(CD), 16000(Naver TTS), 24000(google TTS)

 

               bitsize = -16   # signed 16 bit. support 8,-8,16,-16

 

               channels = 1    # 1 is mono, 2 is stereo

 

               buffer = 2048   # number of samples (experiment to get right sound)


               # default : pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

 

               pygame.mixer.init(freq, bitsize, channels, buffer)

 

               pygame.mixer.music.load(music_file)

 

               pygame.mixer.music.play()

               clock = pygame.time.Clock()

 

               while pygame.mixer.music.get_busy():

 

                   clock.tick(30)

 

               pygame.mixer.quit()

 
               return 0

       elif 'face_append' in msg_list[0]:

             print("[send]" + msg)
             

             for conn, addr in self.users.values():

               conn.send(msg.encode())

             return 0

       elif 'del' in msg_list[0]:

 
             print("[send]" + msg)
             

             for conn, addr in self.users.values():

 

               conn.send(msg.encode())

 

             return 0

       elif 'face_change' in msg_list[0]:

             print("[send]" + msg)

             for conn, addr in self.users.values():

               conn.send(msg.encode())

             return 0

 

       elif 'off' in msg:
          print("[send]" + msg)

          for conn, addr in self.users.values():
               conn.send(msg.encode())

 
class MyTcpHandler(socketserver.BaseRequestHandler):

   userman = UserManager()

   def handle(self): # 클라이언트가 접속시 클라이언트 주소 출력

      print('[%s] 연결됨' %self.client_address[0])

      username = self.client_address[0]

 
      self.userman.addUser(username, self.request, self.client_address)

      try:

         msg = self.request.recv(1024)

 

         while msg:


            print("[receive]"+ msg.decode())

 

            if self.userman.messageHandler(username, msg.decode()) == -1:


               self.request.close()

 
               break

 

            msg = self.request.recv(1024)

 

      except Exception as e:


         print(e)


      print('[%s] 접속종료' %self.client_address[0])

      self.userman.removeUser(username)

##   def registerUsername(self, ca):

##      while True:

##         register_id = ca

####         msg = register_id + '접속'

####         self.request.send(msg.encode())


####         username = self.request.recv(1024)


####         username = username.decode().strip()

##         if self.userman.addUser(register_id, self.request, self.client_address):

 ##            return register_id


class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

 
    pass


def runServer():

   print('*** 접속 시작')


   print('*** 통신 종료 : Ctrl-C')

 

   try:

 
      server = ChatingServer((HOST, PORT), MyTcpHandler)

 

      server.serve_forever()

 
   except KeyboardInterrupt:

 
      print('--- 통신 종료합니다.')

 
      server.shutdown()

 

      server.server_close()

 

runServer()
