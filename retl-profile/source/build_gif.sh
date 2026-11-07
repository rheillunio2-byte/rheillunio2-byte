#!/bin/sh
# Build ../assets/hero-animation.gif from ./frames  (first run: python3 render_hero.py frames)
ffmpeg -y -framerate 20 -i frames/f%03d.png -vf "palettegen=max_colors=96:stats_mode=diff" palette.png
ffmpeg -y -framerate 20 -i frames/f%03d.png -i palette.png -lavfi "paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" -loop 0 ../assets/hero-animation.gif
