import logging
from abc import ABC
from typing import TypeVar, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import animation
from pandas.plotting import parallel_coordinates

LOGGER = logging.getLogger('jmetal')

S = TypeVar('S')


class Plot(ABC):

    def __init__(self,
                 plot_title: str = 'jMetalPy',
                 reference_front: List[S] = None,
                 reference_point: list = None,
                 axis_labels: list = None):
        """
        :param plot_title: Title of the graph.
        :param axis_labels: List of axis labels.
        :param reference_point:
        :param reference_front:
        """
        self.plot_title = plot_title
        self.axis_labels = axis_labels
        self.reference_point = reference_point
        self.reference_front = reference_front
        self.dimension = None

    @staticmethod
    def get_points(solutions: List[S]) -> Tuple[pd.DataFrame, int]:
        """ Get points for each solution of the front.

        :param solutions: List of solutions.
        :return: Pandas df with one column for each objective and one row for each solution.
        """
        if solutions is None:
            raise Exception('Front is none!')

        points = pd.DataFrame(list(solution.objectives for solution in solutions))
        return points, points.shape[1]

    def plot(self, front: List[S], label: List[str] = None, normalize: bool = False, filename: str = None, format: str = 'eps'):
        """ Plot any arbitrary number of fronts in 2D, 3D or p-coords.

        :param front: List of fronts.
        :param label: List of fronts titles (if any).
        :param normalize: If True, normalize data (for p-coords).
        :param filename: Output filename.
        :param format: Output file format.
        """
        if not isinstance(front[0], list):
            front = [front]

        dimension = front[0][0].number_of_objectives

        if dimension == 2:
            self.two_dim(front, label, filename, format)
        elif dimension == 3:
            self.three_dim(front, label, filename, format)
        else:
            self.pcoords(front, normalize, filename, format)

    def two_dim(self, fronts: List[list], labels: List[str] = None, filename: str = None, format: str = 'eps'):
        """ Plot any arbitrary number of fronts in 2D.

        :param fronts: List of fronts (containing solutions).
        :param labels: List of fronts title (if any).
        :param filename: Output filename.
        """
        n = int(np.ceil(np.sqrt(len(fronts))))
        fig = plt.figure()
        fig.suptitle(self.plot_title, fontsize=16)

        reference = None
        if self.reference_front:
            reference, _ = self.get_points(self.reference_front)

        for i, _ in enumerate(fronts):
            points, _ = self.get_points(fronts[i])

            ax = fig.add_subplot(n, n, i + 1)
            points.plot(kind='scatter', x=0, y=1, ax=ax, color='b', alpha=0.2)

            if labels:
                ax.set_title(labels[i])

            if self.reference_front:
                reference.plot(x=0, y=1, ax=ax, color='k', legend=False)

            if self.reference_point:
                plt.plot([self.reference_point[0]], [self.reference_point[1]], marker='o', markersize=3, color='r')

            if self.axis_labels:
                plt.xlabel(self.axis_labels[0])
                plt.ylabel(self.axis_labels[1])

        if filename:
            plt.savefig(filename, format=format, dpi=200)
        else:
            plt.show()

        plt.close(fig)

    def three_dim(self, fronts: List[list], labels: List[str] = None, filename: str = None, format: str = 'eps'):
        """ Plot any arbitrary number of fronts in 3D.

        :param fronts: List of fronts (containing solutions).
        :param labels: List of fronts title (if any).
        :param filename: Output filename.
        """
        n = int(np.ceil(np.sqrt(len(fronts))))
        fig = plt.figure()
        fig.suptitle(self.plot_title, fontsize=16)

        for i, _ in enumerate(fronts):
            ax = fig.add_subplot(n, n, i + 1, projection='3d')
            ax.scatter([s.objectives[0] for s in fronts[i]],
                       [s.objectives[1] for s in fronts[i]],
                       [s.objectives[2] for s in fronts[i]])

            if labels:
                ax.set_title(labels[i])

            if self.reference_front:
                ax.scatter([s.objectives[0] for s in self.reference_front],
                           [s.objectives[1] for s in self.reference_front],
                           [s.objectives[2] for s in self.reference_front])

            if self.reference_point:
                # todo
                pass

            ax.relim()
            ax.autoscale_view(True, True, True)
            ax.view_init(elev=30.0, azim=15.0)
            ax.locator_params(nbins=4)

        if filename:
            if format == 'gif':
                def animate(i):
                    ax.view_init(elev=10., azim=i)
                    return fig,

                anim = animation.FuncAnimation(fig, animate, frames=20, interval=1, blit=True, repeat=False)

                LOGGER.info('Generating GIF (this may take some time...)')
                anim.save(filename + '.gif', writer=animation.PillowWriter(fps=24))
                LOGGER.info('Done')
            else:
                plt.savefig(filename, format=format, dpi=1000)
        else:
            plt.show()

        plt.close(fig)

    def pcoords(self, fronts: list, normalize: bool = False, filename: str = None, format: str = 'eps'):
        """ Plot any arbitrary number of fronts in parallel coordinates.

        :param fronts: List of fronts (containing solutions).
        :param filename: Output filename.
        """
        n = int(np.ceil(np.sqrt(len(fronts))))
        fig = plt.figure()
        fig.suptitle(self.plot_title, fontsize=16)

        for i, _ in enumerate(fronts):
            points, _ = self.get_points(fronts[i])

            if normalize:
                points = (points - points.min()) / (points.max() - points.min())

            ax = fig.add_subplot(n, n, i + 1)
            parallel_coordinates(points, 0, ax=ax)

            ax.get_legend().remove()

            if self.axis_labels:
                ax.set_xticklabels(self.axis_labels)

        if filename:
            plt.savefig(filename, format=format, dpi=1000)
        else:
            plt.show()

        plt.close(fig)