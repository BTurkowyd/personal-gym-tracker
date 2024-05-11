import requests
from dotenv import load_dotenv
import os

load_dotenv('.env')

APP_ID = os.environ.get('APP_ID')
SERVER_ID = os.environ.get('SERVER_ID')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

url = f'https://discord.com/api/v10/applications/{APP_ID}/guilds/{SERVER_ID}/commands'

json = [
  {
    'name': 'bleb',
    'description': 'Test command.',
    'options': []
  },
  {
    'name': 'fetch_workouts',
    'description': 'Fetching missing workouts to the S3 bucket.',
    'options': []
  },
  {
    'name': 'print_latest_workout',
    'description': 'Print the latest workout',
    'options': []
  }
]

response = requests.put(url, headers={
  'Authorization': f'Bot {BOT_TOKEN}'
}, json=json)

print(response.json())