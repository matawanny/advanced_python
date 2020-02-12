import requests
response_data=requests.get("http://www.facebook.com")
print(response_data.text)
if response_data.ok:
    print("success")
print(response_data.headers['Content-Type'])
response_data=requests.get("https://cdn.pixabay.com/photo/2015/12/01/20/28/road-1072823_960_720.jpg")
f = open ("my_image.jpeg", "wb")
f.write(response_data.content)

