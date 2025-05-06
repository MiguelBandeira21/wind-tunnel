"""Helper class to visualize the wind tunnel."""
import matplotlib.pyplot as plt
import pyvista as pv
import vtk

vtk.vtkLogger.SetStderrVerbosity(vtk.vtkLogger.VERBOSITY_OFF)


def _get_x_aligned_rectangle(x, y_min, y_max, z_min, z_max):
    y_mean = (y_min + y_max) / 2
    z_mean = (z_min + z_max) / 2
    y_length = y_max - y_min
    z_length = z_max - z_min
    plane = pv.Plane(center=(x, y_mean, z_mean),
                     direction=(1, 0, 0),
                     i_size=z_length,
                     j_size=y_length)
    return plane


def _get_y_aligned_rectangle(y, x_min, x_max, z_min, z_max):
    x_mean = (x_min + x_max) / 2
    z_mean = (z_min + z_max) / 2
    x_length = x_max - x_min
    z_length = z_max - z_min
    plane = pv.Plane(center=(x_mean, y, z_mean),
                     direction=(0, 1, 0),
                     i_size=z_length,
                     j_size=x_length)
    return plane


def _get_z_aligned_rectangle(z, x_min, x_max, y_min, y_max):
    x_mean = (x_min + x_max) / 2
    y_mean = (y_min + y_max) / 2
    x_length = x_max - x_min
    y_length = y_max - y_min
    plane = pv.Plane(center=(x_mean, y_mean, z),
                     direction=(0, 0, 1),
                     i_size=x_length,
                     j_size=y_length)
    return plane


def plot_force_coefficients(force_coefficients_file_path: str,
                            coefficient: str):
    """Visualize a graph of the evolution of a force coefficient.

    Can be used to visualize the evolution of the Moment, Drag, Lift,
    Front Lift, and Rear Lift coefficients.

    Parameters:
    - file_path (str): The path to the force coefficients file.
    - coefficient (str): The force coefficient to visualize.
    """

    coefficient = coefficient.lower()
    coeffs_map = {
        "moment": 1,
        "drag": 2,
        "lift": 3,
        "front lift": 4,
        "rear lift": 5
    }
    if coefficient not in coeffs_map:
        raise ValueError(f"Invalid coefficient: {coefficient} must be one of \
                (Moment, Drag, Lift, Front Lift, Rear Lift)")

    time = []
    coeff = []

    with open(force_coefficients_file_path, "r", encoding="utf-8") as file:
        for _ in range(9):
            next(file)

        for line in file:
            columns = line.split()
            time.append(float(columns[0]))
            coeff.append(float(columns[coeffs_map[coefficient]]))

    plt.figure(figsize=(10, 6))
    plt.plot(time, coeff, color="b")
    plt.xlabel("Time")
    plt.ylabel(f"{coefficient}")
    plt.title(f"{coefficient} vs Time")
    plt.grid(True)
    plt.show()


class WindTunnelVisualizer:
    """
    A class for visualizing wind tunnel data.

    Parameters:
    - x_min (float): The minimum x-coordinate of the visualization space.
    - x_max (float): The maximum x-coordinate of the visualization space.
    - y_min (float): The minimum y-coordinate of the visualization space.
    - y_max (float): The maximum y-coordinate of the visualization space.
    - z_min (float): The minimum z-coordinate of the visualization space.
    - z_max (float): The maximum z-coordinate of the visualization space.
    """

    # pylint: disable=too-many-positional-arguments
    def __init__(self, x_min: float, x_max: float, y_min: float, y_max: float,
                 z_min: float, z_max: float):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max

        self.plt = pv.Plotter()
        self.plt.add_axes()
        self.plt.show_bounds()
        self._add_walls()
        self._add_origin_sphere()

    def _add_origin_sphere(self, radius: float = 0.1, color: str = "black"):
        """
        Add a sphere at the origin of the visualization space.

        Parameters:
        - radius (float): The radius of the sphere.
        - color (str): The color of the sphere.
        """
        sphere = pv.Sphere(radius=radius, center=(0, 0, 0))
        self.plt.add_mesh(sphere, color=color)

    def add_mesh(self,
                 mesh: pv.PolyData,
                 *,
                 color: str = "blue",
                 opacity: float = 1.0,
                 show_edges: bool = False,
                 scalars: str = None,
                 clim: list = None):
        """
        Add a mesh to the visualization.

        Parameters:
        - mesh (pv.PolyData): The mesh to be added.
        - color (str): The color of the mesh.
        - opacity (float): The opacity of the mesh.
        - show_edges (bool): Whether to show the edges of the mesh.
        - scalars (str): The scalar data to be used for coloring the mesh.
        - clim (list): The scale limits for the scalar data.
        """
        self.plt.add_mesh(mesh,
                          color=color,
                          opacity=opacity,
                          show_edges=show_edges,
                          scalars=scalars,
                          clim=clim)

    def add_force_coefficients(self,
                               coefficients: dict,
                               font_size: int = 12,
                               color: str = "black",
                               position: str = "upper_right"):
        """ Add the force coefficients to the visualization.

        Parameters:
        - coefficients (dict): A dictionary containing the force coefficients.
        - font_size (int): The font size of the text.
        - color (str): The color of the text.
        - position (str): The position of the text.
        """

        moment = coefficients.get("Moment", 0)
        drag = coefficients.get("Drag", 0)
        lift = coefficients.get("Lift", 0)
        front_lift = coefficients.get("Front Lift", 0)
        rear_lift = coefficients.get("Rear Lift", 0)

        force_coeffs_text = (f"Moment: {moment:.3f}\n"
                             f"Drag: {drag:.3f}\n"
                             f"Lift: {lift:.3f}\n"
                             f"Front Lift: {front_lift:.3f}\n"
                             f"Rear Lift: {rear_lift:.3f}")

        self.plt.add_text(force_coeffs_text,
                          position=position,
                          font_size=font_size,
                          color=color)

    def _add_walls(self, opacity: float = 0.5):
        """
        Add walls to the visualization.

        Parameters:
        - opacity (float): The opacity of the walls.
        """
        plane = _get_x_aligned_rectangle(self.x_min, self.y_min, self.y_max,
                                         self.z_min, self.z_max)
        self.plt.add_mesh(plane, color="red", opacity=opacity)
        plane = _get_x_aligned_rectangle(self.x_max, self.y_min, self.y_max,
                                         self.z_min, self.z_max)
        self.plt.add_mesh(plane, color="red", opacity=opacity, show_edges=True)

        plane = _get_y_aligned_rectangle(self.y_min, self.x_min, self.x_max,
                                         self.z_min, self.z_max)
        self.plt.add_mesh(plane,
                          color="green",
                          opacity=opacity,
                          show_edges=True)

        plane = _get_z_aligned_rectangle(self.z_min, self.x_min, self.x_max,
                                         self.y_min, self.y_max)
        self.plt.add_mesh(plane, color="blue", opacity=opacity, show_edges=True)

    def set_camera_position(self, camera_position):
        """
        Set the camera position of the visualization.

        Parameters:
        - camera_position: The new camera position.
        """
        self.plt.camera_position = camera_position

    def show(self):
        """
        Show the visualization.
        """
        self.plt.show()
