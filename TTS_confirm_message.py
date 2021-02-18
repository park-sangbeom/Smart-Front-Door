import urllib.request


client_id = "6escqnyccv"

client_secret = "gtN7dBGpkqpuiZe42m9yiYIjoEHIO0Fb918iHdnx"

encText = urllib.parse.quote("사진 사용 가능 여부 확인 중입니다.")

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

    with open('checkingpic.mp3', 'wb') as f:

        f.write(response_body)

else:

    print("Error Code:" + rescode)

f.close()