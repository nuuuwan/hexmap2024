from gig import Ent
import matplotlib.pyplot as plt
from utils import Log
import os

log = Log('GeoMap')


class GeoMap:
    def __init__(self, id):
        self.ent = Ent.from_id(id)

    def draw(self, image_path):
        geo = self.ent.geo()
        geo.plot()
        plt.savefig(image_path)
        log.info(f'Wrote {image_path}')


def main():
    gm = GeoMap('LK-11')
    gm.draw(os.path.join('images', 'geomap.LK-11.png'))


if __name__ == "__main__":
    main()
