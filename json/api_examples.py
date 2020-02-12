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

response = requests.get("https://jsonplaceholder.typicode.com/users", timeout = 6,  verify=False)
# print(response.ok)
# print(response.text)
users_list = response.json()
print(users_list)
if(response.ok):
    summary = getSummary(users_list, ['name','email','phone','website'])
    print(summary)
else:
    print("Some error happen ", reponse.status_code)