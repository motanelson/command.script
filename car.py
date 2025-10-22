
import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class CarSimulator:
    def __init__(self):
        self.car_position = [0.0, 0.0, 0.0]
        self.car_speed = 0.0
        self.road_width = 8.0
        self.road_length = 100.0
        self.camera_distance = 10.0
        self.camera_height = 3.0
        self.steering_angle = 0.0
        
    def init_gl(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.53, 0.81, 0.98, 1.0)
        
    def draw_car_simple(self):
        glPushMatrix()
        glTranslatef(self.car_position[0], self.car_position[1] + 0.5, self.car_position[2])
        glRotatef(self.steering_angle, 0, 1, 0)
        
        # Corpo do carro (vermelho)
        glColor3f(1.0, 0.0, 0.0)
        self.draw_cuboid(1.5, 0.5, 3.0)
        
        # Teto do carro
        glColor3f(0.8, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        self.draw_cuboid(1.0, 0.3, 2.0)
        glPopMatrix()
        
        # Rodas simplificadas (cubos)
        glColor3f(0.1, 0.1, 0.1)
        wheel_positions = [
            (-1.0, -0.3, 1.0), (1.0, -0.3, 1.0),
            (-1.0, -0.3, -1.0), (1.0, -0.3, -1.0)
        ]
        
        for pos in wheel_positions:
            glPushMatrix()
            glTranslatef(*pos)
            self.draw_cuboid(0.3, 0.2, 0.3)
            glPopMatrix()
        
        glPopMatrix()
    
    def draw_cuboid(self, width, height, depth):
        # Desenhar um cuboide manualmente
        w, h, d = width/2, height/2, depth/2
        
        vertices = [
            [-w, -h, -d], [w, -h, -d], [w, h, -d], [-w, h, -d],
            [-w, -h, d], [w, -h, d], [w, h, d], [-w, h, d]
        ]
        
        faces = [
            [0, 1, 2, 3], [3, 2, 6, 7], [7, 6, 5, 4],
            [4, 5, 1, 0], [1, 5, 6, 2], [4, 0, 3, 7]
        ]
        
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
    
    def draw_road(self):
        # Desenhar a estrada amarela
        glColor3f(1.0, 0.84, 0.0)
        
        glBegin(GL_QUADS)
        glVertex3f(-self.road_width/2, 0.0, -self.road_length/2)
        glVertex3f(self.road_width/2, 0.0, -self.road_length/2)
        glVertex3f(self.road_width/2, 0.0, self.road_length/2)
        glVertex3f(-self.road_width/2, 0.0, self.road_length/2)
        glEnd()
        
        # Marcas da estrada
        glColor3f(1.0, 1.0, 1.0)
        stripe_width = 0.2
        stripe_length = 2.0
        gap_length = 4.0
        
        z = -self.road_length/2
        while z < self.road_length/2:
            glBegin(GL_QUADS)
            glVertex3f(-stripe_width/2, 0.01, z)
            glVertex3f(stripe_width/2, 0.01, z)
            glVertex3f(stripe_width/2, 0.01, z + stripe_length)
            glVertex3f(-stripe_width/2, 0.01, z + stripe_length)
            glEnd()
            z += stripe_length + gap_length
    
    def draw_environment(self):
        # Grama ao lado da estrada
        glColor3f(0.0, 0.6, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-20.0, 0.0, -self.road_length/2)
        glVertex3f(-self.road_width/2, 0.0, -self.road_length/2)
        glVertex3f(-self.road_width/2, 0.0, self.road_length/2)
        glVertex3f(-20.0, 0.0, self.road_length/2)
        
        glVertex3f(self.road_width/2, 0.0, -self.road_length/2)
        glVertex3f(20.0, 0.0, -self.road_length/2)
        glVertex3f(20.0, 0.0, self.road_length/2)
        glVertex3f(self.road_width/2, 0.0, self.road_length/2)
        glEnd()
    
    def setup_camera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (800/600), 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        camera_x = self.car_position[0] - np.sin(np.radians(self.steering_angle)) * self.camera_distance
        camera_z = self.car_position[2] - np.cos(np.radians(self.steering_angle)) * self.camera_distance
        camera_y = self.car_position[1] + self.camera_height
        
        gluLookAt(
            camera_x, camera_y, camera_z,
            self.car_position[0], self.car_position[1] + 1.0, self.car_position[2],
            0, 1, 0
        )
    
    def update(self, keys, dt):
        acceleration = 0.0
        steering = 0.0
        
        if keys[K_UP] or keys[K_w]:
            acceleration = 20.0
        if keys[K_DOWN] or keys[K_s]:
            acceleration = -15.0
        if keys[K_LEFT] or keys[K_a]:
            steering = 2.0
        if keys[K_RIGHT] or keys[K_d]:
            steering = -2.0
        
        self.car_speed += acceleration * dt
        self.car_speed *= 0.95
        
        self.steering_angle += steering * self.car_speed * dt
        
        self.car_position[0] += np.sin(np.radians(self.steering_angle)) * self.car_speed * dt
        self.car_position[2] += np.cos(np.radians(self.steering_angle)) * self.car_speed * dt
        
        self.car_position[0] = max(-self.road_width/2 + 0.5, min(self.road_width/2 - 0.5, self.car_position[0]))
        
        if self.car_position[2] > self.road_length/2:
            self.car_position[2] = -self.road_length/2
        elif self.car_position[2] < -self.road_length/2:
            self.car_position[2] = self.road_length/2
    
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.setup_camera()
        self.draw_environment()
        self.draw_road()
        self.draw_car_simple()
        
        pygame.display.flip()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Simulador de Condução 3D - Estrada Amarela")
    
    simulator = CarSimulator()
    simulator.init_gl()
    
    clock = pygame.time.Clock()
    
    print("Controles:")
    print("Setas/WASD: Controlar o carro")
    print("ESC: Sair")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        keys = pygame.key.get_pressed()
        simulator.update(keys, dt)
        simulator.draw()
    
    pygame.quit()

if __name__ == "__main__":
    main()