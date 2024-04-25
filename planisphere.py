#!/usr/bin/python3
# planisphere.py
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
This is the top level script for drawing all the parts needed to build
planispheres which demonstrate the precession of the equinoxes in both the
northern and southern skies. They are rendered in PDF, SVG and PNG image
formats.

Additionally, we use LaTeX to build a summary document for each hemisphere,
which includes all the parts needed to build a planisphere for that
hemisphere, and instructions as to how to put them together.
"""

import os
import subprocess
import time

from typing import Dict, Union

import text
from ra_dec import RaDecGrid
from holder import Holder
from settings import fetch_command_line_arguments
from starwheel import StarWheel

# Create output directory
os.system("rm -Rf output")
os.system("mkdir -p output/planispheres output/planisphere_parts")

arguments: Dict[str, Union[int, str]] = fetch_command_line_arguments()
theme: str = arguments['theme']

# Render planisphere in all available languages
language: str
for language in text.text:

    # Render climates for both northern and southern hemispheres
    southern: bool
    for southern in [False, True]:

        # A dictionary of common substitutions
        subs: Dict[str, Union[str, float]] = {
            'dir_parts': 'output/planisphere_parts',
            'dir_out': 'output/planispheres',
            'ns': "S" if southern else "N",
            'ns_full': 'southern' if southern else 'northern',
            'lang': language,
        }

        settings: Dict[str, Union[str, bool]] = {
            'language': language,
            'southern': southern,
            'theme': theme
        }

        # Render the various parts of the planisphere
        StarWheel(settings=settings).render_all_formats(
            filename="{dir_parts}/starwheel_{ns}_{lang}".format(**subs)
        )

        Holder(settings=settings).render_all_formats(
            filename="{dir_parts}/holder_{ns}_{lang}".format(**subs)
        )

        RaDecGrid(settings=settings).render_all_formats(
            filename="{dir_parts}/ra_dec_grid_{ns}_{lang}".format(**subs)
        )

        # Copy the PDF versions of the components of this astrolabe into LaTeX's working directory, to produce a
        # PDF file containing all the parts of this astrolabe
        os.system("mkdir -p doc/tmp")
        os.system("cp {dir_parts}/starwheel_{ns}_{lang}.pdf doc/tmp/starwheel.pdf".format(**subs))
        os.system("cp {dir_parts}/holder_{ns}_{lang}.pdf doc/tmp/holder.pdf".format(**subs))
        os.system("cp {dir_parts}/ra_dec_grid_{ns}_{lang}.pdf doc/tmp/ra_dec.pdf".format(**subs))

        with open("doc/tmp/lat.tex", "wt") as f:
            f.write(r"{ns_full}".format(**subs))

        # Wait for cairo to wake up and close the files
        time.sleep(1)

        # Build LaTeX documentation
        for build_pass in range(3):
            subprocess.check_output("cd doc ; pdflatex planisphere.tex".format(**subs), shell=True)

        os.system("mv doc/planisphere.pdf "
                  "{dir_out}/planisphere_{ns}_{lang}.pdf".format(**subs))

        # For the English language planisphere, create a symlink with no language suffix in the filename
        if language == "en":
            os.system("ln -s planisphere_{ns}_en.pdf "
                      "{dir_out}/planisphere_{ns}.pdf".format(**subs))

        # Clean up the rubbish that LaTeX leaves behind
        os.system("cd doc ; rm -f *.aux *.log *.dvi *.ps *.pdf")
