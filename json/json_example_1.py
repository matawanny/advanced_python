import json

json_string='''{
  "countries": [
    {
      "name": "usa",
      "capital": "washington",
      "west": true
    },
    {
      "name": "cannada",
      "capital": "ottawa",
      "west": true
    },
    {
      "name": "japan",
      "capital": "tokyo",
      "west": false
    }
  ]
}'''
json_data = json.loads(json_string)
# print(json_data)
countries = json_data["countries"]
# print(countries)
for country in countries:
    print(country['name'], country['capital'])


