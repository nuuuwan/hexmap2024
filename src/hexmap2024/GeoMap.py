import os
import random
from functools import cached_property

import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import numpy as np
from gig import Ent, EntType
from utils import Hash, JSONFile, Log

log = Log('GeoMap')


class GeoMap:
    BACKGROUND_COLOR = '#004'

    def __init__(self, info_list):
        self.info_list = sorted(info_list, key=lambda info: info['id'])

    @cached_property
    def ids(self):
        return [info['id'] for info in self.info_list]

    @staticmethod
    def get_geo(id):
        ent = Ent.from_id(id)
        return ent.geo()

    @staticmethod
    def get_multi_polygon(id):
        geo = GeoMap.get_geo(id)
        return geo.loc[0, 'geometry']

    @staticmethod
    def get_largest_polygon(id):
        multi_polygon = GeoMap.get_multi_polygon(id)
        largest_area = 0
        largest_polygon = None
        for polygon in list(multi_polygon.geoms):
            if polygon.area > largest_area:
                largest_area = polygon.area
                largest_polygon = polygon
        return largest_polygon

    @staticmethod
    def get_random_points_nocache(id, n):
        multi_polygon = GeoMap.get_multi_polygon(id)
        polygons = list(multi_polygon.geoms)
        total_area = sum([polygon.area for polygon in polygons])
        points = []
        for polygon in polygons:
            n_polygon = int(round(n * polygon.area / total_area, 0))
            points_for_polygon = GeoMap.get_random_points_from_polygon(
                polygon, n_polygon
            )
            points.extend(points_for_polygon)
        return points

    @staticmethod
    def get_random_points(id, n):
        json_file = JSONFile(os.path.join('temp-data', f'random_points.{id}.json'))
        if json_file.exists:
            return json_file.read()
        random_points = GeoMap.get_random_points_nocache(id, n)
        json_file.write(random_points)
        return random_points

    @staticmethod
    def get_random_points_from_polygon(polygon, n):
        xs, yx = polygon.exterior.coords.xy

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(yx)
        max_y = max(yx)

        xys = [(x, y) for x, y in zip(xs, yx)]
        path = mplPath.Path(np.array(xys))

        points = []
        while len(points) < n:
            random_point = (
                random.uniform(min_x, max_x),
                random.uniform(min_y, max_y),
            )
            if path.contains_point(random_point):
                points.append(random_point)
        return points

    @cached_property
    def file_label(self):
        return Hash.md5(str(self.info_list))[:8]

    def draw(self):
        fig, ax = plt.subplots()
        fig.set_size_inches(12, 12)
        ax.set_facecolor(self.BACKGROUND_COLOR)

        for info in self.info_list:
            id = info['id']
            n = info['n']
            log.debug(f'{id}: {n}')
            try:
                geo = GeoMap.get_geo(id)
                geo.plot(ax=ax, color=self.BACKGROUND_COLOR)

                for point in GeoMap.get_random_points(id, n):
                    circle = plt.Circle(point, 0.005, facecolor=info['color'])
                    ax.add_patch(circle)
            except Exception as e:
                log.error(f'Error drawing {id}: {e}')

        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        image_path = os.path.join(
            'temp-images', f'geomap.{self.file_label}.png'
        )
        plt.savefig(image_path, dpi=300)
        log.info(f'Wrote {image_path}')
        os.startfile(image_path)


def main():
    regions = Ent.list_from_type(EntType.DSD)
    info_list = [
        dict(
            id=region.id,
            n=int(round(region.population / 1_000, 0)),
            color='#fff',
        )
        for region in regions
    ]
    gm = GeoMap(info_list)
    gm.draw()


if __name__ == "__main__":
    main()
