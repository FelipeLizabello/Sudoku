import sys, pygame as pg
import os

pg.init()
screen_size = 1280, 720
screen = pg.display.set_mode(screen_size)

try:
    image_paths = [
        "../assets/background.jpg",
        "assets/background.jpg", 
        "../assets/background.png",
        "assets/background.png"
    ]
    
    background_image = None
    for path in image_paths:
        if os.path.exists(path):
            print(f"Carregando imagem: {path}")
            background_image = pg.image.load(path)
            background_image = pg.transform.scale(background_image, screen_size)
            break
    
    if background_image is None:
        print("Nenhuma imagem encontrada nos caminhos:")
        for path in image_paths:
            print(f"  {path} - {'EXISTS' if os.path.exists(path) else 'NOT FOUND'}")
        
except Exception as e:
    print(f"Erro ao carregar imagem: {e}")
    background_image = None

def draw_background():

    screen.fill(pg.Color("lightblue"))

    board_x = 280
    board_y = 0

    if background_image:
        left_area = pg.Rect(0, 0, board_x, 720)
        screen.blit(background_image, (0, 0), left_area)

        right_start = board_x + 720
        right_width = 1280 - right_start
        right_area = pg.Rect(right_start, 0, right_width, 720)
        screen.blit(background_image, (right_start, 0), pg.Rect(right_start, 0, right_width, 720))
    

    pg.draw.rect(screen, pg.Color("white"), pg.Rect(board_x + 10, board_y + 10, 700, 700))

    pg.draw.rect(screen, pg.Color("black"), pg.Rect(board_x, board_y, 720, 720), 10)
    i = 1
    while(i * 80) < 720:
        line_width = 5 if i % 3 > 0 else 10
        pg.draw.line(screen, pg.Color("black"), pg.Vector2((i * 80)+board_x, board_y), pg.Vector2((i * 80)+board_x, board_y + 720), line_width)
        pg.draw.line(screen, pg.Color("black"), pg.Vector2(board_x, (i * 80)+board_y), pg.Vector2(board_x + 720, (i * 80)+board_y), line_width)
        i += 1

def game_loop():
    for event in pg.event.get():
        if event.type == pg.QUIT: sys.exit()
    
    draw_background()
    pg.display.flip()


while 1:
    game_loop()
