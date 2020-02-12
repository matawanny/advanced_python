import json

json_string = '''{
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
json_string_from_dict = json.dumps(json_data, indent=4, sort_keys=True)
print(json_string_from_dict)
