from PyQt6.QtWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

class ThreeDView(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.vehicle_attitude = {'roll': 0, 'pitch': 0, 'yaw': 0}
        self.camera_distance = 5.0
        self.camera_rotation = {'x': 30, 'y': 0}
        self.last_mouse_pos = None
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)  # ~60 FPS

    def initializeGL(self):
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        
        # Işık ayarları
        glLight(GL_LIGHT0, GL_POSITION, (5.0, 5.0, 5.0, 1.0))
        glLight(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLight(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h, 0.1, 100.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Kamera pozisyonu
        gluLookAt(
            self.camera_distance * math.sin(math.radians(self.camera_rotation['y'])) * math.cos(math.radians(self.camera_rotation['x'])),
            self.camera_distance * math.sin(math.radians(self.camera_rotation['x'])),
            self.camera_distance * math.cos(math.radians(self.camera_rotation['y'])) * math.cos(math.radians(self.camera_rotation['x'])),
            0, 0, 0,
            0, 1, 0
        )
        
        # Araç dönüşü
        glRotatef(self.vehicle_attitude['roll'], 1, 0, 0)
        glRotatef(self.vehicle_attitude['pitch'], 0, 1, 0)
        glRotatef(self.vehicle_attitude['yaw'], 0, 0, 1)
        
        self.draw_vehicle()
        self.draw_coordinate_system()

    def draw_vehicle(self):
        # Ana gövde
        glColor3f(0.7, 0.7, 0.7)
        self.draw_box(1.0, 0.2, 0.2)
        
        # Kollar
        glPushMatrix()
        glColor3f(0.5, 0.5, 0.5)
        for i in range(4):
            glRotatef(90, 0, 1, 0)
            glPushMatrix()
            glTranslatef(0.8, 0, 0)
            self.draw_box(0.6, 0.1, 0.1)
            # Pervaneler
            glColor3f(0.3, 0.3, 0.3)
            glTranslatef(0.3, 0, 0)
            self.draw_propeller()
            glPopMatrix()
        glPopMatrix()

    def draw_box(self, length, width, height):
        glBegin(GL_QUADS)
        # Üst yüz
        glVertex3f(length/2, height/2, width/2)
        glVertex3f(-length/2, height/2, width/2)
        glVertex3f(-length/2, height/2, -width/2)
        glVertex3f(length/2, height/2, -width/2)
        # Alt yüz
        glVertex3f(length/2, -height/2, width/2)
        glVertex3f(-length/2, -height/2, width/2)
        glVertex3f(-length/2, -height/2, -width/2)
        glVertex3f(length/2, -height/2, -width/2)
        # Ön yüz
        glVertex3f(length/2, height/2, width/2)
        glVertex3f(-length/2, height/2, width/2)
        glVertex3f(-length/2, -height/2, width/2)
        glVertex3f(length/2, -height/2, width/2)
        # Arka yüz
        glVertex3f(length/2, height/2, -width/2)
        glVertex3f(-length/2, height/2, -width/2)
        glVertex3f(-length/2, -height/2, -width/2)
        glVertex3f(length/2, -height/2, -width/2)
        # Sağ yüz
        glVertex3f(length/2, height/2, width/2)
        glVertex3f(length/2, height/2, -width/2)
        glVertex3f(length/2, -height/2, -width/2)
        glVertex3f(length/2, -height/2, width/2)
        # Sol yüz
        glVertex3f(-length/2, height/2, width/2)
        glVertex3f(-length/2, height/2, -width/2)
        glVertex3f(-length/2, -height/2, -width/2)
        glVertex3f(-length/2, -height/2, width/2)
        glEnd()

    def draw_propeller(self):
        glBegin(GL_TRIANGLES)
        # Pervane kanadı 1
        glVertex3f(0, 0, 0)
        glVertex3f(0.2, 0.02, 0.4)
        glVertex3f(0.2, 0.02, -0.4)
        # Pervane kanadı 2
        glVertex3f(0, 0, 0)
        glVertex3f(0.2, 0.4, 0.02)
        glVertex3f(0.2, -0.4, 0.02)
        glEnd()

    def draw_coordinate_system(self):
        glBegin(GL_LINES)
        # X ekseni (kırmızı)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(2, 0, 0)
        # Y ekseni (yeşil)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 2, 0)
        # Z ekseni (mavi)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 2)
        glEnd()

    def update_attitude(self, roll, pitch, yaw):
        self.vehicle_attitude['roll'] = roll
        self.vehicle_attitude['pitch'] = pitch
        self.vehicle_attitude['yaw'] = yaw
        self.update()

    def update_animation(self):
        # Pervaneleri döndürme animasyonu eklenebilir
        self.update()

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return
            
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.camera_rotation['y'] += dx * 0.5
            self.camera_rotation['x'] += dy * 0.5
            self.camera_rotation['x'] = max(-90, min(90, self.camera_rotation['x']))
            
        self.last_mouse_pos = event.pos()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.camera_distance = max(2, min(20, self.camera_distance - delta))
        self.update()