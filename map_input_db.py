from firebase import Firebase
from db import config


db = Firebase(config).database()
file_path = 'map.txt'
#'l/w' + 'p/n/b/r/q/k' + 'id' + '1/0 (has moved)' 
data = {}

with open(file_path, 'r') as file:
    content = file.read()
    width = 527
    height = len(content) // width   #378
    print(height)
    
    for y in range(300, height):
        data[y] = {}
        for x in range(width):
            data[y][x] = {'terrain': 'w',
                            'piece': '',
                            'id': 0,
                            'moved': 0
                            }
            if content[y * width + x] == '0':
                data[y][x]['terrain'] = 'w'
            else:
                data[y][x]['terrain'] = 'l'
        
db.child('map_data').update(data)