from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.uic import loadUi
import open3d as o3d
import numpy as np

import warnings


# Disable all warnings
warnings.filterwarnings("ignore")


class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize class member variables
        self.fileName = None  # File name for point cloud
        self.selected_points_coords = []  # Store selected points coordinates

        # Connect UI elements to their corresponding functions
        # Open your own base or paste your file path
        self.dianyun = loadUi(
            r"C:\Users\lumos\Desktop\DDP_Gr4_HU_LI\codes\open3D\dianyun_mainwindow.ui"
        )

        self.dianyun.duquwenjian_2.triggered.connect(self.openProject)
        self.dianyun.jiangzao.triggered.connect(self.denoising)
        self.dianyun.baocunwenjian_2.triggered.connect(self.saving_ply)
        self.dianyun.baocunchuanghu.triggered.connect(self.saving_chuanghu)
        self.dianyun.jieshudianxuan.clicked.connect(self.End_Selection)
        self.dianyun.pushButton.clicked.connect(self.visual_2)
        self.dianyun.labeling_1.clicked.connect(self.labeling)
        self.dianyun.baocundianyunyou.triggered.connect(self.saving_baocundianyunyou)

    # Function to open a point cloud project
    def openProject(self):
        options = QFileDialog.Options()
        options &= ~QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(
            self, "open file", "", "all files (*)", options=options
        )
        if self.fileName:
            ply = o3d.io.read_point_cloud(self.fileName)
            ply_points = np.asarray(ply.points)
            self.dianyun.widget_1.centroid = np.mean(ply_points, axis=0)
            translated_ply_points = ply_points - self.dianyun.widget_1.centroid
            self.dianyun.widget_1.points = translated_ply_points
            # Color
            ply_colors = np.asarray(ply.colors)
            if ply_colors.shape[0] > 0:
                self.dianyun.widget_1.colors = ply_colors
            else:
                ply_colors = np.array([[255, 0, 0]] * ply_points.shape[0])
                self.dianyun.widget_1.colors = ply_colors
            self.dianyun.widget_1.drawing()

    # Function for denoising the point cloud
    def denoising(self):
        self.dianyun.widget_1.clearDrawing()

        ply = o3d.io.read_point_cloud(self.fileName)

        # Set the coordinate range, such as x range [xmin, xmax], y range [ymin, ymax], z range [zmin, zmax]
        xmin, xmax = 16.1, 20.0
        ymin, ymax = -28.3, 15.0
        zmin, zmax = -3.2, 21.5

        # Create a box (AxisAlignedBoundingBox) to represent the coordinate range
        bbox = o3d.geometry.AxisAlignedBoundingBox(
            min_bound=[xmin, ymin, zmin], max_bound=[xmax, ymax, zmax]
        )

        # Empolying crop func. to denoising
        cropped_ply = ply.crop(bbox)

        ply_points = np.asarray(cropped_ply.points)
        ply_colors = np.array([[1.0, 0.0, 0.0]] * ply_points.shape[0])
        self.dianyun.widget_1.points = ply_points - self.dianyun.widget_1.centroid
        self.dianyun.widget_1.colors = ply_colors
        self.dianyun.widget_1.drawing()

    # Function to save point cloud as a PLY file
    def saving_ply(self):
        points = self.dianyun.widget_1.points
        colors = self.dianyun.widget_1.colors
        ply = o3d.geometry.PointCloud()
        ply.points = o3d.utility.Vector3dVector(points)
        ply.colors = o3d.utility.Vector3dVector(colors)
        self.save_file, ftype = QFileDialog.getSaveFileName(
            self, "save file", "./", "PLY Files (*.ply);;All Files (*.*)"
        )

        if not self.save_file:
            return

        o3d.io.write_point_cloud(self.save_file, ply)

    # Function to save selected points as a PLY file as last selection

    def saving_chuanghu(self):
        points = self.dianyun.widget_1.clicked_points_last
        colors = self.dianyun.widget_1.clicked_colors_last
        ply = o3d.geometry.PointCloud()
        ply.points = o3d.utility.Vector3dVector(points)
        ply.colors = o3d.utility.Vector3dVector(colors)
        self.save_chuanghu, ftype = QFileDialog.getSaveFileName(
            self, "save file", "./", "PLY Files (*.ply);;All Files (*.*)"
        )

        if not self.save_chuanghu:
            return
        o3d.io.write_point_cloud(self.save_chuanghu, ply)

    # Function to save all selected points as a PLY file in displayer

    def saving_baocundianyunyou(self):
        points = self.dianyun.widget_1.clicked_points_all
        colors = self.dianyun.widget_1.clicked_colors_all
        ply = o3d.geometry.PointCloud()
        ply.points = o3d.utility.Vector3dVector(points)
        ply.colors = o3d.utility.Vector3dVector(colors)
        self.save_dianyunyou, ftype = QFileDialog.getSaveFileName(
            self, "save file", "./", "PLY Files (*.ply);;All Files (*.*)"
        )

        if not self.save_dianyunyou:
            return
        o3d.io.write_point_cloud(self.save_dianyunyou, ply)

    # Function to visualize selected points in a separate widget

    def visual_2(self):
        self.dianyun.widget_2.points = self.dianyun.widget_1.clicked_points_last
        self.dianyun.widget_2.colors = self.dianyun.widget_1.clicked_colors_last

        self.dianyun.widget_2.drawing_2()

    def End_Selection(self):
        self.dianyun.widget_1.Finish_Selection()

    def labeling(self):
        if self.dianyun:
            # Segment the largest plane, which is considered as the wall
            plane_model, inliers = self.dianyun.segment_plane(
                distance_threshold=0.01, ransac_n=3, num_iterations=1000
            )
            wall = self.dianyun.select_by_index(inliers)
            wall.paint_uniform_color([0.8, 0.8, 0.8])  # Paint the wall gray

            # Extract the rest, potentially containing windows
            non_wall = self.dianyun.select_by_index(inliers, invert=True)
            # non_window = self.dianyun.select_by_index(inliers, invert=True)

            # Cluster the non-wall points and assume the smallest cluster is a window
            labels = np.array(non_wall.cluster_dbscan(eps=0.02, min_points=10))
            label, count = np.unique(labels, return_counts=True)
            if (
                len(label) > 1
            ):  # Ensure there is at least one cluster apart from the background
                window_label = label[
                    np.argmin(count[1:]) + 1
                ]  # Avoid label -1 for noise
                window_points = non_wall.select_by_index(
                    np.where(labels == window_label)[0]
                )
                window_points.paint_uniform_color(
                    [0.1, 0.1, 0.7]
                )  # Paint the window blue
                marked_dianyun = wall + window_points
            else:
                marked_dianyun = wall  # If no clusters found, just display the wall

            # Visualize the point cloud with identified features
            o3d.visualization.draw_geometries([marked_dianyun])
        else:
            print("No point cloud loaded. Please open the viewer first.")


app = QApplication([])
mainwindow = mainwindow()
mainwindow.dianyun.show()
app.exec_()

print("fff")
