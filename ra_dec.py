#!/usr/bin/python3
# ra_dec.py
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
Render the optional ra-dec grid of the precession planisphere.
"""

from math import atan2
from numpy import arange
from typing import Dict, List, Tuple

from constants import radius, transform, pos
from constants import unit_deg, unit_rev, unit_mm, inclination_ecliptic, central_hole_size
from graphics_context import BaseComponent, GraphicsContext
from settings import fetch_command_line_arguments
from text import text


class RaDecGrid(BaseComponent):
    """
    Render the optional ra-dec grid of the precession planisphere.
    """

    def default_filename(self) -> str:
        """
        Return the default filename to use when saving this component.
        """
        return "ra_dec_grid"

    def bounding_box(self, settings: dict) -> Dict[str, float]:
        """
        Return the bounding box of the canvas area used by this component.

        :param settings:
            A dictionary of settings required by the renderer.
        :return:
         Dictionary with the elements 'x_min', 'x_max', 'y_min' and 'y_max' set
        """

        latitude: float = 90 - inclination_ecliptic

        bounding_box: Dict[str, float] = {
            'x_min': 0,
            'x_max': 0,
            'y_min': 0,
            'y_max': 0
        }

        # Trace around the equator, keeping track of minimum and maximum coordinates
        dec_edge: float = -12

        path: List[Tuple[float, float]] = [
            transform(alt=dec_edge, az=az, latitude=latitude) for az in arange(0, 360.5, 1)
        ]

        for p in path:
            r_b: float = radius(dec=p[1] / unit_deg, latitude=latitude)
            position: Dict[str, float] = pos(r_b, p[0])
            bounding_box['x_min'] = min(bounding_box['x_min'], position['x'])
            bounding_box['x_max'] = max(bounding_box['x_max'], position['x'])
            bounding_box['y_min'] = min(bounding_box['y_min'], position['y'])
            bounding_box['y_max'] = max(bounding_box['y_max'], position['y'])

        return bounding_box

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

        latitude: float = 90 - inclination_ecliptic
        language: str = settings['language']

        context.set_font_size(0.9)

        # Set altitude of outer edge of ra-dec grid, including margin for gluing instructions
        dec_edge: float = -10
        ra_step: float = 1

        # Draw equator (declination 0), and line to cut around edge of window (declination dec_edge)
        dec: float
        for dec in (dec_edge, 0):
            # Draw a line, segment by segment, taking small steps in azimuth
            path: List[Tuple[float, float]] = [
                transform(alt=dec, az=ra, latitude=latitude) for ra in arange(0, 360.5, ra_step)
            ]

            # Project line from equatorial coordinates into planispheric coordinates
            context.begin_path()
            for i, p in enumerate(path):
                r_b: float = radius(dec=p[1] / unit_deg, latitude=latitude)
                if i == 0:
                    context.move_to(**pos(r_b, p[0]))
                else:
                    context.line_to(**pos(r_b, p[0]))
            context.stroke()

            if dec == dec_edge:
                # Draw the central hole in the middle of the viewing window
                context.begin_sub_path()
                context.circle(centre_x=0, centre_y=0, radius=central_hole_size)
                context.stroke()

                # Create clipping area, excluding central hole
                context.clip()

        # Draw lines of constant declination
        context.begin_path()
        for dec in range(10, 85, 10):
            path: List[Tuple[float, float]] = [
                transform(alt=dec, az=ra, latitude=latitude) for ra in arange(0, 360.5, 1)
            ]
            for i, p in enumerate(path):
                r_b: float = radius(dec=p[1] / unit_deg, latitude=latitude)
                if i == 0:
                    context.move_to(**pos(r_b, p[0]))
                else:
                    context.line_to(**pos(r_b, p[0]))
        context.stroke(color=(0.5, 0.5, 0.5, 1))

        # Draw lines of constant right ascension, and 1 hour intervals
        context.begin_path()
        for ra in arange(0, 359, 15):
            path: List[Tuple[float, float]] = [
                transform(alt=dec, az=ra, latitude=latitude) for dec in arange(0, 90.1, 1)
            ]
            for i, p in enumerate(path):
                r_b: float = radius(dec=p[1] / unit_deg, latitude=latitude)
                if i == 0:
                    context.move_to(**pos(r_b, p[0]))
                else:
                    context.line_to(**pos(r_b, p[0]))
        context.stroke(color=(0.5, 0.5, 0.5, 1))

        # Gluing labels
        def make_gluing_label(azimuth: float) -> None:
            pp: Tuple[float, float] = transform(alt=0, az=azimuth - 0.01, latitude=latitude)
            r: float = radius(dec=pp[1] / unit_deg, latitude=latitude)
            p: Dict[str, float] = pos(r, pp[0])

            pp2: Tuple[float, float] = transform(alt=0, az=azimuth + 0.01, latitude=latitude)
            r2: float = radius(dec=pp2[1] / unit_deg, latitude=latitude)
            p2: Dict[str, float] = pos(r2, pp2[0])

            p3: List[float] = [p2[i] - p[i] for i in ('x', 'y')]
            tr: float = -unit_rev / 4 - atan2(p3[0], p3[1])

            context.text(text=text[language]["glue_here"],
                         x=p['x'], y=p['y'],
                         h_align=0, v_align=1, gap=unit_mm, rotation=tr)

        # Write the text "Glue here" at various points around the equator
        context.set_font_style(bold=True)
        context.set_color(color=(0, 0, 0, 1))
        make_gluing_label(azimuth=0)
        make_gluing_label(azimuth=90)
        make_gluing_label(azimuth=180)
        make_gluing_label(azimuth=270)


# Do it right away if we're run as a script
if __name__ == "__main__":
    # Fetch command line arguments passed to us
    arguments = fetch_command_line_arguments(default_filename=RaDecGrid().default_filename())

    # Render the alt-az grid
    RaDecGrid(settings={
        'language': 'en'
    }).render_to_file(
        filename=arguments['filename'],
        img_format=arguments['img_format']
    )
