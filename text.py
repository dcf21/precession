# text.py
# -*- coding: utf-8 -*-
#
# The python script in this file makes the various parts of a precession
# planisphere.
#
# Copyright (C) 2014-2021 Dominic Ford <dcf21-www@dcford.org.uk>
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

# A list of text strings, which we can render in various languages

text = {
    "en":
        {
            "title": "PRECESSION OF THE EQUINOXES",
            "instructions_1": "Turn the star wheel until the arrow on its edge lines up with the scale of years marked around the top of the planisphere.",
            "instructions_2": "The viewing window will now show all of the stars in the celestial {cardinal}ern hemisphere in this year.",
            "instructions_3": "The grid of lines marked onto the transparent plastic window indicates the right ascension and declination of the stars behind. As stars move relative to the lines, their celestial coordinates change over time.",
            "instructions_4": (
                r"The precession of the equinoxes is a gradual changing in the direction of the Earth's rotation axis, which causes the position of the celestial poles to drift through the constellations at a continuous rate of roughly 20 arcseconds per year. Although this effect is small on short timescales, the accumulated drift adds up to about one Moon diameter per century. Currently the Earth's north celestial pole points close to the star Polaris, but this will not always be the case. By 2500, Polaris will be several degrees away from the true celestial pole.",
                r"",
                r"This special design of planisphere demonstrates the effect. The sky is projected onto the star wheel with the north ecliptic pole at the center. The grey lines marked onto the transparent plastic window mark the right ascension and declination of the stars behind.",
                r"",
                r"As the star wheel is rotated, the position of the north celestial pole turns in circles around the ecliptic pole, simulating how the celestial coordinates of stars change over time due to the precession of the equinoxes.",
                r""),
            "more_info": "For more information, see https://in-the-sky.org/precession       \u00A9 Dominic Ford 2021.",
            "glue_here": "GLUE HERE",
            "cut_out_instructions": (
                "Cut out this shaded area with scissors.",
                "",
                "It will become a viewing window through which to look at the star wheel behind."
            ),
            "constellation_translations": {
            }
        }
}
