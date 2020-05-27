import numpy as np
import pygame

class radar:
    
    def __init__(self, x,y,w,h):

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.rays_specs = np.empty((0, 3))

        self.ray_range = 200

    def add_ray(self, star_x, start_y, degree):
    
        # if np.all(self.rays_specs[0,:] == np.array([0,0,0])):
    
        #     self.rays_specs[0] = np.array([star_X,start_y,degree])
        
        # else:

        self.rays_specs = np.vstack((self.rays_specs, np.array([star_x,start_y,degree])))

    def update_x_rays(self, move):

        for n, ray in enumerate(self.rays_specs):

            self.rays_specs[n][0] += move



    def check_radar(self, display):

        w, h = pygame.display.get_surface().get_size()

        self.rays = np.empty((0, 3))
        
        for ray in self.rays_specs:
        
            length = 0
        
            x = int(ray[0] + np.cos(np.radians(360 - ray[2])) * length)
            y = int(ray[1] + np.sin(np.radians(360 - ray[2])) * length)

            dist = int(np.sqrt(np.power(x - ray[0], 2) + np.power(y - ray[1], 2)))

            
            # print(length)

            # print(x,y)

            if x > w/2:

                try:
                    pixel = display.get_at((x-1,y-1))

                except:
                    pixel = display.get_at((598,y-1))

            else:

                try: 
                    pixel = display.get_at((x+1,y-1))

                except:
                    pixel = display.get_at((1,y-1))


            while ((pixel == (0, 133, 185, 255)) or (pixel == (173, 0, 156,255)) or (pixel == (255, 202, 24))) and (dist < self.ray_range):
                
                length += 3
                
                x = int(ray[0] + np.cos(np.radians(360 - ray[2])) * length)
                y = int(ray[1] + np.sin(np.radians(360 - ray[2])) * length)

                dist = int(np.sqrt(np.power(x - ray[0], 2) + np.power(y - ray[1], 2)))
                

                # dist = int(np.sqrt(np.power(x,2) + np.power(y,2)))
                    

                if ((x < 0) or (x > w)) or ((y < 0) or (y > h)):

                    break

                if x > w/2:
                    pixel = display.get_at((x-1,y-1))

                else:
                    pixel = display.get_at((x+1,y-1))

            if dist > self.ray_range:

                dist = 400

            self.rays = np.vstack((self.rays, np.array([(ray[0],ray[1]), (x,y), dist])))
        
    def draw_radar(self, display, color = (173, 0, 156)):

        for ray in self.rays:

            start, end, dist = ray

            pygame.draw.line(display, color, start, end, 1)
            # pygame.draw.circle(display, color, end, 5)

    def get_dists(self):

        dists = np.array([])

        dists_normalized = np.array([])

        for ray in self.rays:

            dists = np.append(dists, ray[2])

        for dist in dists:

            dists_normalized = np.append(dists_normalized, dist/self.ray_range)

        return dists, dists_normalized




        


                  

        