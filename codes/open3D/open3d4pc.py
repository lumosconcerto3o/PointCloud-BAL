import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import open3d as o3d
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dianyun = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Open3D Viewer with PyQt")

        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        layout = QVBoxLayout()
        mainWidget.setLayout(layout)

        self.viewerButton = QPushButton("Open Open3D Viewer")
        self.viewerButton.clicked.connect(self.openViewer)
        layout.addWidget(self.viewerButton)

        self.identifyButton = QPushButton("labeling")
        self.identifyButton.clicked.connect(self.labeling)
        layout.addWidget(self.identifyButton)

    def openViewer(self):
        # Load point cloud file using Open3D
        # Replace the placeholder path with your actual file path
        dianyun_path = "C:\\Users\\lumos\\Desktop\\DDP\\reference_site_facade_laser.ply"
        self.dianyun = o3d.io.read_point_cloud(dianyun_path)

        # Visualize point cloud
        o3d.visualization.draw_geometries([self.dianyun])

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


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
