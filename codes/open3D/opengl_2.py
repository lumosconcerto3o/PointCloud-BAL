import pyqtgraph.opengl as gl
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QWidget
import open3d as o3d
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtGui import QMouseEvent



class OpenGLWidget_2(QWidget):  
    def __init__(self, parent = None):       
        super(OpenGLWidget_2, self).__init__(parent)    
        self.selected_points = []
        self.points = []
        self.colors = []


        self.gl_widget = gl.GLViewWidget()  
        self.gl_widget.setCameraPosition(distance=10, elevation=30, azimuth=30)
        self.gl_widget.setBackgroundColor((255, 255, 255, 0))

        self.gl_widget.setContentsMargins(0, 0, 0, 0)

        axis = gl.GLAxisItem()
        self.gl_widget.addItem(axis)
        axis.setSize(30, 30, 30)  

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  
        layout.addWidget(self.gl_widget)



    def drawing_2(self):

        scatter = gl.GLScatterPlotItem(pos=self.points, color=self.colors, size=5.0)
        scatter.setGLOptions('translucent')
        self.scatter = scatter  
        self.gl_widget.addItem(scatter)





