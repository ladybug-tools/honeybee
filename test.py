from collections import namedtuple

color = namedtuple('Color', 'r g b')
c = color(100, 200, 255)
print c[0]
