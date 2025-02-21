# Example of displaying a point cloud in PyQt5
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt
import numpy as np
import copy
import pyqtgraph.opengl as gl
import open3d as o3d

import pyqtgraph.opengl as gl
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QPainter, QPen
import pyqtgraph as pg
import numpy as np
import copy
import open3d as o3d
from pyqtgraph.opengl import GLViewWidget
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen


class OpenGLWidget(QWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.file_name = ""
        self.points = []
        self.colors = []
        self.clicked_points = []
        self.clicked_colors = []
        self.clicked_points_last = []
        self.clicked_colors_last = []
        self.clicked_points_all = []
        self.clicked_colors_all = []
        self.scatter = None
        self.centroid = []
        self.mouse_positions = []
        self.mouse_positions_crop = []
        self.projected_array_1 = []
        self.flag = False
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.right_click_state = False
        self.crop_state = False
        self.croping = False
        self.picking = False

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

        self.gl_widget.mousePressEvent = self.mousePressEvent_1
        self.gl_widget.mouseReleaseEvent = self.mouseReleaseEvent_1
        self.gl_widget.mouseMoveEvent = self.mouseMoveEvent_1
        self.gl_widget.keyPressEvent = self.keyPressEvent_1

    def mousePressEvent_1(self, event):
        pos = event.pos()
        self.mousePos = pos
        self.flag = True
        self.x0 = pos.x()
        self.y0 = pos.y()
        if event.button() == Qt.RightButton:
            if self.picking == True:
                self.comp(event)
        # self.update()

    def mouseReleaseEvent_1(self, event):
        self.flag = False
        # print(self.x0)
        # print(self.y0)
        # print(self.x1)
        # print(self.y1)
        self.mouse_positions_crop.append([self.x0, self.y0])
        self.mouse_positions_crop.append([self.x1, self.y1])
        if self.croping == True:
            self.crop(event)
            self.Finish_crop()
        self.update()

    def mouseMoveEvent_1(self, event):
        pos = event.pos()
        diff = pos - self.mousePos
        self.mousePos = pos
        if event.buttons() == Qt.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.gl_widget.pan(diff.x(), diff.y(), 0, relative="view")
                self.gl_widget.right_click_state = False
                self.crop_state = False
            else:
                self.gl_widget.orbit(-diff.x(), diff.y())
                self.gl_widget.right_click_state = False
                self.crop_state = False
        elif event.buttons() == Qt.MiddleButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.gl_widget.pan(diff.x(), 0, diff.y(), relative="view-upright")
                self.gl_widget.right_click_state = False
                self.crop_state = False
            else:
                self.gl_widget.pan(diff.x(), diff.y(), 0, relative="view-upright")
                self.gl_widget.right_click_state = False
                self.crop_state = False

        elif event.buttons() == Qt.RightButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if self.flag:
                    self.right_click_state = True
                    self.crop_state = True
                    self.x1 = pos.x()
                    self.y1 = pos.y()
                    # self.update()
                    self.gl_widget.update()

    # 绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.right_click_state == True:
            if self.croping == True:
                # self.gl_widget.update()
                painter = QPainter(self.gl_widget)
                pen_color = QColor(0, 0, 255)
                pen_width = 2
                pen_style = Qt.SolidLine

                pen_color_with_alpha = QColor(pen_color)
                pen_color_with_alpha.setAlpha(100)
                painter.setPen(QPen(pen_color_with_alpha, pen_width, pen_style))

                # painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))

                rect = QRect(
                    self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0)
                )
                # abs(self.x1 - self.x0), abs(self.y1 - self.y0)

                painter.drawRect(rect)
                self.right_click_state = False

    def crop(self, event):
        if self.crop_state == True:
            points = self.points
            m = self.gl_widget.projectionMatrix() * self.gl_widget.viewMatrix()

            m = np.array(m.data(), dtype=np.float32).reshape((4, 4))
            one_mat = np.ones((points.shape[0], 1))
            points = np.concatenate((points, one_mat), axis=1)
            new = np.matmul(points, m)
            new[:, :3] = new[:, :3] / new[:, 3].reshape(-1, 1)
            new = new[:, :3]

            projected_array = np.zeros((new.shape[0], 2))
            projected_array[:, 0] = (new[:, 0] + 1) / 2
            projected_array[:, 1] = (-new[:, 1] + 1) / 2
            self.projected_array = copy.deepcopy(projected_array)

    def Finish_crop(self):
        if self.crop_state == True:
            if self.croping == True:
                x_min = self.x0 / self.width()
                x_max = self.x1 / self.width()
                y_min = self.y0 / self.height()
                y_max = self.y1 / self.height()

                # Use conditional filtering to find the indices of points within a specified range
                indices = np.where(
                    (self.projected_array[:, 0] >= x_min)
                    & (self.projected_array[:, 0] <= x_max)
                    & (self.projected_array[:, 1] >= y_min)
                    & (self.projected_array[:, 1] <= y_max)
                )[0]
                self.clicked_points = self.points[indices]
                self.clicked_colors = np.array(
                    [[0.0, 1.0, 0.0]] * self.clicked_points.shape[0]
                )

                self.mouse_positions_crop = []
                self.clicked_points_last = np.vstack(
                    (self.clicked_points, self.clicked_points)
                )
                self.clicked_colors_last = np.vstack(
                    (self.clicked_colors, self.clicked_colors)
                )

                # add self.clicked_points_last into self.clicked_points_all
                if len(self.clicked_points_all) == 0:
                    self.clicked_points_all = copy.deepcopy(self.clicked_points_last)
                else:
                    self.clicked_points_all = np.vstack(
                        (self.clicked_points_all, self.clicked_points_last)
                    )

                if len(self.clicked_colors_all) == 0:
                    self.clicked_colors_all = copy.deepcopy(self.clicked_colors_last)
                else:
                    self.clicked_colors_all = np.vstack(
                        (self.clicked_colors_all, self.clicked_colors_last)
                    )

    def comp(self, event):
        points = self.points
        pos = event.pos()
        view_w = self.width()
        view_h = self.height()
        mouse_x = pos.x()
        mouse_y = pos.y()
        self.mouse_positions.append([mouse_x, mouse_y])

        m = self.gl_widget.projectionMatrix() * self.gl_widget.viewMatrix()
        m = np.array(m.data(), dtype=np.float32).reshape((4, 4))
        one_mat = np.ones((points.shape[0], 1))
        points = np.concatenate((points, one_mat), axis=1)
        new = np.matmul(points, m)
        new[:, :3] = new[:, :3] / new[:, 3].reshape(-1, 1)
        new = new[:, :3]

        projected_array = np.zeros((new.shape[0], 2))
        projected_array_1 = np.zeros((new.shape[0], 2))
        projected_array[:, 0] = (new[:, 0] + 1) / 2
        projected_array[:, 1] = (-new[:, 1] + 1) / 2
        self.projected_array = copy.deepcopy(projected_array)

        # obtain the distance between each selection
        projected_array_1[:, 0] = projected_array[:, 0] - (mouse_x / view_w)
        projected_array_1[:, 1] = projected_array[:, 1] - (mouse_y / view_h)
        distance_array = np.power(
            np.power(projected_array_1[:, 0], 2) + np.power(projected_array_1[:, 1], 2),
            0.5,
        )
        min_index = np.nanargmin(distance_array)
        print(points[min_index][0:3] + self.centroid)
        self.updatePointColors(min_index)

    def Finish_Selection(self):
        set_mouse_positions = np.vstack(self.mouse_positions)

        min_values = np.min(set_mouse_positions, axis=0)
        max_values = np.max(set_mouse_positions, axis=0)
        x_min = min_values[0] / self.width()
        x_max = max_values[0] / self.width()
        y_min = min_values[1] / self.height()
        y_max = max_values[1] / self.height()

        # Use conditional filtering to find an index of points
        indices = np.where(
            (self.projected_array[:, 0] >= x_min)
            & (self.projected_array[:, 0] <= x_max)
            & (self.projected_array[:, 1] >= y_min)
            & (self.projected_array[:, 1] <= y_max)
        )[0]
        self.clicked_points = self.points[indices]
        self.clicked_colors = np.array([[0.0, 1.0, 0.0]] * self.clicked_points.shape[0])

        self.mouse_positions = []
        self.clicked_points_last = np.vstack((self.clicked_points, self.clicked_points))
        self.clicked_colors_last = np.vstack((self.clicked_colors, self.clicked_colors))

        # add self.clicked_points_last into self.clicked_points_all
        if len(self.clicked_points_all) == 0:
            self.clicked_points_all = copy.deepcopy(self.clicked_points_last)
        else:
            self.clicked_points_all = np.vstack(
                (self.clicked_points_all, self.clicked_points_last)
            )

        if len(self.clicked_colors_all) == 0:
            self.clicked_colors_all = copy.deepcopy(self.clicked_colors_last)
        else:
            self.clicked_colors_all = np.vstack(
                (self.clicked_colors_all, self.clicked_colors_last)
            )

    def updatePointColors(self, min_index):
        if self.scatter is not None:

            colors = self.colors

            colors[min_index] = [0, 1, 0]

            # update GLScatterPlotItem color
            self.scatter.setData(color=colors)
            # update GLScatterPlotItem size
            self.sizes_array[min_index] = 10.0
            self.scatter.setData(size=self.sizes_array)

    def drawing(self):
        sizes = [1.0] * len(self.points)
        self.sizes_array = np.array(sizes)
        scatter = gl.GLScatterPlotItem(
            pos=self.points, color=self.colors, size=self.sizes_array
        )

        scatter.setGLOptions("translucent")
        self.scatter = scatter
        self.gl_widget.addItem(scatter)

    def clearDrawing(self):
        if self.scatter is not None:
            self.gl_widget.removeItem(self.scatter)
            self.scatter = None

    def keyPressEvent_1(self, ev):

        if ev.key() == 81:
            # Q
            self.croping = True
            self.picking = False

            print("croping", self.croping)
            print("picking", self.picking)

        if ev.key() == 83:
            # S
            self.picking = True
            self.croping = False
            print("croping", self.croping)
            print("picking", self.picking)
