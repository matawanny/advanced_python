import json


f = open("example.json")
json_data = json.load(f)
# print(json_data)
countries = json_data["countries"]
# print(countries)
for country in countries:
    print(country['name'], country['capital'])


