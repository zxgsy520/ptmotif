#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import gzip
import json
import math
import logging
import argparse

LOG = logging.getLogger(__name__)

__version__ = "1.1.0"
__author__ = ("Xingguo Zhang",)
__email__ = "invicoun@foxmail.com"
__all__ = []


CONF = """\
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
 <!-- Created with Method Draw - http://github.com/duopixel/Method-Draw/ -->
 <g>
  <title>background</title>
  <rect fill="#fff" id="canvas_background" height="{height}" width="{width}" y="-1" x="-1"/>
  <g display="none" overflow="visible" y="0" x="0" height="100%" width="100%" id="canvasGrid">
   <rect fill="url(#gridpattern)" stroke-width="0" y="0" x="0" height="100%" width="100%"/>
  </g>
 </g>
 <g>
  <title>Layer 1</title>
{data}
 </g>
</svg>\
"""


def ipd_line(id, x1, y1, x2, y2, width="1.5", stroke="#000",fill="none"):

    linecap = "undefined"
    linejoin = "undefined"

    string = '''  \
<\
line stroke-linecap="{linecap}" \
stroke-linejoin="{linejoin}" \
id="{id_name}" \
y2="{y2}" \
x2="{x2}" \
y1="{y1}" \
x1="{x1}" \
stroke-width="{width}" \
stroke="{stroke}" \
fill="{fill}"\
/>\
'''.format(
           linecap=linecap,
           linejoin=linejoin,
           id_name=id,
           y2=y2,
           x2=x2,
           y1=y1,
           x1=x1,
           width=width,
           stroke=stroke,
           fill=fill
        )

    return string


def ipd_text(id, x, y, content, stroke="#000", font_size= "14", fill="#000000"):

    space="preserve"
    anchor="start"

    string = '''  \
<text \
stroke="{stroke}" \
xml:space="{space}" \
text-anchor="{anchor}" \
font-family="Helvetica, Arial, sans-serif" \
font-size="{font_size}" \
id="{id}" \
y="{y}" \
x="{x}" \
fill-opacity="null" \
stroke-opacity="null" \
stroke-width="0" \
fill="{fill}"\
>{content}</text>\
'''.format(
           stroke=stroke,
           space=space,
           anchor=anchor,
           font_size=font_size,
           id=id,
           x=x,
           y=y,
           fill=fill,
           content=content
        )

    return string


def ipd_label(id, x, y, label="",transform = 0, stroke="#000000" , font_size="24", font="", fill="#000"):

    space = "preserve"
    text_anchor = "start"
    tx = x
    ty = y

    if len(font)==0:
        font = "Helvetica, Arial, sans-serif"

    string = '''  \
<text stroke="{stroke}" \
transform="rotate({transform} {tx},{ty})" \
xml:space="{space}" \
text-anchor="{text_anchor}" \
font-family="{font}" \
font-size="{font_size}" \
id="{id}" \
y="{y}" \
x="{x}" \
fill-opacity="null" \
stroke-opacity="null" \
stroke-width="0" \
fill="{fill}"\
>{label}</text>
'''.format(
           stroke=stroke,
           transform=transform,
           tx=tx,
           ty=ty,
           space=space,
           text_anchor=text_anchor,
           font=font,
           font_size=font_size,
           id=id,
           y=y,
           x=x,
           fill=fill,
           label=label
        )

    return string


def ipd_post(id, x, y, height,  width, stroke="#000" ,fill="#000000"):

    fill_opacity="null"
    stroke_opacity="null"

    string = '''  \
<rect id="{id}" \
height="{height}" \
width="{width}" \
y="{y}" \
x="{x}" \
fill-opacity="{fill_opacity}" \
stroke-opacity="{stroke_opacity}" \
stroke-width="0" \
stroke="{stroke}"
fill="{fill}"/>
'''.format(
           id=id,
           height=height,
           width=width,
           y=y,
           x=x,
           fill_opacity=fill_opacity,
           stroke_opacity=stroke_opacity,
           stroke=stroke,
           fill=fill
            )

    return string


def main_axis(fig_length, fig_height, frame, av_height, height):

    config = ""
    ystart_x = frame
    ystart_y = frame
    yend_x = frame
    yend_y = fig_height-frame

    xstart_x = frame
    xstart_y1 = fig_height/2.0-av_height
    xstart_y2 = fig_height/2.0+av_height
    xstart_y3 = fig_height/2.0+av_height*height
    xend_x = fig_length-frame

    config += ipd_line("yaxis_1", ystart_x, ystart_y, yend_x, yend_y)+"\n"
    config += ipd_line("xaxis_2", xstart_x, xstart_y1, xend_x, xstart_y1)+"\n"
    config += ipd_line("yaxis_3", xstart_x, xstart_y2, xend_x, xstart_y2)+"\n"
    config += ipd_line("yaxis_4", xstart_x, xstart_y3, xend_x, xstart_y3)+"\n"
    return config


def axis_xscale(frame, fig_height, av_height, height, main_len=8, minor_len=4, interval=0.5):

    config = ""
    n = 0
    x1 = frame
    main_x = frame-main_len
    minor_x = frame-minor_len

    for i in range(0, height):
        n +=1
        name = "pxscale_main"+str(n)
        y = fig_height/2.0-(i+1)*av_height
        config += ipd_line(name, x1, y, main_x, y)+"\n"

        name = "pxscale_minor"+str(n)
        y = fig_height/2.0-i*av_height-0.5*av_height
        config += ipd_line(name, x1, y, minor_x, y)+"\n"

        name = "nxscale_minor"+str(n)
        y = fig_height/2.0+(i+1)*av_height
        config += ipd_line(name, x1, y, main_x, y)+"\n"

        name = "nxscale_minor"+str(n)
        y = fig_height/2.0+i*av_height+0.5*av_height
        config += ipd_line(name, x1, y, minor_x, y)+"\n"

    return config


def axis_yscale(frame, fig_height, height, av_height, max_x, hist_space, av_length,  main_len=8, minor_len=4, interval=1, space=5):

    config = ""
    n = 0
    y1 = fig_height/2.0+av_height*height
    main_y = y1+main_len
    minor_y = y1+minor_len

    for i in range(0,max_x):
        n +=1
        name = "yscale_"+str(n)
        x = av_length*i+hist_space+frame+(av_length-hist_space)/2.0

        if i%space == 0:
            config += ipd_line(name, x, y1, x, main_y)+"\n"
        config += ipd_line(name, x, y1, x, minor_y)+"\n"

    return config


def axis_yscale_value(fig_height, frame, height, av_height):

    n = 0
    config = ""
    content = av_height/2.0

    for i in range(1, height+1):
        n +=1
        name = "pyscale_value"+str(n)
        content = i
        zx = frame-20
        zy = fig_height/2.0-i*av_height+5
        config += ipd_text(name, zx, zy, content)+"\n"

        name = "nyscale_value"+str(n)
        fx = frame-20
        fy = fig_height/2.0+i*av_height+5
        config += ipd_text(name, fx, fy, content)+"\n"

    return config


def main_picture(px, py, nx, ny, sx, fig_length, fig_height, frame, space, hist_space):

    n = 0
    s = 0
    config = ""
    max_x = max(len(px), len(nx))
    max_y = max(max(py), max(ny))
    height = int(math.ceil(max_y))
    av_height = (fig_height-2.5*frame)/(2*height)
    av_length = (fig_length-2.5*frame)/max_x
    center = av_height/2.0
    width = av_length-hist_space

    for i in range(max_x):

        if i%space ==0:
            s += 1
            name = "psite"+str(n)
            px_site = av_length*i+hist_space+frame+width/5
            py_site = fig_height/2.0+av_height*height+22
            config += ipd_text(name, px_site-len(str(sx[i]))*2, py_site, sx[i])+"\n"

        n +=1
        pipd_value = px[i]
        nipd_value = nx[i]
        ptname = "pxscale_value"+str(n)
        phname = "phist"+str(n)
        ntname = "nxscale_value"+str(n)
        nhname = "nhist"+str(n)

        pxt = av_length*i+hist_space+frame+width/5
        pyt = fig_height/2.0-0.5*av_height+av_height/3.5
        config += ipd_text(ptname, pxt, pyt, pipd_value)+"\n"
        pxh = av_length*i+hist_space+frame
        post_height = av_height*py[i]
        post_height = abs(post_height-av_height)
        pyh = fig_height/2.0-av_height
        width = av_length-hist_space
        if py[i]>=1:
            config += ipd_post(phname, pxh, pyh-post_height, post_height, width)+"\n"
        else:
            config += ipd_post(phname, pxh, pyh, post_height, width)+"\n"

        nxt = pxt
        nyt = fig_height/2.0+0.5*av_height-av_height/3.5
        config += ipd_text(ntname, nxt, nyt, nipd_value)+"\n"
        nxh = pxh
        post_height = av_height*ny[i]
        post_height = abs(post_height-av_height)
        nyh = fig_height/2.0+av_height
        width = av_length-hist_space
        if ny[i]>=1:
            config += ipd_post(nhname, nxh, nyh, post_height,  width)+"\n"
        else:
            config += ipd_post(nhname, nxh, nyh-post_height, post_height,  width)+"\n"

    return config

def out_conf(prepare_data, out_name, fig_length, fig_height):

    with open(out_name, 'w') as fh:
        fh.write(CONF.format(data=prepare_data, width=fig_length, height=fig_height))


def draw_ipdratio(px, py, nx, ny, sx, out_name, fig_length=1200, fig_height=600, frame=60, space=5, hist_space=5):

    config = ""
    max_x = max(len(px), len(nx))
    max_y = max(max(py), max(ny))
    height = int(math.ceil(max_y))
    av_height = (fig_height-2.5*frame)/(2*height)
    av_length = (fig_length-2.5*frame)/max_x
    center = av_height/2.0

    config += main_axis(fig_length, fig_height, frame, av_height, height)
    config += axis_xscale(frame, fig_height, av_height, height)
    config += axis_yscale(frame, fig_height, height, av_height, max_x, hist_space, av_length)
    config += axis_yscale_value(fig_height, frame, height, av_height)
    config += main_picture(px, py, nx, ny, sx, fig_length, fig_height, frame, space, hist_space)
    config += ipd_label("ylabel1", frame/2.0+5, fig_height/2.0+frame/1.5, "IPD ratio" ,-90)
    config += ipd_label("xlabel1", fig_length/2.0-frame/2.0, fig_height-frame/2.0, "Genome position")

    out_conf(config, out_name, fig_length, fig_height)

    return 0


def read_csv(file):

    if file.endswith(".gz"):
        fc = gzip.open(file)
    else:
        fc = open(file)

    n = 0
    head = ""
    for line in fc:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        line = line.strip().replace('"', '')
        if not line:
            continue
        line  = line.split(',')
        if n == 0:
            head = line
        else:
            yield [head, line, n]
        n += 1
    fc.close()

    return 0


def plot_ipd(file, tigid="", start=1, length=1200, height=600, distance=600):

    end = start + 40
    px = []
    py = []
    nx = []
    ny = []
    sx = []

    for head, line, n in read_csv(file):
        seqid, tpl, strand, base = line[0], int(line[1]), int(line[2]), line[3]
        ipdratio = float(line[8])

        if tigid != seqid:
            continue
        if tpl < start:
            continue
        if tpl > end:
            break

        if strand == 0:
            sx.append(tpl)
            px.append(base)
            py.append(ipdratio)
            continue
        if strand == 1:
            nx.append(base)
            ny.append(ipdratio)

    out_name  = "%s_%s_%s_idp.svg" % (tigid, start, end)

    draw_ipdratio(px, py, nx, ny, sx, out_name, length, height, distance)

    return 0


def add_hlep_args(parser):

    parser.add_argument("input", metavar='FILE', type=str,
        help="Input files.")
    parser.add_argument("-id", "--tigid", metavar='STR', type=str, default='tig0001',
        help="Input sequence id, default='tig0001'.")
    parser.add_argument("-s", "--start", metavar='INT', type=int, default=0,
        help="Input start position, default=0.")
    parser.add_argument('-ph', '--height', type=int, default=600,
        help='Set picture height(default=600).')
    parser.add_argument('-pl', '--length', type=int, default=1200,
        help='Set picture length,(default=1200).')
    parser.add_argument('-d', '--distance', type=int, default=60,
        help='Set border distance,(default=60).')

    return parser


def main():
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
name:
        plot_ipd.py -- Draw a separate graph of ipdratio values
attention:
        plot_ipd.py WP3NRDnd1.modifications.csv.gz -id tig0001 -s 200
version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_hlep_args(parser)
    args = parser.parse_args()

    plot_ipd(args.input, args.tigid, args.start, args.length, args.height, args.distance)


if __name__ == "__main__":
    main()
