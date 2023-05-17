import requests

BASE =  "http://127.0.0.1:5000/"

response1 = requests.put(BASE + 'players/1',json={ 'name':'Ivan', 'surname':'Ivanović', 'year_of_birth' : 2002, 'month_of_birth':2, 'coach_id': 2})
print(response1.json())
input()

response2 = requests.get(BASE + 'players/1')
print(response2.json())
input()

response6 = requests.get(BASE + 'coaches/2')
print(response6.json())
input()

response4 = requests.patch(BASE + 'players/1', json = {'name': 'Josip'})
print(response4.json())
input()

response5 = requests.get(BASE + 'players/1')
print(response5.json())
input()

response3 = requests.delete(BASE + 'players/1')
print(response3.json())
input()