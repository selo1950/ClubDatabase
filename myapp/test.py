import requests

response = requests.put('https://club-database-api.onrender.com/players/1', json = {'name':'Ivan', 'surname':'Ivanović', 'year_of_birth':1997, 'month_of_birth':3, 'coach_id':1})
print(response.json())