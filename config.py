import pymongo

token = '1108145675:AAF3KHTSIVSktNUZBk4_xBA-bGxf0PlJFRM'
client = pymongo.MongoClient()
main_db = client['PoligonStudioBot']
users = main_db['users']
applications = main_db['applications']
orders = main_db['orders']
months = main_db['months']
days =  main_db['days']
times = main_db['time']
port = 7051
main_lang = 'ru'
provider_tokens = {
    'payme' : '387026696:LIVE:5f631d9e639b10a9119757b4'
}
polling = True 
channel_id = -1001379214048
webhook = ""
host = "127.0.0.1"
