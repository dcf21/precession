#!/usr/bin/python3
# starwheel.py
# -*- coding: utf-8 -*-
#
# The python script in this file makes the various parts of a precession
# planisphere.
#
# Copyright (C) 2014-2024 Dominic Ford <https://dcford.org.uk/>
#
# This code is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# You should have received a copy of the GNU General Public License along with
# this file; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA  02110-1301, USA

# ----------------------------------------------------------------------------

"""
Render the star wheel for the precession planisphere.
"""

import re
from math import pi, sin, cos, atan2, asin, hypot

from bright_stars_process import fetch_bright_star_list
from constants import unit_deg, unit_rev, unit_mm, unit_cm, inclination_ecliptic, r_1, r_gap, central_hole_size, radius
from graphics_context import BaseComponent, GraphicsContext
from settings import fetch_command_line_arguments
from text import text
from themes import themes


class StarWheel(BaseComponent):
    """
    Render the star wheel for the precession planisphere.
    """

    def default_filename(self) -> str:
        """
        Return the default filename to use when saving this component.
        """
        return "star_wheel"

    def bounding_box(self, settings: dict) -> dict[str, float]:
        """
        Return the bounding box of the canvas area used by this component.

        :param settings:
            A dictionary of settings required by the renderer.
        :return:
         Dictionary with the elements 'x_min', 'x_max', 'y_min' and 'y_max' set
        """
        return {
            'x_min': -r_1 - 4 * unit_mm,
            'x_max': r_1 + 4 * unit_mm,
            'y_min': -r_1 - 4 * unit_mm,
            'y_max': r_1 + 4 * unit_mm
        }

    @staticmethod
    def ra_dec_to_ecliptic_coordinates(ra: float, dec: float) -> tuple[float, float]:
        ra = float(ra)
        dec = float(dec)

        hr: float = pi / 12
        deg: float = pi / 180

        x: float = cos(ra * hr) * cos(dec * deg)
        y: float = sin(ra * hr) * cos(dec * deg)
        z: float = sin(dec * deg)

        x2: float = x
        y2: float = y * cos(inclination_ecliptic * deg) + z * sin(inclination_ecliptic * deg)
        z2: float = -y * sin(inclination_ecliptic * deg) + z * cos(inclination_ecliptic * deg)

        lat: float = asin(z2) / deg
        lng: float = atan2(y2, x2) / deg

        return lng, lat

    def do_rendering(self, settings: dict, context: GraphicsContext) -> None:
        """
        This method is required to actually render this item.

        :param settings:
            A dictionary of settings required by the renderer.
        :param context:
            A GraphicsContext object to use for drawing
        :return:
            None
        """

        is_southern: bool = settings['southern']
        language: str = settings['language']
        latitude: float = 90 - inclination_ecliptic
        theme: dict[str, tuple[float, float, float, float]] = themes[settings['theme']]

        context.set_font_size(1.2)

        # Radius of outer edge of star chart
        r_2: float = r_1 - r_gap

        # Radius of tip / base of arrow for lining up with year scale
        r_4: float = r_2 * 0.8 + r_1 * 0.2
        r_5: float = r_2 * 0.5 + r_1 * 0.5
        r_6: float = r_2 * 0.3 + r_1 * 0.7

        # Draw the outer edge of planisphere
        context.begin_path()
        context.circle(centre_x=0, centre_y=0, radius=r_1)
        context.fill(color=theme['background'])

        # Draw the central hole in the middle of the planisphere
        context.begin_sub_path()
        context.circle(centre_x=0, centre_y=0, radius=central_hole_size)
        context.stroke(color=theme['edge'])

        # Combine these two paths to make a clipping path for drawing the star wheel
        context.clip()

        # Draw lines of constant ecliptic latitude for path of north pole
        lat: float
        for lat in (90 - inclination_ecliptic,
                    0,
                    -90 + inclination_ecliptic):
            # Convert latitude into radius from the centre of the planisphere
            r: float = radius(dec=lat, latitude=latitude)
            if r > r_2:
                continue
            context.begin_path()
            context.circle(centre_x=0, centre_y=0, radius=r)
            context.stroke(color=theme['grid'])

        # Draw constellation stick figures
        with open("raw_data/constellation_stick_figures.dat", "rt") as f_in:
            for line in f_in:
                line: str = line.strip()

                # Ignore blank lines and comment lines
                if (len(line) == 0) or (line[0] == '#'):
                    continue

                # Split line into words.
                # These are the names of the constellations, and the start and end points for each stroke.
                name: str
                ra1_str: str
                dec1_str: str
                ra2_str: str
                dec2_str: str
                name, ra1_str, dec1_str, ra2_str, dec2_str = line.split()

                lng1: float
                lat1: float
                lng2: float
                lat2: float
                lng1, lat1 = self.ra_dec_to_ecliptic_coordinates(ra=float(ra1_str) * 12 / 180, dec=float(dec1_str))
                lng2, lat2 = self.ra_dec_to_ecliptic_coordinates(ra=float(ra2_str) * 12 / 180, dec=float(dec2_str))

                # If we're making a southern hemisphere planisphere, we flip the sky upside down
                if is_southern:
                    lng1 *= -1
                    lng2 *= -1
                    lat1 *= -1
                    lat2 *= -1

                # Project RA and Dec into radius and azimuth in the planispheric projection
                r_point_1: float = radius(dec=lat1, latitude=latitude)
                if r_point_1 > r_2:
                    continue

                r_point_2: float = radius(dec=lat2, latitude=latitude)
                if r_point_2 > r_2:
                    continue

                p1: tuple[float, float] = (-r_point_1 * cos(lng1 * unit_deg), -r_point_1 * sin(lng1 * unit_deg))
                p2: tuple[float, float] = (-r_point_2 * cos(lng2 * unit_deg), -r_point_2 * sin(lng2 * unit_deg))

                # Impose a maximum length of 4 cm on constellation stick figures; they get quite distorted at the edge
                if hypot(p2[0] - p1[0], p2[1] - p1[1]) > 4 * unit_cm:
                    continue

                # Stroke a line
                context.begin_path()
                context.move_to(x=p1[0], y=p1[1])
                context.line_to(x=p2[0], y=p2[1])
                context.stroke(color=theme['stick'], line_width=1, dotted=True)

        # Draw stars from Yale Bright Star Catalogue
        for star_descriptor in fetch_bright_star_list()['stars'].values():
            ra, dec, mag = star_descriptor[:3]

            # Discard stars fainter than mag 4
            if mag == "-" or float(mag) > 4.0:
                continue

            lng, lat = self.ra_dec_to_ecliptic_coordinates(ra=ra * 12 / 180, dec=dec)

            # If we're making a southern hemisphere planisphere, we flip the sky upside down
            if is_southern:
                lng *= -1
                lat *= -1

            r = radius(dec=lat, latitude=latitude)
            if r > r_2:
                continue

            # Represent each star with a small circle
            context.begin_path()
            context.circle(centre_x=-r * cos(lng * unit_deg), centre_y=-r * sin(lng * unit_deg),
                           radius=0.18 * unit_mm * (5 - mag))
            context.fill(color=theme['star'])

        # Write constellation names
        context.set_font_size(0.7)
        context.set_color(theme['constellation'])

        # Open a list of the coordinates where we place the names of the constellations
        with open("raw_data/constellation_names.dat") as f_in:
            for line in f_in:
                line = line.strip()

                # Ignore blank lines and comment lines
                if (len(line) == 0) or (line[0] == '#'):
                    continue

                # Split line into words
                name, ra_str, dec_str = line.split()[:3]

                # Translate constellation name into the requested language, if required
                if name in text[language]['constellation_translations']:
                    name = text[language]['constellation_translations'][name]

                lng, lat = self.ra_dec_to_ecliptic_coordinates(ra=float(ra_str), dec=float(dec_str))

                # If we're making a southern hemisphere planisphere, we flip the sky upside down
                if is_southern:
                    lng *= -1
                    lat *= -1

                # Render name of constellation, with _s turned into spaces
                name2: str = re.sub("_", " ", name)
                r = radius(dec=lat, latitude=latitude)
                if r > r_2:
                    continue
                p: tuple[float, float] = (-r * cos(lng * unit_deg), -r * sin(lng * unit_deg))
                a: float = atan2(p[0], p[1])
                context.text(text=name2, x=p[0], y=p[1], h_align=0, v_align=0, gap=0, rotation=unit_rev / 2 - a)

        # Draw arrow for lining up with the year scale
        context.begin_path()
        context.move_to(x=0, y=-r_4)
        context.line_to(x=-(r_5 - r_4) * 0.4, y=-r_5)
        context.line_to(x=(r_5 - r_4) * 0.4, y=-r_5)
        context.fill()

        context.circular_text(text="SELECT YEAR",
                              centre_x=0, centre_y=0, radius=r_6,
                              azimuth=90,
                              spacing=1, size=-1.2)

        # Draw the dividing line between the date scale and the star chart
        context.begin_path()
        context.circle(centre_x=0, centre_y=0, radius=r_2)
        context.stroke(color=theme['date'], line_width=1, dotted=False)


# Do it right away if we're run as a script
if __name__ == "__main__":
    # Fetch command line arguments passed to us
    arguments = fetch_command_line_arguments(default_filename=StarWheel().default_filename())

    # Render the star wheel for the planisphere
    StarWheel(settings={
        'southern': arguments['southern'],
        'language': 'en',
        'theme': arguments['theme'],
    }).render_to_file(
        filename=arguments['filename'],
        img_format=arguments['img_format'],

    )
