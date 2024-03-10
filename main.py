import pygame
import sys
import random
import keyboard
import math
import time
from firebase import Firebase
from db import config


file_path = 'map.txt'
width = 527  # Adjust the width according to your file

color_pallete = {
    0: (28, 163, 236),
    1: (118, 150, 86),
    2: (238, 238, 210),
    3: 	(0, 68, 116)
}
camera_sens = 10
defoult_cd = 1    # Mins
defoult_cd_start = 0

pieces = {}
next_piece_id = 2

def makeP(n):
    if n < 0:
        return -n
    return n
    
def update_db_map(pos, new_piece):
    if not new_piece:
        data = {'piece': '',
                'id': 0,
                'moved': 0
                }
    else:
        data = {'piece': new_piece.db_caption,
                'id': new_piece.team_id,
                'moved': new_piece.has_moved
                    }
    db.child('map_data').child(pos[1]).child(pos[0]).update(data)
    a = db.child('update_id').get().val()['id']
    
    data['x'] = pos[0]
    data['y']  = pos[1]
    data = {a: data}  
    db.child('updates').child(a).update(data)
    db.child('update_id').update({'id': a+1})
    

    

    

           
     # Login

client_team_id = 1
db = Firebase(config).database()
db_data = db.get()
next_id_db = db.child('next_player_id').get().val()
proceed = False
register_new_pokemon = False
while not proceed:
    s = input('press 1 to login, press 2 to register: ')
    if s == '2':
        login = input('Login: ')
        if login in db_data.val():
            print('login already taken')
            continue
        password = input('Password: ')
        db.child(login).set({'password': password,
                            'id': next_id_db})
        db.update({'next_player_id': next_id_db+1})
        client_team_id = next_id_db
        register_new_pokemon = True
        proceed = True
    elif s == '1':
        login = input('Login: ')
        password = input('Password: ')
        if db.child(login).get().val() != None:
            if db.child(login).get().val()['password'] == password:
                client_team_id = db.child(login).get().val()['id']
                proceed = True
                
db_map1 = db.child('map_data').get().val()
db_map = []
for i1 in db_map1:
    db_map.append([])
    for i in db_map1[0]:
        db_map.append(i)
        

with open(file_path, 'r') as file:
    content = file.read()
    height = len(content) // width
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess 2.0")

    x_adj, y_adj = 0, 0
    x_adj_pix, y_adj_pix = 20, 5
    zoom_factor = 2
    selected_tile = [0, 0]

    piece_matrix = []
    for n in range(height):
        piece_matrix.append([0]*width)

    def new_piece(piece, db_update=True):
        global next_piece_id
        global pieces
        global piece_matrix
        pieces[next_piece_id] = piece
        piece_matrix[piece.pos[1]][piece.pos[0]] = next_piece_id
        if db_update:
            update_db_map(piece.pos, piece)
        next_piece_id += 1

        return True

    class Horse:
        imp = pygame.image.load("Textures\\nw.png")
        db_caption = 'horse'

        def __init__(self, pos, team_id, has_moved=False):
            self.pos = pos
            self.team_id = team_id
            self.has_moved = has_moved
            self.cooldown = time.time()

        def viable_move(self, target):
            target = [round(target[0]), round(target[1])]
            if content[target[1] * width + target[0]] == '0':
                return False
            if makeP(self.pos[0]-target[0]) == 1 and makeP(self.pos[1]-target[1]) == 2:
                pass
            elif makeP(self.pos[0]-target[0]) == 2 and makeP(self.pos[1]-target[1]) == 1:
                pass
            else:
                return False

            if target[0] < 0 or target[0] > width or target[1] < 0 or target[1] > height:
                return False

            if piece_matrix[target[1]][target[0]] == 0:
                return True
            if pieces[piece_matrix[target[1]][target[0]]].team_id != self.team_id:
                return True
            return False

        def move(self, target):
            global piece_matrix
            if self.viable_move(target) and time.time() - self.cooldown > defoult_cd * 60:
                update_db_map(self.pos, 0)
                update_db_map(target, self)
                
                target = [round(target[0]), round(target[1])]
                piece_matrix[self.pos[1]][self.pos[0]], piece_matrix[target[1]][target[0]] = 0, piece_matrix[self.pos[1]][self.pos[0]]
                self.pos = [target[0], target[1]]
                self.cooldown = time.time()

        def render(self):
            screen.blit(pygame.transform.scale(self.imp, (round(zoom_factor), round(zoom_factor))), ((self.pos[0]+x_adj) *
                        zoom_factor + x_adj_pix, (self.pos[1]+y_adj) * zoom_factor + y_adj_pix))

    class Rook:
        imp = pygame.image.load("Textures\\rw.png")
        db_caption = 'rook'

        def __init__(self, pos, team_id, has_moved=False):
            self.pos = pos
            self.team_id = team_id
            self.has_moved = has_moved
            self.cooldown = time.time()

        def viable_move(self, target):
            y_step, x_step = 0, 0
            target = [round(target[0]), round(target[1])]
            if content[target[1] * width + target[0]] == '0':
                return False
            if target[0] == self.pos[0] and target[1] == self.pos[1]:
                return False
            if target[0] != self.pos[0] and target[1] != self.pos[1]:
                return False
            if target[1] == self.pos[1]:
                if target[0] < self.pos[0]:
                    x_step = -1
                else:
                    x_step = 1
                for x in range(self.pos[0], target[0], x_step):
                    if content[self.pos[1] * width + x] == '0':
                        return False
                    if x != self.pos[0]:
                        if piece_matrix[self.pos[1]][x] != 0:
                            return False
                if piece_matrix[self.pos[1]][x + x_step] == 0:
                    return True
                if pieces[piece_matrix[self.pos[1]][x + x_step]].team_id != self.team_id:
                    return True
                    
            elif target[0] == self.pos[0]:
                
                if target[1] < self.pos[1]:
                    y_step = -1
                else:
                    y_step = 1
                    
                for y in range(self.pos[1], target[1], y_step):
                    if content[y * width + self.pos[0]] == '0':
                        return False
                    if y != self.pos[1]:
                        if piece_matrix[y][self.pos[0]] != 0:
                            return False
                if piece_matrix[y + y_step][self.pos[0]] == 0:
                    return True
                if pieces[piece_matrix[y + y_step][self.pos[0]]].team_id != self.team_id:
                    return True
            return False

        def move(self, target):
            if self.viable_move(target) and time.time() - self.cooldown > defoult_cd * 60:
                update_db_map(self.pos, 0)
                update_db_map(target, self)
                
                
                target = [round(target[0]), round(target[1])]
                piece_matrix[self.pos[1]][self.pos[0]], piece_matrix[target[1]][target[0]] = 0, piece_matrix[self.pos[1]][self.pos[0]]
                self.pos = [target[0], target[1]]
                self.cooldown = time.time()
                

        def render(self):
            screen.blit(pygame.transform.scale(self.imp, (round(zoom_factor), round(zoom_factor))), ((self.pos[0]+x_adj) *
                        zoom_factor + x_adj_pix, (self.pos[1]+y_adj) * zoom_factor + y_adj_pix))
            
    
    class Bishop:
        imp = pygame.image.load("Textures\\bw.png")
        db_caption = 'bishop'

        def __init__(self, pos, team_id, has_moved=False):
            self.pos = pos
            self.team_id = team_id
            self.has_moved = has_moved
            self.cooldown = time.time()

        def viable_move(self, target):
            y_step, x_step = 0, 0
            target = [round(target[0]), round(target[1])]
            if content[target[1] * width + target[0]] == '0':
                return False
            if makeP(target[0]-self.pos[0]) != makeP(target[1]-self.pos[1]):
                return False
            if target[0] == self.pos[0] and target[1] == self.pos[1]:
                return False
            if target[0] < self.pos[0]:
                x_step = -1
            else:
                x_step = 1
              
            if target[1] < self.pos[1]:
                y_step = -1
            else:
                y_step = 1
                    
            for n in range(makeP(target[0]-self.pos[0])):
                if content[(self.pos[1] + n * y_step) * width + (self.pos[0] + n * x_step)] == '0':
                    return False
                if self.pos[1] + n * y_step != self.pos[1] and self.pos[0] + n * x_step != self.pos[0]:
                    if piece_matrix[self.pos[1] + n * y_step][self.pos[0] + n * x_step] != 0:
                        return False
                        
            if piece_matrix[self.pos[1] + (n+1) * y_step][self.pos[0] + (n+1) * x_step] == 0:
                return True
            else:
                if pieces[piece_matrix[self.pos[1] + (n+1) * y_step][self.pos[0] + (n+1) * x_step]].team_id != self.team_id:
                    return True
            
            return False
        
        
        def move(self, target):
            global piece_matrix
            if self.viable_move(target) and time.time() - self.cooldown > defoult_cd * 60:
                update_db_map(self.pos, 0)
                update_db_map(target, self)
                
                target = [round(target[0]), round(target[1])]
                piece_matrix[self.pos[1]][self.pos[0]], piece_matrix[target[1]][target[0]] = 0, piece_matrix[self.pos[1]][self.pos[0]]
                self.pos = [target[0], target[1]]
                self.cooldown = time.time()
                

        def render(self):
            screen.blit(pygame.transform.scale(self.imp, (round(zoom_factor), round(zoom_factor))), ((self.pos[0]+x_adj) *
                        zoom_factor + x_adj_pix, (self.pos[1]+y_adj) * zoom_factor + y_adj_pix))
        
        
    class Queen:
        imp = pygame.image.load("Textures\\qw.png")
        db_caption = 'queen'

        def __init__(self, pos, team_id, has_moved=False):
            self.pos = pos
            self.team_id = team_id
            self.has_moved = has_moved
            self.cooldown = time.time()

        def viable_move(self, target):
            global content
            global width
            global height
            y_step, x_step = 0, 0
            a = 0
            target = [round(target[0]), round(target[1])]
            if content[target[1] * width + target[0]] == '0':
                return False
            if target[0] != self.pos[0] and target[1] != self.pos[1]:
                if makeP(target[0]-self.pos[0]) != makeP(target[1]-self.pos[1]):
                    return False
            if target[0] == self.pos[0] and target[1] == self.pos[1]:
                return False
            if target[0] < self.pos[0]:
                x_step = -1
                a = makeP(target[0]-self.pos[0])
            elif target[0] > self.pos[0]:
                x_step = 1
                a = makeP(target[0]-self.pos[0])
              
            if target[1] < self.pos[1]:
                y_step = -1
                a = makeP(target[1]-self.pos[1])
            elif target[1] > self.pos[1]:
                y_step = 1
                a = makeP(target[1]-self.pos[1])
            for n in range(a):
                if content[(self.pos[1] + n * y_step) * width + (self.pos[0] + n * x_step)] == '0':
                    return False
                if self.pos[1] + n * y_step != self.pos[1] or self.pos[0] + n * x_step != self.pos[0]:
                    if piece_matrix[self.pos[1] + n * y_step][self.pos[0] + n * x_step] != 0:
                        return False
                        
            if piece_matrix[self.pos[1] + (n+1) * y_step][self.pos[0] + (n+1) * x_step] == 0:
                return True
            else:
                if pieces[piece_matrix[self.pos[1] + (n+1) * y_step][self.pos[0] + (n+1) * x_step]].team_id != self.team_id:
                    return True
            
            return False

        def move(self, target):
            global piece_matrix
            if self.viable_move(target) and time.time() - self.cooldown > defoult_cd * 60:
                update_db_map(self.pos, 0)
                update_db_map(target, self)
                
                target = [round(target[0]), round(target[1])]
                piece_matrix[self.pos[1]][self.pos[0]], piece_matrix[target[1]][target[0]] = 0, piece_matrix[self.pos[1]][self.pos[0]]
                self.pos = [target[0], target[1]]
                self.cooldown = time.time()
                

        def render(self):
            screen.blit(pygame.transform.scale(self.imp, (round(zoom_factor), round(zoom_factor))), ((self.pos[0]+x_adj) *
                        zoom_factor + x_adj_pix, (self.pos[1]+y_adj) * zoom_factor + y_adj_pix))
            
            
    class Pawn:
        imp = pygame.image.load("Textures\\pw.png")
        db_caption = 'pawn'

        def __init__(self, pos, team_id, has_moved=False):
            self.pos = pos
            self.team_id = team_id
            self.has_moved = has_moved
            self.cooldown = time.time()

        def viable_move(self, target):
            target = [round(target[0]), round(target[1])]
            if content[target[1] * width + target[0]] == '0':
                return False
            if makeP(self.pos[0] - target[0]) == 1 and makeP(self.pos[1] - target[1]) == 0:
                if piece_matrix[target[1]][target[0]] == 0:
                    return True
            elif makeP(self.pos[0] - target[0]) == 0 and makeP(self.pos[1] - target[1]) == 1:
                if piece_matrix[target[1]][target[0]] == 0:
                    return True
            else:
                if makeP(self.pos[0] - target[0]) == 1 and makeP(self.pos[1] - target[1]) == 1:
                    if piece_matrix[target[1]][target[0]] != 0:
                        if pieces[piece_matrix[target[1]][target[0]]].team_id != self.team_id:
                            return True
                elif makeP(self.pos[0] - target[0]) == 1 and makeP(self.pos[1] - target[1]) == 1:
                    if piece_matrix[target[1]][target[0]] != 0:
                        if pieces[piece_matrix[target[1]][target[0]]].team_id != self.team_id:
                            return True
            

        def move(self, target):
            global piece_matrix
            if self.viable_move(target) and time.time() - self.cooldown > defoult_cd * 60:
                update_db_map(self.pos, 0)
                update_db_map(target, self)
                
                target = [round(target[0]), round(target[1])]
                piece_matrix[self.pos[1]][self.pos[0]], piece_matrix[target[1]][target[0]] = 0, piece_matrix[self.pos[1]][self.pos[0]]
                self.pos = [target[0], target[1]]
                self.cooldown = time.time()
                

        def render(self):
            screen.blit(pygame.transform.scale(self.imp, (round(zoom_factor), round(zoom_factor))), ((self.pos[0]+x_adj) *
                        zoom_factor + x_adj_pix, (self.pos[1]+y_adj) * zoom_factor + y_adj_pix))
            
            
    class King:
        imp = pygame.image.load("Textures\\kw.png")
        db_caption = 'king'

        def __init__(self, pos, team_id, has_moved=False):
            self.pos = pos
            self.team_id = team_id
            self.has_moved = has_moved
            self.cooldown = time.time()

        def viable_move(self, target):
            target = [round(target[0]), round(target[1])]
            if content[target[1] * width + target[0]] == '0':
                return False
            if piece_matrix[target[1]][target[0]] != 0:
                if pieces[piece_matrix[target[1]][target[0]]].team_id == self.team_id:
                    return False
                
            if makeP(target[0] - self.pos[0]) == 1 and makeP(target[1] - self.pos[1]) == 1:
                return True
            
            elif makeP(target[0] - self.pos[0]) == 0 and makeP(target[1] - self.pos[1]) == 1:
                return True
            
            elif makeP(target[0] - self.pos[0]) == 1 and makeP(target[1] - self.pos[1]) == 0:
                return True
            

        def move(self, target):
            global piece_matrix
            if self.viable_move(target) and time.time() - self.cooldown > defoult_cd * 60:
                update_db_map(self.pos, 0)
                update_db_map(target, self)
                
                target = [round(target[0]), round(target[1])]
                piece_matrix[self.pos[1]][self.pos[0]], piece_matrix[target[1]][target[0]] = 0, piece_matrix[self.pos[1]][self.pos[0]]
                self.pos = [target[0], target[1]]
                self.cooldown = time.time()
                

        def render(self):
            screen.blit(pygame.transform.scale(self.imp, (round(zoom_factor), round(zoom_factor))), ((self.pos[0]+x_adj) *
                        zoom_factor + x_adj_pix, (self.pos[1]+y_adj) * zoom_factor + y_adj_pix))
            
            
    class Caption:
        font_file_directory = 'Panton-BlackCaps.otf'
        def __init__(self, pos, text, size):
            self.pos = pos
            self.text = text
            self.size = size
            
        def render(self, papa_pos):
            my_font = pygame.font.Font(self.font_file_directory, self.size)
            text_surface = my_font.render(self.text, False, (0, 0, 0))
            screen.blit(text_surface, (self.pos[0]+papa_pos[0],self.pos[1]+papa_pos[1]))
            
            
    class Button:
        def __init__(self, pos, size, caption, func):
            self.pos = pos
            self.size = size
            self.caption = caption
            self.func = func
            
        def render(self, papa_pos):
            pygame.draw.rect(screen, (60,179,113), (self.pos[0]+papa_pos[0], self.pos[1]+papa_pos[1], self.size[0], self.size[1]))
            mpos = pygame.mouse.get_pos()
            if mpos[0] > self.pos[0] + papa_pos[0] and mpos[0] < self.pos[0] + papa_pos[0] + self.size[0]:
                if mpos[1] > self.pos[1] + papa_pos[1] and mpos[1] < self.pos[1] + papa_pos[1] + self.size[1]:
                    pygame.draw.rect(screen, (0,100,0), (self.pos[0]+papa_pos[0], self.pos[1]+papa_pos[1], self.size[0], self.size[1]))
            self.caption.render((self.pos[0]+papa_pos[0], self.pos[1]+papa_pos[1]))
            
        def logic(self, papa_pos):
            mpos = pygame.mouse.get_pos()
            if mpos[0] > self.pos[0] + papa_pos[0] and mpos[0] < self.pos[0] + papa_pos[0] + self.size[0]:
                if mpos[1] > self.pos[1] + papa_pos[1] and mpos[1] < self.pos[1] + papa_pos[1] + self.size[1]:
                    if self.func():
                        return 2
                    return 1
            return 0
            
    
    class Table:
        background_color = (192,192,192)
        def __init__(self, pos, size, buttons, captions):
            self.pos = pos
            self.size = size
            self.buttons = buttons
            self.captions = captions
            buttons.append(Button([size[0]-25, 5], [15, 15], Caption([3,0], 'X', 14), close_table_func))
            
        def render(self):
            caption_offset = [0, 25]
            pygame.draw.rect(screen, self.background_color, (self.pos[0], self.pos[1], self.size[0], self.size[1]))
            for button in self.buttons:
                button.render(self.pos)
            for caption in self.captions:
                if caption.pos[0] + len(caption.text) * caption.size > self.size[0]:
                    a = self.split_caption(caption)
                    for sub_caption in a:
                        sub_caption.render([self.pos[0]+caption_offset[0], self.pos[1]+caption_offset[1]])
                else:
                    caption.render([self.pos[0]+caption_offset[0], self.pos[1]+caption_offset[1]])
                
        def split_caption(self, caption):
            words_line = 0
            lines = 0
            chars = (self.size[0] - caption.pos[1]) // caption.size
            chars_left = chars
            s = caption.text.split(' ')
            output_s = ''
            output_captions = []
            for word in s:
                
                if len(word) <= chars_left:
                    output_s += word + ' '
                    chars_left -= len(word)
                    words_line += 1
                else:
                    if words_line == 0:
                        output_s += word
                    output_captions.append(Caption([caption.pos[0], caption.pos[1] + lines*caption.size], output_s, caption.size))
                    output_s = ''
                    chars_left = chars
                    lines += 1
                    words_line = 0
                    
                    output_s += word + ' '
                    chars_left -= len(word)
                    words_line += 1
            output_captions.append(Caption([caption.pos[0], caption.pos[1] + lines*caption.size], output_s, caption.size))
            return output_captions
                        
        def is_pressed(self):
            mpos = pygame.mouse.get_pos()
            if mpos[0] > self.pos[0] and mpos[0] < self.pos[0] + self.size[0]:
                if mpos[1] > self.pos[1] and mpos[1] < self.pos[1] + self.size[1]:
                    return True
            return False
                
    move_piece_id = 0
    def make_move_func(piece_id):
        def btn_func():
            global move_piece_id
            move_piece_id = piece_id
            return True
        return btn_func
            
    def close_table_func():
        return True
        
    def but_example():
        return True
    tables = []
    spawn_structure = [[0,    Pawn, Pawn,    0],
                       [Pawn, Horse, Bishop, Pawn],
                       [Rook, King,  Queen,  Rook],
                       [Pawn, Bishop, Horse, Pawn],
                       [0,    Pawn, Pawn,    0]]
    
    
    next_player_id = 1
    def is_occupied(pos):
        if content[pos[1] * width + pos[0]] == '0':
            return True
        if piece_matrix[pos[1]][pos[0]] != 0:
            return True
        return False
    
    def viable_spawn_point(pos):
        for y in range(len(spawn_structure)):
            for x in range(len(spawn_structure[y])):
                if is_occupied([pos[0] + x,  pos[1] + y]):
                    return False
        return True
        
    def spawn_player(pos):
        global spawn_structure
        global client_team_id
        if not viable_spawn_point(pos):
            return False
        for y in range(len(spawn_structure)):
            for x in range(len(spawn_structure[y])):
                if spawn_structure[y][x] != 0:
                    new_piece(spawn_structure[y][x]([pos[0]+x, pos[1]+y], client_team_id)) 
        return True
    
    if register_new_pokemon:
        while not spawn_player((random.randint(0, width-1), random.randint(0, height-1))):
            pass
    
    
    last_update = 1
    captions = {
        'pawn': Pawn,
        'horse': Horse,
        'bishop': Bishop,
        'rook': Rook,
        'king': King,
        'queen': Queen
    }
    

    run = True
    while run:
        pygame.draw.rect(screen, (25, 25, 25), (0, 0, width, height))
        
        p = db.child('updates').get().val()
        if 1 in p:
            p[1] = {'1': p[1][1]}
        for i in range(last_update, len(p)):
            change = p[i][str(i)]
            if change['id'] == 0:
                piece_matrix[change['y']][change['x']] = 0
                continue
            new_piece(captions[change['piece']]([change['x'], change['y']], change['id'], change['moved']), False)
        last_update = len(p)
            
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEWHEEL:

                if event.y < 0 and zoom_factor / (-event.y+1) >= 1:
                    zoom_factor //= (-event.y+1)
                    x_adj += width // zoom_factor // 4
                    y_adj += height // zoom_factor // 4
                elif event.y > 0:
                    zoom_factor *= (event.y+1)
                    x_adj -= width // zoom_factor // 2
                    y_adj -= height // zoom_factor // 2

            elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                tile_size = 1 * zoom_factor
                break_loop = False
                for n in range(len(tables)-1, -1, -1):
                    for btn in tables[n].buttons:
                        a = btn.logic(tables[n].pos)
                        #code 1 - dont close the table
                        if a == 1:
                            break_loop = True
                        #code 2 - close the table
                        elif a == 2:
                            tables.pop(n)
                            break_loop = True
                            break
                    if break_loop:
                        break
                    if tables[n].is_pressed():
                        break_loop = True
                    if break_loop:
                        break
                if break_loop:
                    continue
                was_selected = selected_tile
                selected_tile = [(pos[0]-x_adj_pix)//tile_size -
                                 round(x_adj), (pos[1]-y_adj_pix)//tile_size - round(y_adj)]

                if was_selected[0] == selected_tile[0] and was_selected[1] == selected_tile[1]:
                    selected_tile = [0, 0]
                else:
                    if piece_matrix[round(selected_tile[1])][round(selected_tile[0])] != 0:
                        if pieces[piece_matrix[round(selected_tile[1])][round(selected_tile[0])]].team_id == client_team_id:
                            if time.time() - pieces[piece_matrix[round(selected_tile[1])][round(selected_tile[0])]].cooldown > defoult_cd*60:
                                tables.append(Table([150, 150], [150, 150], [Button([25, 120], [100, 20], Caption([10, 2], 'Move', 12), 
                                                    make_move_func(piece_matrix[round(selected_tile[1])][round(selected_tile[0])]))], 
                                                    [Caption([20, 20], 'The piece is ready to move', 15)]))
                            else:
                                tables.append(Table([150, 150], [150, 150], [], 
                                                    [Caption([20, 20], str(round(pieces[piece_matrix[round(selected_tile[1])][round(selected_tile[0])]].cooldown 
                                                                                 + defoult_cd*60 - time.time())) + ' seconds until the piece can move', 13)]))
                                
                                
                        elif move_piece_id != 0:
                            if move_piece_id != 0:
                                pieces[move_piece_id].move(selected_tile)
                                selected_tile = [0, 0]
                                move_piece_id = 0
                    else:
                        if move_piece_id != 0:
                            pieces[move_piece_id].move(selected_tile)
                            selected_tile = [0, 0]
                            move_piece_id = 0

        camera_sens = 7
        if keyboard.is_pressed('w'):
            y_adj_pix += camera_sens
        if keyboard.is_pressed('s'):
            y_adj_pix -= camera_sens
        if keyboard.is_pressed('a'):
            x_adj_pix += camera_sens
        if keyboard.is_pressed('d'):
            x_adj_pix -= camera_sens
            
        x_adj += x_adj_pix // zoom_factor
        x_adj_pix = x_adj_pix % zoom_factor
        y_adj += y_adj_pix // zoom_factor
        y_adj_pix = y_adj_pix % zoom_factor

        if x_adj > 0:
            x_adj = 0
        if y_adj > 0:
            y_adj = 0
        if width/zoom_factor - x_adj > width:
            x_adj = width/zoom_factor - width
        if height/zoom_factor - y_adj > height:
            y_adj = height/zoom_factor - height
        for y in range(math.floor(-y_adj)-1, math.ceil(height / zoom_factor - y_adj)):
            for x in range(math.floor(-x_adj)-1, math.ceil(width / zoom_factor - x_adj)):
                color_id = int(content[y * width + x])
                if x == selected_tile[0] and y == selected_tile[1]:
                    color_id = 3
                xpos, ypos = (x + x_adj) * zoom_factor + x_adj_pix, (y + y_adj) * zoom_factor + y_adj_pix
                pygame.draw.rect(
                    screen, color_pallete[color_id], (xpos, ypos, 1*zoom_factor, 1*zoom_factor))

        for y in piece_matrix:
            for x in y:
                if x != 0:
                    pieces[x].render()
                    
        for n in tables:
            n.render()
                    

        pygame.display.update()
    pygame.quit
