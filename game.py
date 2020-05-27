import pygame as pygame
import numpy as np
import time
import random
import neat
import os
import visualize


import radar

engine_tick = 0.5


black = (0,0,0)
white_ = (255,255,255)
gray = (100,100,100)
red = (255,0,0)

background_blue = (0, 133, 185)

dimensions = {'display': (600,900),  
                'pedra_1': (55,35),
                'pedra_2': (65,43),
                'shark': (155,55),
                'player': (40,40),
                'wave': (100,35),
                'foca': (150,165),
                'foca_rei': (169,250),
                'normal_egg': (25,28),
                'golden_egg' : (32,39),
                'radar_block' : (90,90)
                }

fps = 60
corte = 0

player_image = pygame.image.load('assets/player_image.png')

pygame.display.set_icon(player_image)

shark = pygame.image.load('assets/shark.png')



ondas = ['onda_hm_1','onda_hm_2','onda_hm_3','onda_hm_2','onda_hm_1']


def mask(obstacle):
    
    a = pygame.mask.from_surface(obstacle)

    return a

generation = -1

high_score = 0

def game_loop(genomes,config):

    global generation
    global high_score
        
    generation +=1

    def player(x, y):
        gameDisplay.blit(player_image,(x,y))

    def generate_obstacle(obstacle, x, y):

        loaded_obstacle = pygame.image.load(f'assets/{obstacle}.png')
        gameDisplay.blit(loaded_obstacle, (x,y))

    def text_objects(text, font):
        text_surf = font.render(text, True, black)

        return text_surf, text_surf.get_rect()
        
    def message_display(text, x = 0.5, y = 0.35, size = 60):
        text_format = pygame.font.Font('fonts/PressStart2P-Regular.ttf', size)
        text_surf, text_rect = text_objects(text, text_format)
        text_rect.center = (dimensions['display'][0] * x, dimensions['display'][1] * y)
        gameDisplay.blit(text_surf, text_rect)


    pygame.init()
    gameDisplay = pygame.display.set_mode((dimensions['display'][0],dimensions['display'][1]))
    pygame.display.set_caption('River')
    clock = pygame.time.Clock()

    gameDisplay.fill(background_blue)

    # Defining borders for colision purposes
    pygame.draw.line(gameDisplay, red, (0,0), (0,dimensions['display'][1]))
    pygame.draw.line(gameDisplay, red, (dimensions['display'][0] -1, 0), (dimensions['display'][0] -1, dimensions['display'][1]))

    pygame.display.update()

    start_x = 280
    start_y = 720

    nets = []
    ge = []
    ducks = []
    sonars = []

    for _,g in genomes:

        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        ducks.append([str(random.uniform(0, 1)),start_x, start_y,0])
        g.fitness = 0
        ge.append(g)

        sonars.append(radar.radar(start_x, start_y, dimensions['player'][0], dimensions['player'][1]))

    # Initializing the sonar for each duck

    for n, duck in enumerate(ducks):

        sonars[n].add_ray(duck[1], duck[2] + dimensions['player'][1] + 1, 180)

        sonars[n].add_ray(duck[1], duck[2], 180)
        sonars[n].add_ray(duck[1], duck[2], 150)
        sonars[n].add_ray(duck[1], duck[2], 120)
        sonars[n].add_ray(duck[1], duck[2], 90)


        sonars[n].add_ray(duck[1] + dimensions['player'][0], duck[2], 90)
        sonars[n].add_ray(duck[1] + dimensions['player'][0], duck[2], 60)
        sonars[n].add_ray(duck[1] + dimensions['player'][0], duck[2], 30)
        sonars[n].add_ray(duck[1] + dimensions['player'][0], duck[2], 0)

        sonars[n].add_ray(duck[1] + dimensions['player'][0] , duck[2] + dimensions['player'][1] + 2, 0)
        # print(duck[2] + dimensions['player'][1])
    print('Sonares Criados')   


    points = 0

    distance_traveled = 0

    speed_factor = 1

    horizontal_move = 7 * (1/engine_tick)

    map_yspeed = 2 * (1/engine_tick)

    rock_xspeed = 0

    obstacles = {}

    start_time = 0

    game_exit = False

    counter = 0

    course_x = 0

    course_left_to_right = True


    block = pygame.Surface((dimensions['radar_block'][0],dimensions['radar_block'][1]), pygame.SRCALPHA)

    block.fill(red)


    images = {'player': player_image,
            'pedra_1': pygame.image.load('assets/pedra_1.png'),
            'pedra_2': pygame.image.load('assets/pedra_2.png'),
            'radar_block' : block
            }

    masks = {'player' : mask(images['player']),
            'pedra_1': mask(images['pedra_1']),
            'pedra_2': mask(images['pedra_2']),
            'radar_block': mask(images['radar_block'])
            
            }


    while game_exit == False:

        if len(ducks) == 0:
            game_exit = True
            break

        for g in ge:

            g.fitness += map_yspeed * speed_factor
            g.fitness = 0



        points += map_yspeed  * speed_factor

        distance_traveled += map_yspeed  * speed_factor

        speed_factor = 1 * (1 + 5 * (distance_traveled/100000))

        rock_number = 10

        ################################### Input ###################################

        counter +=1

        radares = {}

        for n, duck in enumerate(ducks):


            if f'{sonars[n].x}-{sonars[n].y}' in list(radares.keys()):
                
                inputs = radares[f'{sonars[n].x}-{sonars[n].y}']
            
            else:

                sonars[n].check_radar(gameDisplay)

                inputs = sonars[n].get_dists()

                radares[f'{sonars[n].x}-{sonars[n].y}'] = inputs


            output = nets[n].activate(inputs[1])

            i = output.index(max(output))

            if i == 0 :

                ducks[n][1] += horizontal_move

                sonars[n].update_x_rays(horizontal_move)

            elif i == 1 :

                ducks[n][1] += -horizontal_move

                sonars[n].update_x_rays(-horizontal_move)

            elif i == 2:

                pass


            if counter%120 == 0:

                if n == 0:
                    
                    print(inputs)
                    print(output)


        ################################### Input ###################################

        gameDisplay.fill(background_blue)
        pygame.draw.line(gameDisplay, red, (0,0), (0,dimensions['display'][1]))
        pygame.draw.line(gameDisplay, red, (dimensions['display'][0] -1, 0), (dimensions['display'][0] -1, dimensions['display'][1]))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True
                pygame.quit()
                break


        # Ccreating obstacles

        if start_time < 30:

            start_time +=1
        
        else:

            ############################ Training Circuit ############################
            
            if distance_traveled < 10000:

                if counter %10 ==0:

                    item_id = random.uniform(0, 1)

                    a = [f'pedra_2', course_x, 100 , dimensions[f'pedra_2'][0], dimensions[f'pedra_2'][1], rock_xspeed, map_yspeed]

                    obstacles[f'course_{item_id}'] = a

                    if course_left_to_right == True:

                        if  course_x < (dimensions['display'][0]/2):
                    
                            course_x += 70

                        else:
                            
                            course_left_to_right = False

                            course_x = dimensions['display'][0] - dimensions['pedra_2'][0]

                            start_time = 0

                    else:

                        if  course_x > dimensions['display'][0]/3:

                            course_x -= 70


                        else:

                            course_left_to_right = True

                            course_x = 0 

                            start_time = 0

            #################################################################################

            # After training circuit ends, game starts generating random placed rocks
            

            else:

                complete_list = [f'rock{i}' for i in range(rock_number)]
                current_list = [name for name in list(obstacles.keys()) if 'rock' in name]

                missing_list = set(complete_list) - set(current_list)

                for n in missing_list:
                    rock_n = random.randrange(1,3)

                    a = [f'pedra_{rock_n}', random.randrange(0 , dimensions['display'][0] - dimensions[f'pedra_{rock_n}'][0]), - random.randrange(dimensions[f'pedra_{rock_n}'][1], 600), dimensions[f'pedra_{rock_n}'][0], dimensions[f'pedra_{rock_n}'][1], rock_xspeed, map_yspeed]

                    obstacles[n] = a


        
        for obstacle in list(obstacles):

            obstacles[obstacle][2] += obstacles[obstacle][6] * speed_factor
            obstacles[obstacle][1] += obstacles[obstacle][5] * random.uniform(0.5, 1.5)

            generate_obstacle(obstacles[obstacle][0], obstacles[obstacle][1], obstacles[obstacle][2])

            if obstacles[obstacle][2] > dimensions['display'][1]:

                del obstacles[obstacle]



        # Colision System

        for n, duck in enumerate(ducks):

            for obstacle in list(obstacles):
                
                if obstacles[obstacle][2] > 650:

                    if len(ducks) == 0:
                        break
                    player_image

                    obstacle_mask = masks[obstacles[obstacle][0]]
                    

                    n = ducks.index(duck)

                    offset = (round(obstacles[obstacle][1] - ducks[n][1]), round(obstacles[obstacle][2] - ducks[n][2]))

                    colision_point = masks['player'].overlap(obstacle_mask, offset)

                    if colision_point != None:

                        if 'normal_egg' in obstacles[obstacle][0]:

                            for duck in enumerate(ducks):
                            
                                ducks[n][3] += 100

                            del obstacles[obstacle]

                        elif 'golden_egg' in obstacles[obstacle][0]:

                            for duck in enumerate(ducks):
                            
                                ducks[n][3] += 1000

                            del obstacles[obstacle]

                        else:

                            ducks.pop(n)
                            nets.pop(n)
                            ge.pop(n)
                            sonars.pop(n)

                            break

        # End of colision system

        # Drawing Ducks

        for n, duck in enumerate(ducks):

            n = ducks.index(duck)

            if (ducks[n][1] > dimensions['display'][0] - dimensions['player'][0]) or (ducks[n][1] < 0):
                ducks.pop(n)
                nets.pop(n)
                ge.pop(n)
                sonars.pop(n)

        for n, duck in enumerate(list(ducks)):

            player(ducks[n][1], ducks[n][2])


        # HUD

        if points > high_score:

            high_score = points

        message_display(str(round(points/10)), 0.8,  0.1, 20)

        message_display(f'High Score: {round(high_score/10)}', 0.3,  0.2, 20)

        message_display(f'Alive: {len(ducks)}', 0.3,  0.15, 20)

        message_display(f'Generation {generation}', 0.3,  0.1, 20)

        try:
            if len(sonars) > 0:

                sonars[0].draw_radar(gameDisplay)

        except:
            pass

        pygame.display.update()
        clock.tick(60 * engine_tick)

    pygame.quit()


def run(config_path):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
        	                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))

    global stats
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(game_loop, 10)

    print('\nBest genome:\n{!s}'.format(winner))

    # winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    visualize.draw_net(config, winner, True)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)




if __name__ == '__main__':

    run('config-feedforward.txt')