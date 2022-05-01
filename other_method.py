# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 19:53:39 2022

@author: michael
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 14:11:08 2022

@author: michael
"""


#the ratio between the pygame map and the real world map is 9:1 
import numpy as np 
import pygame 
import math 
import random as r
from scipy.stats import norm
import matplotlib.pyplot as plt
from time import process_time

green = (0 , 255 , 0)
red = (0 , 0 , 0)
blue = (0 ,0 , 255)
estimcol = (100 , 100 , 255)
white = (255 ,255 , 255)
col  = (252, 3, 219)
black = (0 ,0 ,0)

pygame.init()
dimx , dimy = 800 , 800
surface = pygame.display.set_mode((dimx , dimy))
img = pygame.image.load('icairmap.png')
img = pygame.transform.scale(img , (dimx , dimy))
step1 = 9
stepp = 9
threshold = 9*3
number_particles = 300
angle_uncertainty = np.deg2rad(30)
step_uncertainty = 3

manholes= [(570 , 550) , (480 , 550) , (300 , 520) , (240, 510), (330 , 350 ) , (300 , 350 )]
#manholes = [(100 , 200) , (700 , 200)]          
        
def plot_manholes(manholes) :
    for point in manholes :
        draw = pygame.draw.circle(surface, green, (point[0] , point[1]) , 5)
    for i in range(1 , len( manholes)) :
        lines = pygame.draw.line(surface , black , (manholes[i-1][0],manholes[i-1][1]) ,  (manholes[i][0],manholes[i][1]) )                         
    pygame.display.flip() 
 
starting_point =  manholes[0]
location = starting_point
n = manholes.index(location)


def move(location,  n):
    if event.key == pygame.K_RIGHT :       
        step = np.random.normal(stepp, step_uncertainty ) 
        x = manholes[n+1][0] - manholes[n][0]
        y = manholes[n+1][1] - manholes[n][1]  
        grad = y/x 
        angle = np.arctan(y/x)
        if grad != 0 and x > 0 :                                                          
            locationx = location[0] + np.cos(angle)*step
            locationy = location[1] + np.sin(angle)*step
            location = (round(locationx , 2), round(locationy , 2))   
        if grad == 0 and location[0] > manholes[n+1][0]:
            locationx = location[0] - np.cos(angle)*step
            locationy = location[1] + np.sin(angle)*step
            location = (np.round(locationx ,2) , np.round(locationy ,2))             
        if grad == 0 and location[0] < manholes[n+1][0]:
            locationx = location[0] + np.cos(angle)*step
            locationy = location[1] + np.sin(angle)*step
            location = (np.round(locationx , 2) , np.round(locationy ,2 ))                             
        if grad != 0 and x < 0 :
            locationx = location[0] - np.cos(angle)*step
            locationy = location[1] - np.sin(angle)*step
            location = (np.round(locationx , 2), np.round(locationy , 2))    
        return location 
        
 
def sense(location , n , stepp):      
    distance = np.sqrt((manholes[n+1][0] - location[0])**2 + (manholes[n+1][1] - location[1])**2)
    distance = np.sqrt((manholes[n+1][0] - location[0])**2 + (manholes[n+1][1] - location[1])**2) + np.random.normal(0, distance/9) 
    if distance < 4: 
        stepp =  2  
        location = manholes[n+1]
        n +=1 
       # return n , location  , distance , stepp
    else:
           n = n
           stepp = step1
    return n  , location , distance , stepp




particle_location = location
particle_angle = []
particle_listi = []


def move_particles(particle_location):        
    if event.key == pygame.K_RIGHT :
        x = manholes[n+1][0] - manholes[n][0]
        y = manholes[n+1][1] - manholes[n][1]  
        grad = y/x   
        #angle_particle = np.arctan(y/x) + np.random.normal(0, 1) 
        angle_particle = np.random.normal(np.arctan(grad), angle_uncertainty , number_particles) 
       # particle_angle.append(angle_particle)
        step_particle = np.random.normal(stepp, step_uncertainty, number_particles)            
        if grad != 0 and x > 0 :                                                          
            locationx = particle_location[0] + np.cos(angle_particle)*step_particle
            locationy = particle_location[1] + np.sin(angle_particle)*step_particle
            particle_location = (np.round(locationx , 2), np.round(locationy , 2))   
        if grad == 0 and np.mean(particle_location[0]) > manholes[n+1][0]:
            locationx = particle_location[0] - np.cos(angle_particle)*step_particle
            locationy = particle_location[1] + np.sin(angle_particle)*step_particle
            particle_location = (np.round(locationx) , np.round(locationy))    
        if grad == 0 and np.mean(particle_location[0]) < manholes[n+1][0]:
            locationx = particle_location[0] + np.cos(angle_particle)*step_particle
            locationy = particle_location[1] + np.sin(angle_particle)*step_particle
            particle_location = (np.round(locationx ,2 ) , np.round(locationy ,2 ))   
        if  grad != 0 and x < 0 :
             locationx = particle_location[0] - np.cos(angle_particle)*step_particle
             locationy = particle_location[1] - np.sin(angle_particle)*step_particle
             particle_location = (np.round(locationx , 2), np.round(locationy , 2))   
        particle_listi.append(particle_location)  
        return particle_location 
     

def particle_sense(particle_location , n ):
    particle_distance = np.sqrt((manholes[n+1][0] - particle_location[0])**2 + (manholes[n+1][1] - particle_location[1])**2)  
    sd = np.std(particle_distance)  
    return particle_distance , sd


def weight(distance , particle_distance ):
    weight_particle  = norm.pdf(particle_distance, distance, 1 )  
    return weight_particle


def resample(weight_particle , particle_location ):
    particle_list = list(zip(particle_location[0] , particle_location[1]))  
    resample = r.choices(particle_list , weight_particle , k = number_particles)
    particle_location = list(zip(*resample))  
    return particle_location

def resasmple2(particle_location , sd ):
    particle_list = list(zip(particle_location[0] , particle_location[1]))
    skew_set =  2 * norm.pdf(particle_list) * norm.cdf(sd*particle_list)
    resample = r.choices(particle_list , skew_set , k = number_particles)
    
    
def normalize(weight_particle):
    normalized_weight = []
    maxp = np.max(weight_particle)
    minp = np.min(weight_particle)
    #for i in weight_particle:
    for i in weight_particle:
        
        normalized = (i - minp)/(maxp - minp)    
        if normalized > 0.5:                     
            normalized_weight.append(normalized)
        else:
            normalized_weight.append(0)
            
        normal= [normalized_weight , list(zip(particle_location[0] , particle_location[1]))]
        
            
    #the list normal has the first column , as the weight, second row as the location tuple 
    return weight_particle , normal
        
        
         
def estimated_location(particle_location , normal):
    estimatex = 0 
    estimatey = 0
    estim  = np.where(weight_particle ==  np.max(weight_particle))[0][0]
    no_estimatex = particle_location[0][estim]
    no_estimatey = particle_location[1][estim]
    count = 0 
    for i in range(number_particles -1 ):
        if normal[0][i] != 0 :
            estimatex += normal[1][i][0]
            estimatey += normal[1][i][1]
            count += 1
        
    estimatex = estimatex/count
    estimatey = estimatey/count
    #estim  = np.where(weight_particle ==  np.max(weight_particle))[0][0]
    # locat = []
    # for val in normal:
    #     loc = np.where(weight_particle == normal )[0][0]
    #     locat.append(loc)
        
    # estimatex = particle_location[0][estim]
    # estimatey = particle_location[1][estim]
    # pygame.draw.circle(surface, estimcol , (estimatex, estimatey) , 3)  
    # #rmse = np.sqrt(estimatex^2 - estimatey^2)
    
    
    
        
    return estimatex , estimatey , count


def estimated_location2(particle_location ):
    estimatex = np.mean(particle_location[0])
    estimatey = np.mean(particle_location[1])
    pygame.draw.circle(surface, estimcol , (estimatex, estimatey) , 3)  
    return estimatex , estimatey


xplt = []
yplt = []   
rmse = []
def data(estimatex , estimatey , location):
    xval = location[0] - estimatex
    yval = location[1] - estimatey
    yplt.append(yval) 
    xplt.append(xval)
    error = np.sqrt(yval**2 + xval**2)/9
    rmse.append(error)
    return xplt , yplt , rmse
           
 
estimated_trajectoryx = []
estimated_trajectoryy = []

step_count = []
step = 0 
while True : 
    pygame.display.update()  
    surface.fill(white) 
    
   # surface.blit(img, (0, 0))
    
    for event in pygame.event.get() : 
        if event.type == pygame.QUIT :               
            pygame.quit()
            quit()    
            
    if event.type == pygame.KEYDOWN:  
        t1_start = process_time()
        step_count.append(step)
        step += 1 
        
                
        if n == len(manholes)-1 :    
            n = 0
            manholes.reverse() 
            location = (manholes[0][0] , manholes[0][1])   
            n , location , distance , stepp  = sense(location , n , stepp )
        else :            
            location  = move(location, n)   
            pygame.draw.circle(surface, red, (location[0]  , location[1]) , 6)
            particle_location  = move_particles(particle_location) 
            for i in range(number_particles):
                xp = particle_location[0][i]
                yp = particle_location[1][i]
                pygame.draw.circle(surface, col, (xp , yp)  , 2) 
            particle_distance , sd  = particle_sense(particle_location , n )
            
            n , location , distance , stepp = sense(location , n , stepp )  
            

            if distance >= threshold:
               #estimatex , estimatey = estimated_location2(particle_location)
                #weight_particle = weight(distance , particle_distance)   
                #estimatex , estimatey = estimated_location(particle_location , weight_particle)
                estimatex , estimatey = estimated_location2(particle_location)
                
            if distance < threshold :

# =============================================================================
                 weight_particle = weight(distance , particle_distance) 
                 weight_particle , normal = normalize(weight_particle)
                 particle_location =  resample(weight_particle , particle_location )
                 estimatex , estimatey, count = estimated_location(particle_location , normal)

               
            
            estimated_trajectoryx.append(estimatex )
            estimated_trajectoryy.append(estimatey )           
            xplt , yplt , rmse  = data(estimatex , estimatey , location)
            t1_stop = process_time()   
            print(t1_stop - t1_start)
            # plt.plot(xplt) 
            # plt.plot(yplt)      
            plt.plot(rmse) 
         
        
          
    else :
        pygame.draw.circle(surface, red, (location[0]  , location[1]) , 6)  
    
                    
 
    #pygame.display.update() 
    
    if location in manholes:
        pygame.display.update()         
        surface.fill(white)                               
        pygame.time.delay(100)                  
        plot_manholes(manholes)  
    else :
        for i in range(number_particles):
            xp = particle_location[0][i]
            yp = particle_location[1][i]
            pygame.draw.circle(surface, col, (xp , yp)  , 2) 
            #estimated_location(particle_location , weight_particle)
        pygame.draw.circle(surface, red, (location[0]  , location[1]) , 6) 

    for p in range(len(estimated_trajectoryx)):
        pygame.draw.circle(surface, estimcol , (estimated_trajectoryx[p], estimated_trajectoryy[p]) , 3)

                 
    pygame.time.delay(100)                  
    plot_manholes(manholes)        
