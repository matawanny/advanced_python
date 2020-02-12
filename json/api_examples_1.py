import requests
# def getSummary(users):
#     result = {}
#     for user in users:
#         result[user['id']] = user['name'] + " , " + user['phone']
#     return result

def getSummary(users, keys):
    result = {}
    for user in users:
        valueList = []
        for key in keys:
            valueList.append(user[key])
    result[user['id']] = valueList
    return result

post = {"userId":1, "title": "My title", "boday": "This is post body"}
response = requests.post("https://jsonplaceholder.typicode.com/posts", data=post, verify=False)
print(response.text)
