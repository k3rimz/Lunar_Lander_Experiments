import random
import pygame
import math

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class LandscapeLine:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.landable = (p1.y == p2.y)
        self.multiplier = 1

class LandingZone:
    def __init__(self, linenum, multi):
        self.lineNum = linenum
        self.multiplier = multi

class Landscape:
    def __init__(self):
        self.points = []
        self.lines = []
        self.stars = []
        self.availableZones = []
        self.zoneCombis = []
        self.currentCombi = 0
        self.zoneInfos = []
        self.landscale = 1.5
        self.flickerProgress = 0

        self.setupData()

        self.tileWidth = self.points[-1].x * self.landscale

        for p in self.points:
            p.x *= self.landscale
            p.y *= self.landscale
            p.y -= 50 * self.landscale

        for i in range(1, len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]
            self.lines.append(LandscapeLine(p1, p2))

        for i in range(len(self.stars)):
            self.stars[i]['x'] *= self.landscale
            self.stars[i]['y'] *= self.landscale

        for line in self.lines:
            if random.random() < 0.1:
                star = {'x': line.p1.x, 'y': random.random() * 600}
                if star['y'] < line.p1.y and star['y'] < line.p2.y:
                    self.stars.append(star)

        # Calculate the total height of the landscape
        self.height = max(p.y for p in self.points)
        self.width = self.tileWidth  # Set width to tileWidth for a single tile

    def setupData(self):
        self.points.append(Vector2(0.5, 355.55))
        self.points.append(Vector2(5.45, 355.55))
        self.points.append(Vector2(6.45, 359.4))
        self.points.append(Vector2(11.15, 359.4))
        self.points.append(Vector2(12.1, 363.65))
        self.points.append(Vector2(14.6, 363.65))
        self.points.append(Vector2(15.95, 375.75))
        self.points.append(Vector2(19.25, 388))
        self.points.append(Vector2(19.25, 391.9))
        self.points.append(Vector2(21.65, 400))
        self.points.append(Vector2(28.85, 404.25))
        self.points.append(Vector2(30.7, 412.4))
        self.points.append(Vector2(33.05, 416.7))
        self.points.append(Vector2(37.9, 420.5))
        self.points.append(Vector2(42.7, 420.5))
        self.points.append(Vector2(47.4, 416.65))
        self.points.append(Vector2(51.75, 409.5))
        self.points.append(Vector2(56.55, 404.25))
        self.points.append(Vector2(61.3, 400))
        self.points.append(Vector2(63.65, 396.15))
        self.points.append(Vector2(68, 391.9))
        self.points.append(Vector2(70.3, 388))
        self.points.append(Vector2(75.1, 386.1))
        self.points.append(Vector2(79.85, 379.95))
        self.points.append(Vector2(84.7, 378.95))
        self.points.append(Vector2(89.05, 375.65))
        self.points.append(Vector2(93.75, 375.65))
        self.points.append(Vector2(98.5, 376.55))
        self.points.append(Vector2(103.2, 379.95))
        self.points.append(Vector2(104.3, 383.8))
        self.points.append(Vector2(107.55, 388))
        self.points.append(Vector2(108.95, 391.9))
        self.points.append(Vector2(112.4, 396.15))
        self.points.append(Vector2(113.3, 400))
        self.points.append(Vector2(117.1, 404.25))
        self.points.append(Vector2(121.95, 404.25))
        self.points.append(Vector2(125.3, 396.3))
        self.points.append(Vector2(128.6, 394.2))
        self.points.append(Vector2(132.45, 396.15))
        self.points.append(Vector2(135.75, 399.9))
        self.points.append(Vector2(138.15, 408.15))
        self.points.append(Vector2(144.7, 412.4))
        self.points.append(Vector2(146.3, 424.8))
        self.points.append(Vector2(149.55, 436.65))
        self.points.append(Vector2(149.55, 441.05))
        self.points.append(Vector2(154.35, 444.85))
        self.points.append(Vector2(163.45, 444.85))
        self.points.append(Vector2(168.15, 441.05))
        self.points.append(Vector2(172.95, 436.75))
        self.points.append(Vector2(175.45, 432.9))
        self.points.append(Vector2(179.7, 428.6))
        self.points.append(Vector2(181.95, 424.8))
        self.points.append(Vector2(186.7, 422.5))
        self.points.append(Vector2(189.15, 412.4))
        self.points.append(Vector2(191.55, 404.35))
        self.points.append(Vector2(196.35, 402.4))
        self.points.append(Vector2(200.7, 398.1))
        self.points.append(Vector2(205.45, 391.9))
        self.points.append(Vector2(210.15, 383.8))
        self.points.append(Vector2(212.55, 375.75))
        self.points.append(Vector2(216.85, 371.8))
        self.points.append(Vector2(219.3, 367.55))
        self.points.append(Vector2(220.65, 363.65))
        self.points.append(Vector2(224, 359.4))
        self.points.append(Vector2(228.8, 359.4))
        self.points.append(Vector2(233.55, 355.55))
        self.points.append(Vector2(237.85, 348.45))
        self.points.append(Vector2(242.65, 343.2))
        self.points.append(Vector2(245, 335.15))
        self.points.append(Vector2(247.35, 322.8))
        self.points.append(Vector2(247.3, 314.5))
        self.points.append(Vector2(248.35, 306.55))
        self.points.append(Vector2(252.2, 296.5))
        self.points.append(Vector2(256.55, 294.55))
        self.points.append(Vector2(257.95, 290.4))
        self.points.append(Vector2(261.25, 285.95))
        self.points.append(Vector2(265.95, 285.95))
        self.points.append(Vector2(267, 290.25))
        self.points.append(Vector2(271.75, 290.25))
        self.points.append(Vector2(273.25, 294.55))
        self.points.append(Vector2(275.2, 294.55))
        self.points.append(Vector2(278.95, 296.5))
        self.points.append(Vector2(282.25, 300.3))
        self.points.append(Vector2(284.7, 308.45))
        self.points.append(Vector2(291.85, 312.65))
        self.points.append(Vector2(298.55, 330.8))
        self.points.append(Vector2(303.25, 331.8))
        self.points.append(Vector2(308, 335.05))
        self.points.append(Vector2(309, 338.9))
        self.points.append(Vector2(312.35, 343.2))
        self.points.append(Vector2(313.8, 347.05))
        self.points.append(Vector2(317.05, 351.4))
        self.points.append(Vector2(321.9, 351.4))
        self.points.append(Vector2(322.85, 363.8))
        self.points.append(Vector2(326.6, 375.75))
        self.points.append(Vector2(326.6, 379.95))
        self.points.append(Vector2(330.9, 379.95))
        self.points.append(Vector2(332.4, 383.8))
        self.points.append(Vector2(335.8, 388))
        self.points.append(Vector2(338.1, 396.15))
        self.points.append(Vector2(340.45, 400.1))
        self.points.append(Vector2(345.3, 404.25))
        self.points.append(Vector2(346.25, 416.65))
        self.points.append(Vector2(349.6, 428.7))
        self.points.append(Vector2(349.6, 432.85))
        self.points.append(Vector2(350.95, 436.75))
        self.points.append(Vector2(354.3, 441.05))
        self.points.append(Vector2(359, 441.05))
        self.points.append(Vector2(361.4, 449.1))
        self.points.append(Vector2(363.95, 453))
        self.points.append(Vector2(368.2, 457.2))
        self.points.append(Vector2(372.9, 461))
        self.points.append(Vector2(410.2, 461))
        self.points.append(Vector2(412.55, 449.1))
        self.points.append(Vector2(417.4, 441.05))
        self.points.append(Vector2(419.7, 432.9))
        self.points.append(Vector2(422.05, 432.9))
        self.points.append(Vector2(425.45, 424.8))
        self.points.append(Vector2(428.8, 422.35))
        self.points.append(Vector2(433.45, 416.65))
        self.points.append(Vector2(438.25, 415.15))
        self.points.append(Vector2(442.6, 412.4))
        self.points.append(Vector2(447.4, 412.4))
        self.points.append(Vector2(448.8, 416.65))
        self.points.append(Vector2(454.55, 430.55))
        self.points.append(Vector2(455.5, 434.8))
        self.points.append(Vector2(459.25, 438.6))
        self.points.append(Vector2(462.6, 440.9))
        self.points.append(Vector2(466, 444.85))
        self.points.append(Vector2(468.35, 452.9))
        self.points.append(Vector2(475.55, 457.3))
        self.points.append(Vector2(484.7, 457.3))
        self.points.append(Vector2(494.7, 458.2))
        self.points.append(Vector2(503.75, 461.1))
        self.points.append(Vector2(522.2, 461.1))
        self.points.append(Vector2(524.75, 453))
        self.points.append(Vector2(527.1, 441.05))
        self.points.append(Vector2(527.1, 432.9))
        self.points.append(Vector2(531.9, 432.9))
        self.points.append(Vector2(534.15, 424.8))
        self.points.append(Vector2(538.6, 420.5))
        self.points.append(Vector2(540.9, 416.65))
        self.points.append(Vector2(542.35, 412.5))
        self.points.append(Vector2(545.7, 408))
        self.points.append(Vector2(550.45, 408))
        self.points.append(Vector2(552.85, 398.1))
        self.points.append(Vector2(554.75, 389.95))
        self.points.append(Vector2(559.55, 388))
        self.points.append(Vector2(564.35, 391.9))
        self.points.append(Vector2(573.35, 391.9))
        self.points.append(Vector2(578.1, 388))
        self.points.append(Vector2(579.55, 379.95))
        self.points.append(Vector2(582.9, 369.4))
        self.points.append(Vector2(587.75, 367.55))
        self.points.append(Vector2(588.65, 363.8))
        self.points.append(Vector2(592.05, 359.5))
        self.points.append(Vector2(596.85, 355.55))

        self.availableZones.append(LandingZone(0, 4))
        self.availableZones.append(LandingZone(13, 3))
        self.availableZones.append(LandingZone(25, 4))
        self.availableZones.append(LandingZone(34, 4))
        self.availableZones.append(LandingZone(63, 5))
        self.availableZones.append(LandingZone(75, 4))
        self.availableZones.append(LandingZone(106, 5))
        self.availableZones.append(LandingZone(111, 2))
        self.availableZones.append(LandingZone(121, 5))
        self.availableZones.append(LandingZone(133, 2))
        self.availableZones.append(LandingZone(148, 3))

        self.zoneCombis.append([2, 3, 7, 9])
        self.zoneCombis.append([7, 8, 9, 10])
        self.zoneCombis.append([2, 3, 7, 9])
        self.zoneCombis.append([1, 4, 7, 9])
        self.zoneCombis.append([0, 5, 7, 9])
        self.zoneCombis.append([6, 7, 8, 9])
        self.zoneCombis.append([1, 4, 7, 9])

    def render(self, surface, camera_rect):
        # Calculate how many tiles are needed to cover the screen
        tiles_needed = math.ceil(camera_rect.width / self.tileWidth) + 2

        # Calculate the starting tile index based on camera's left position
        start_tile = int(camera_rect.left // self.tileWidth) - 1

        for tile in range(start_tile, start_tile + tiles_needed):
            offset = tile * self.tileWidth

            # Render landscape lines
            for line in self.lines:
                start_pos = (line.p1.x + offset - camera_rect.left, line.p1.y - camera_rect.top)
                end_pos = (line.p2.x + offset - camera_rect.left, line.p2.y - camera_rect.top)
                color = (0, 255, 0) if line.landable else (255, 255, 255)
                pygame.draw.line(surface, color, start_pos, end_pos, 2)

            # Render stars
            for star in self.stars:
                star_pos = (star['x'] + offset - camera_rect.left, star['y'] - camera_rect.top)
                # Wrap stars horizontally
                star_pos = (star_pos[0] % camera_rect.width, star_pos[1])
                if 0 <= star_pos[0] < camera_rect.width and 0 <= star_pos[1] < camera_rect.height:
                    pygame.draw.circle(surface, (255, 255, 255), (int(star_pos[0]), int(star_pos[1])), 1)
