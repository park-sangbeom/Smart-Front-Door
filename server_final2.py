# -*- coding: utf-8 -*-
import socketserver
import threading


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

         self.sendMessageToAll('[%s] %s' %(username, msg))

         return

 

      if msg.strip() == '/quit': # 보낸 메세지가 'quit'이면

         self.removeUser(username)

         return -1

 

   def sendMessageToAll(self, msg):   # 이제 여기서 아두이노랑 라즈베리로 신호 보낼거 코드 짜기

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

            print(msg.decode())

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