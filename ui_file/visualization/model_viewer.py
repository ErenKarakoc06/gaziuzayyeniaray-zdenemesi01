from PyQt6.QtWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class ModelViewer(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.model_rotation = [0, 0, 0]
        self.model_position = [0, 0, 0]
        
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
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
        gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)
        
        # Model dönüşü
        glRotatef(self.model_rotation[0], 1, 0, 0)
        glRotatef(self.model_rotation[1], 0, 1, 0)
        glRotatef(self.model_rotation[2], 0, 0, 1)
        
        # Model çizimi
        self.draw_model()
        
    def draw_model(self):
        # Basit bir drone modeli çizimi
        glBegin(GL_LINES)
        # Ana gövde
        glVertex3f(-1, 0, 0)
        glVertex3f(1, 0, 0)
        glVertex3f(0, -1, 0)
        glVertex3f(0, 1, 0)
        glEnd()