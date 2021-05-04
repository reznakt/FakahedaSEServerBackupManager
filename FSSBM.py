#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2021 Tomáš Režňák
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
A simple module providing an overview of one's FakaHeda SE server and automatic backup and restore functions.

API reference: https://forum.fakaheda.eu/viewtopic.php?f=126&t=35153
"""

from __future__ import annotations

__title__ = "FakahedaSEServerBackupManager"
__abbrev__ = "FSSBM"
__author__ = "Tomáš Režňák"
__version__ = "1.0"
__year__ = 2021

import datetime
import io
import json
import os
import shutil
import sys
import threading
import time
import typing

import PySimpleGUI as sg
import PySimpleGUIQt as sgqt
import ftputil
import requests
from PIL import Image
from ftputil import error

# -------------------------------------------------------------------------------------------------------------------- #
#                                                  STATICS B64
# -------------------------------------------------------------------------------------------------------------------- #
ICON_SUCCESS = b"""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAd
TAAAOpgAAA6mAAAF3CculE8AAAAolBMVEVqvWVrvmZrvmVqvWVrvmZqvWVqvWVqvWVqvmVwwWpqvWVqvWVvwWpqvWVrvmZrvmZrvmZrvmZrvmZqvWVqvWVqv
WVrvmZqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvmVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVqvWVrvmZqv
mZqvmX///+v9vsWAAAAMXRSTlMAAAACAzil5f0BCJYBvvz9/vn6PPyi++NUv+HsNIz71H/z9DlhhkpJVf73Tfr9Z0/1pBbgVAAAAAFiS0dENd622WsAAAAHd
ElNRQflARYPNghO1F8YAAAApklEQVQY02VPyRaCQAwrsjoIU2VRUXHHfSH6/99mZ7hJD31t0pekRK7n+EEYRWHgO55L5A5V3MJWG6uRICpBqhlgnSJRRE6Ms
eU51RPEDmU5dzt/pOUZFdDgUtp0NkeJgirLp1gsBysBKqrBWG+2uz0djFktQIkjNSc6X2CBSi6uN6LmDqNeWVE8nq+32bWIGlvW+LLhjW0XTJusMkiwXvT+c
3/v/wCtHhujNj8VNAAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyMS0wMS0yMlQxNTo1Mzo1OCswMDowMP6FMukAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjEtMDEtM
jJUMTU6NTM6NTgrMDA6MDCP2IpVAAAAAElFTkSuQmCC"""

ICON_ERROR = b"""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTA
AAOpgAAA6mAAAF3CculE8AAAAclBMVEX+QED/QUH9QED+QED/QUH+QED+QED+QED+QED/RUX+QED+QED/RET+QED/QUH/QUH/QUH/QUH+QED+QED+QED+QED
+QED+QED+QED+QED9QED+QED+QED+QED+QED+QED+QED+QED/Rkb+QED/QUH///8XMY/qAAAAI3RSTlMAAAACAzil5f0BCJYBvvz7/vk8/OHx8OCi5wT25kl
K+05NAUXjv0MAAAABYktHRCXDAckPAAAAB3RJTUUH5QEWDzgOOTTXowAAAJZJREFUGNNlj+kOgzAMg10Kg7XjWFvuG/L+z7gU0LSJ/PpiKY4NyFBEjzhJ4kc
kQgnIp9I7HbNr9ZIIVEpZXhAVeUapCiA0vXnjIQYtYCyTK4mqmnVr0FBObWf63nQDYwNHBdkR04TRMjrM3t8uwGo9zZewAsslXCfj98SbDqdpe5geb+uKqHT
n21uwW3S5/ZbbfN3/+h81URU9/Kh2fgAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyMS0wMS0yMlQxNTo1NjowNCswMDowMJfsnb0AAAAldEVYdGRhdGU6bW9kaWZ
5ADIwMjEtMDEtMjJUMTU6NTY6MDQrMDA6MDDmsSUBAAAAAElFTkSuQmCC"""

DEFAULT_ICON = b"""iVBORw0KGgoAAAANSUhEUgAAABkAAAASCAYAAACuLnWgAAAACXBIWXMAAAsTAAALEwEAmpwYAAAJsWlUWHRYTUw6Y29tLmFkb2JlL
nhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuc
zptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmL
XN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb
20veGFwLzEuMC8iPgogICAgICAgICA8eG1wOkNyZWF0b3JUb29sPlpvbmVyIFBob3RvIFN0dWRpbyBYPC94bXA6Q3JlYXRvclRvb2w+CiAgICAgIDwvcmRmO
kRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgI
CAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgI
CAgICAgICAgICAgICAgICAgCjw/eHBhY2tldCBlbmQ9InciPz7dPuZdAAABxElEQVQ4T7XVT4hOURjH8c8z3SmNEWVjaQwrC4kVKX8bEosxUkpSs/CnlGykK
Bv2LJkSGxazszBJGSlCWdhOsWQx5c9uyjwW933H+565Zkb41u3e+/s9p1/n3HOeW1mAzOzFCI5iK1bjO97iLsYjIucG/IaqFNpk5g6MYUNh9eFg63qcmcci4
ltR00VjSGYO4wF6S69gP8YzcwiD2IjPeB0RP9pF80IycwD3LB7QZq96+TZ3aB8z83RETNAQgvNYXoqL0BkAa/EoM/dFxLOmkC2lUPAUe0qxgQpX0B2Smf1Y1
qkVjEXEaGbexmhpNrCG1nJlZg8u4jJW/arpYhJnW8/nsB4759xm3kCVmYH7ON7tdzGFIxExAxExk5kjeKUOa+I9LlHP5KSFA77gcERMd4oRMZ2Zh/BS8+z71
BvgU4Uz3d48rmI2Mwci4kNbbG31VH/cW229g0E8ycxtFTaVbsHN1n1K9+mfKN6b6MeNCnMn8z+xq8I7bC+df0hWuGNpIesys7MRLrUrvKjUfeoEdhdmSQ9Wl
OIizOJ6FRGzra77EENF0d8wiwsR8byCiPiamQcwjFPqH9TKjgF/QqoP6bWImISf2j+BlvSimPoAAAAASUVORK5CYII="""

ICON_SETTINGS = b"""iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAACXBIWXMAAAsTAAALEwEAmpwYAAAJsWlUWHRYTUw6Y29tLmFkb2Jl
LnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpu
czptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRm
LXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5j
b20veGFwLzEuMC8iPgogICAgICAgICA8eG1wOkNyZWF0b3JUb29sPlpvbmVyIFBob3RvIFN0dWRpbyBYPC94bXA6Q3JlYXRvclRvb2w+CiAgICAgIDwvcmRm
OkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAg
ICAgICAgICAgICAgICAgICAgCjw/eHBhY2tldCBlbmQ9InciPz7dPuZdAAACvklEQVRIS73VT4hWZRTH8c/Ri0KWxSySAYWMiv5MCI2Nua+0QmgVlLQIiUqk
WljbQKgghCAiKl1kQQWVtHCRTUURVFApQSTIUKvZFJkzkZOmnhbPc507l/fNCawvvLzP/Z1z+d3nnPPc2/gfaPrCf8FQk8wM3IgV+CUipnopi2aoCdbhEAK/
Z+aqiJjr5SyKcyaZOYpX8TrexVrFAJYrO5rLzM04HREf1dh5aSAzR3BQKc/t2InxTt4yHMrMA9iGzMz7I+KdTs5Q2p2swtV1vQwTdd1lDR7pXO/OzP0Rcaaj
DaSBiDiSmY/j5U7sLL7FDNbjsk7sT2xfjAHz5Qps7OjTuDsivqnxldiDe2r8JL6s6/PSZOYkrlTK0fJQawARMZuZD+BmZSAuxXOZ+T1ei4jjbe4gGtza047j
k54mIk5k5kE8XKVt9f837KvrgTQ4Xf9bltTfIJb2BYO1BTS4UynBsxjBSmzGe528ti93dKSjmMXhjiYzl/YHoomIyRqcMF+ClzJzBh9HRGY5qHuwusZ/xURE
zNRrmbkcn+PnzNyC2/BpRJxqp2sUt7Q34HLlcE5l5iyux0Wd+BROQWZejKeVHY0p1flKGfsX8Vjbi+24oa5bluCantayAbvwBLbi0U7spPnDfJj5hj+v9GE9
9isGWyxs6lHl6ccwh8mq78VTyu7vxft4UNnF7sy8r4GIOJaZm3AX3o6IvzLzzXoTvKU88QhewL6I+LCW6gBG8WPUd1lm7sUzNf+Kc6MbEcfwRnutzH/LdESk
0vCtHX0O1ynHYHUdnq+Vpl+C73BT93z02alsGX7qBloi4kxmrsWTSsk+U3KvUko+hk1DTaJ8oI709T71TbAOqZyba/GHUq5xfDHU5F+yAx8oH7wfFLNdEXGW
f/78LpqImMYrkJnjONEacIFMutQBWsAFNxnE355s6ItR+L2UAAAAAElFTkSuQmCC"""

ICON_WHITE_DOT = b"""iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAJxWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJ
lZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1
QIENvcmUgNS41LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA
8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iPgogICAgICA
gICA8eG1wOkNyZWF0b3JUb29sPlpvbmVyIFBob3RvIFN0dWRpbyBYPC94bXA6Q3JlYXRvclRvb2w+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3J
kZjpSREY+CjwveDp4bXBtZXRhPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA
gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgCjw
/eHBhY2tldCBlbmQ9InciPz4KPD94cGFja2V0IGVuOT+UWh8XJ63Hws0AAADjSURBVBhXZY8vTsRgEEfffP9CN6mshxOA4ABIMKimem8ADtfUcAGSRXEDTC2
CIBAQwh1wFdhN2my/LoNpN9B9yWQm83sjxjGjqioz9p+/ezcNMcZza+0tcAJoWZavwzDchBA+duIwDEtjzL2IJNMhcOace4kxXnrvn13TNAtjzN1MAkBEFtb
aB+DIZVl2CuhcmhCRQwCnqhtA/sf7uLquP/M8XwPpPFRVBd4BXFEU2xhjbq19Ag5ExI/SBlj3fb+E8Wvv/VvXdcchhCvgAtiq6mPbtqs0Tb93IkCSJF/A9Vh
7/AJWr0oYcdErmQAAAABJRU5ErkJggg=="""

ICON_RELOAD = b"""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAALEwEAmpwYAAAJsWlUWHRYTUw6Y29tLmFkb2JlLn
htcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpucz
ptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLX
N5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb2
0veGFwLzEuMC8iPgogICAgICAgICA8eG1wOkNyZWF0b3JUb29sPlpvbmVyIFBob3RvIFN0dWRpbyBYPC94bXA6Q3JlYXRvclRvb2w+CiAgICAgIDwvcmRmOk
Rlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgIC
AgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgIC
AgICAgICAgICAgICAgICAgCjw/eHBhY2tldCBlbmQ9InciPz7dPuZdAAABW0lEQVQ4T6XTsWpVQRAG4G8uC/ZqejEIglpY6ANEMSA+gIiNQYxKGiEg2HjtDX
aS6AukUSxECILExkQshIC9+AAB7VLoWJy9526uuVr4w3B2/tkZZs8/U0wgM89gERdwHIFveI/nEbHd3D1SGucQVnAHgxFfMVttITPXcRsPsFPok1/jYp8yHV
d13c3g+qiDx/Ynv9F18xE/cRZLuFbjM/WrZOYp3B0RGEbEo8aHLWxl5lFcagMFt4zfvHFAMsjMFRPJdAXmGv9Jc+6RmYfxoVqLTwXHWqI594iIXbyY5Ok6+C
8UfMXp6p/DRh89AJl5AsPqfi94Z1zgnn8UwH1jOV8WPNNpPMB8Zj78ixI3sdBQqyUivmTmU10RGGbmed0gbeOXPwcJXkXE29FPXMZJ42m8XG0aPuMGVYWI2M
vMK6YvU4t1LEbEDxoZI2IPS5m5Zv86D3TrvGlineE3KxhpsO1CfqQAAAAASUVORK5CYII="""

# -------------------------------------------------------------------------------------------------------------------- #
#                                               INIT & CONFIGURATION
# -------------------------------------------------------------------------------------------------------------------- #
# SYSTEM
REDIRECT_STDOUT_STDERR_TO_FILE = True
LOG_FILENAME = "latest.log"

# GUI
sg.MENU_SHORTCUT_CHARACTER = '&'
_COLOR_LIGHT_GREY = "#000000"
_LIST_FOREGROUND_COLOR = "#555555"
MIN_AUTO_BACKUP_INTERVAL = 5
MAX_AUTO_BACKUP_INTERVAL = 60

# PATHS
CONFIG_FILENAME = os.path.abspath("config.json")
_DEFAULT_CONFIG = {"fakaheda": {
    "api_url": "https://www.fakaheda.eu/fhapi/v1/servers", "server_id": 123456, "api_token": "",
    "json_feed_url": "https://query.fakaheda.eu/{server_ip}{port}.feed"},
    "ftp": {"host": "https://example.org/", "user": "user", "password": "", "dir": "/Saves", "blacklist": ["/Backup"]},
    "backups_dir": "backups", "auto_backup": False, "interval": MIN_AUTO_BACKUP_INTERVAL, "last_run": 10 ** 9}


# -------------------------------------------------------------------------------------------------------------------- #
#                                                     UTILS
# -------------------------------------------------------------------------------------------------------------------- #
class Util:
    class ObjectifiedDict(dict):
        def __getattr__(self, item):
            return self.get(item)

        def __setattr__(self, key, value):
            self[key] = value

    class BackupRestorer:
        def __init__(self, backup: Backup):
            self.backup = backup
            self.action = None

        def run(self):
            self.action = "__SERVER_STOP__"
            print("[RESTORER] Stopping server...")
            server.stop()
            while True:
                if not server.status.is_running:
                    break
            time.sleep(5)

            self.action = "__UPLOAD__"
            print("[RESTORER] Uploading files...")
            Util.upload_backup(self.backup)

            self.action = "__SERVER_START__"
            print("[RESTORER] Starting server...")
            server.start()
            while True:
                if server.status.is_running:
                    break
            self.action = "__EXIT__"

    @staticmethod
    def get_folder_size(start_path: str):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size

    @classmethod
    def json_load(cls, filename: str, encoding: str = None):
        with open(filename, "r", encoding="utf-8" if encoding is None else encoding) as file:
            return json.load(file, object_hook=cls.ObjectifiedDict)

    @staticmethod
    def json_dump(filename: str, data: dict, encoding: str = None):
        with open(filename, "w", encoding="utf-8" if encoding is None else encoding) as file:
            json.dump(data, file, sort_keys=False, ensure_ascii=False, indent=4)

    @classmethod
    def get_config(cls):
        return cls.json_load(CONFIG_FILENAME)

    @classmethod
    def save_config(cls, data: dict):
        cls.json_dump(CONFIG_FILENAME, data)

    @staticmethod
    def to_megabytes(size: float):
        return "{:.2f} MB".format(size / (1024 ** 2))

    @staticmethod
    def menu_bar(
            menu_def: list[list],
            text_color: str = None,
            background_color: str = None,
            pad: typing.Union[
                tuple[int, int],
                tuple[tuple[int, int], tuple[int, int]],
                tuple[int, tuple[int, int]],
                tuple[tuple[int, int], int]
            ] = (0, 0)
    ):

        if text_color is None:
            text_color = sg.theme_text_color()
        if background_color is None:
            background_color = sg.theme_background_color()

        row = []
        for menu in menu_def:
            text = menu[0]
            if sg.MENU_SHORTCUT_CHARACTER in text:
                text = text.replace(sg.MENU_SHORTCUT_CHARACTER, '')
            if text.startswith(sg.MENU_DISABLED_CHARACTER):
                disabled = True
                text = text[len(sg.MENU_DISABLED_CHARACTER):]
            else:
                disabled = False
            row += [sg.ButtonMenu(text, menu, border_width=0, button_color=(text_color, background_color), key=text,
                                  pad=pad, disabled=disabled, font="Any 9 bold")]

        return sg.Column([row], background_color=background_color, pad=(0, 0), expand_x=True)

    @staticmethod
    def popup(*args, **kwargs):
        p = Popup(*args, **kwargs)
        return p.event

    @staticmethod
    def image_preprocessor(path: str, max_size: tuple[int, int] = (600, 300)):
        img = Image.open(path)
        img.thumbnail(max_size)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()

    @classmethod
    def img_from_url(cls, url: str, *args, **kwargs):
        data = requests.get(url, stream=True).raw
        return cls.image_preprocessor(data, *args, **kwargs)

    @staticmethod
    def download_backup():
        global ftp
        print("[BACKUP-DOWNLOAD] Downloading backup...")
        ftp = FTPManager(FTP_HOST, FTP_USER, FTP_PASSWORD)
        ftp.download_folder(FTP_DIR, os.path.join(BACKUPS_DIR, str(datetime.datetime.now().timestamp())), FTP_BLACKLIST)
        ftp.close()
        print("[BACKUP-DOWNLOAD] Backup downloaded")
        ftp = None

    @staticmethod
    def upload_backup(backup):
        global ftp
        print("[BACKUP-UPLOAD] Uploading backup...")
        ftp = FTPManager(FTP_HOST, FTP_USER, FTP_PASSWORD)
        ftp.upload_folder(os.path.join(BACKUPS_DIR, backup.path), FTP_DIR)
        ftp.close()
        print("[BACKUP-UPLOAD] Backup uploaded")
        ftp = None


class Logger:
    INPUT_STREAM_STDOUT = "stdout"
    INPUT_STREAM_STDERR = "stderr"
    STDOUT = sys.stdout
    STDERR = sys.stderr

    def __init__(self, output_stream: typing.TextIO, input_stream: str):
        if input_stream != self.INPUT_STREAM_STDOUT and input_stream != self.INPUT_STREAM_STDERR:
            raise AttributeError("input_stream must be either 'stdout' or 'stderr'")
        self.output_stream = output_stream
        self.input_stream = input_stream

    def write(self, string: str):
        if string and string != "\n":
            if self.input_stream == self.INPUT_STREAM_STDOUT:
                self.STDOUT.write(string + "\n")
                self.output_stream.write(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + ": " + string + "\n")
                self.output_stream.flush()
            else:
                self.STDERR.write(string)
                self.output_stream.write(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + ": [SYS_ERR] " + string.replace(
                        "\n", "") + "\n")
                self.output_stream.flush()

    def flush(self):
        pass


# -------------------------------------------------------------------------------------------------------------------- #
#                                                     API
# -------------------------------------------------------------------------------------------------------------------- #
class ServerException(BaseException):
    pass


class InvalidResponse(ServerException):
    pass


class Server:
    ENDPOINT_STATUS = "status"
    ENDPOINT_START = "start_async"
    ENDPOINT_STOP = "stop_async"
    ENDPOINT_RESTART = "restart_async"

    def __init__(self, host: str, server_id: int, token: str, json_feed_url: str):
        self.host = host
        self.server_id = server_id
        self.token = token
        self.json_feed_url = json_feed_url

        self.headers = {"Authorization": "Bearer " + self.token}
        self.url = API_BASE_URL + "/" + str(SERVER_ID)

    def send_request(self, endpoint: str):
        if endpoint:
            return requests.get(url=self.url + "/" + endpoint, headers=self.headers)

    @property
    def _json_feed(self) -> dict:
        return requests.get(url=self.json_feed_url).json()

    @property
    def status(self) -> Util.ObjectifiedDict:
        status_ = self.send_request(self.ENDPOINT_STATUS).json()
        if not status_.get("result"):
            raise InvalidResponse("InvalidResponse: " + repr(status_))
        return Util.ObjectifiedDict(status_ | self._json_feed)

    def start(self):
        print("[SERVER] Sending request to endpoint " + self.ENDPOINT_START)
        return self.send_request(self.ENDPOINT_START).status_code

    def stop(self):
        print("[SERVER] Sending request to endpoint " + self.ENDPOINT_STOP)
        return self.send_request(self.ENDPOINT_STOP).status_code

    def restart(self):
        print("[SERVER] Sending request to endpoint " + self.ENDPOINT_RESTART)
        return self.send_request(self.ENDPOINT_RESTART).status_code


class Player:
    def __init__(self, data: Util.ObjectifiedDict):
        self.data = data
        self.name = data.name
        self.score = data.score
        self.time = data.time
        self.kills = data.kills
        self.deaths = data.deaths
        self.ping = data.ping


class FTPManager(ftputil.FTPHost):
    class _IOStream:
        def __init__(self, total_size: float):
            self.total_size = total_size
            self.cum_size = 0

        def add_size(self, size: float):
            self.cum_size += size

        @property
        def progress(self):
            return "{:.2f} %".format((self.cum_size / self.total_size) * 100)

        @property
        def finished(self):
            return self.cum_size == self.total_size

    # ----------------------------------- #

    def __init__(self, *args, **kwargs):
        self.down_stream = None
        self.up_stream = None
        super().__init__(*args, **kwargs)
        self.def_wd = self.getcwd()

    def folder_size(self, folder: str, blacklist: list[str] = None):
        self.chdir(self.def_wd)
        self.chdir(folder)
        size = 0
        for item in self.walk("."):
            if not any(val in item[0] for val in (blacklist or [])):
                for file in item[2]:
                    size += self.path.getsize(self.path.join(item[0], file))
        self.chdir(self.def_wd)
        return size

    def download_folder(self, remote_folder: str, local_folder: str = None, blacklist: list[str] = None):
        if local_folder is not None:
            try:
                os.mkdir(local_folder)
            except OSError:
                pass

        self.down_stream = self._IOStream(self.folder_size(remote_folder, blacklist))

        self.chdir(self.def_wd)
        self.chdir(remote_folder)
        for item in self.walk("."):
            if not any(val in item[0] for val in (blacklist or [])):
                try:
                    os.mkdir(os.path.join(local_folder, item[0]))
                except OSError:
                    pass
                for file in item[2]:
                    self.download(self.path.join(item[0], file), self.path.join(local_folder, item[0], file),
                                  callback=lambda data: self.down_stream.add_size(len(data)))
        self.chdir(self.def_wd)

    def upload_folder(self, local_folder: str, remote_folder: str):
        self.up_stream = self._IOStream(Util.get_folder_size(local_folder))
        for item in os.listdir(local_folder):
            path = os.path.join(local_folder, item)
            rem_path = os.path.join(remote_folder, item)
            if os.path.isfile(path):
                self.upload(path, rem_path, callback=lambda data: self.up_stream.add_size(len(data)))
            elif os.path.isdir(path):
                try:
                    self.mkdir(rem_path)
                except ftputil.error.FTPError:
                    pass
                self.upload_folder(path, rem_path)


# -------------------------------------------------------------------------------------------------------------------- #
#                                                    GUI
# -------------------------------------------------------------------------------------------------------------------- #
class Backup:
    def __init__(self, path: str):
        self.path = path
        self.abspath = os.path.abspath(os.path.join(BACKUPS_DIR, self.path))
        self.name = next(os.walk(os.path.join(BACKUPS_DIR, self.path)))[1][0]
        self.size = Util.get_folder_size(os.path.join(BACKUPS_DIR, self.path)) / (1024 ** 2)
        self.date = datetime.datetime.fromtimestamp(float(self.path)).strftime("%Y-%m-%d %H:%M:%S")
        self.thumbnail = os.path.join(BACKUPS_DIR, self.path, self.name, "thumb.jpg")

    def __repr__(self):
        return ("<" + __name__ + "." + self.__class__.__name__ + " name=" + repr(self.name) + " size=" + repr(self.size)
                + " date=" + repr(self.date) + " path=" + repr(self.path) + ">")


class Scheduler:
    def __init__(self):
        self._stop_flag = False
        self.running = False
        self.thread_running = False

    def run(self):
        self._stop_flag = False
        thread = None

        while True:
            if not self._stop_flag:
                self.running = True

                if thread is not None and thread.is_alive():
                    self.thread_running = True
                else:
                    self.thread_running = False

                config = Util.get_config()
                interval = config.interval
                last_run = config.last_run

                if datetime.datetime.timestamp(
                        datetime.datetime.fromtimestamp(last_run) + datetime.timedelta(minutes=interval)
                ) <= datetime.datetime.now().timestamp():
                    config.last_run = datetime.datetime.now().timestamp()
                    Util.save_config(config)
                    print("[SCHEDULER] Starting task...")
                    thread = threading.Thread(target=lambda: Util.download_backup(), daemon=True)
                    thread.start()
            else:
                self.running = False
                break
            time.sleep(1)

    def stop(self):
        print("[SCHEDULER] Stopping scheduler...")
        self._stop_flag = True
        return self

    def start(self):
        print("[SCHEDULER] Starting scheduler...")
        threading.Thread(target=lambda: self.run(), daemon=True).start()

    @property
    def is_running(self):
        return self.running

    @property
    def is_thread_running(self):
        return self.thread_running


def update_status():
    global status

    while True:
        status = server.status
        time.sleep(1)


class Popup:
    def __init__(
            self,
            title: str,
            prompt: str,
            buttons: list[sg.Button],
            modal: bool = True,
            keep_on_top: bool = False,
            title_font: str = "Any 10",
            icon: typing.Union[bytes, str] = None
    ):
        self.layout = [
            [sg.Text(prompt, pad=((10, 10), (10, 10)))]
        ]
        self.layout.append([button for button in buttons])

        self.window = sg.Window(
            layout=self.layout,
            title=title,
            modal=modal,
            keep_on_top=keep_on_top,
            use_custom_titlebar=True,
            use_ttk_buttons=True,
            use_default_focus=False,
            titlebar_font=title_font,
            titlebar_icon=icon,
            disable_close=True
        )

        while True:
            self.event = self.window.read()[0]
            if self.event != sg.TIMEOUT_EVENT and self.event is not None:
                break
        self.window.close()


class RestoreWindow:
    def __init__(self, restorer: Util.BackupRestorer):
        self.restorer = restorer
        self.status = ""
        self.window = None
        self.action = "__SERVER_STOP__"

        self.layout = [[
            sg.Frame("", element_justification="c", relief=sg.RELIEF_RAISED, layout=[
                [
                    sg.Text("Restoring backup " + self.restorer.backup.name + "...", font="Any 11 bold",
                            pad=((20, 20), (20, 0)))
                ],
                [
                    sg.ProgressBar(100, size=(15, 15), pad=((0, 0), (20, 0)), border_width=0, key="__PROGRESS__")
                ],
                [
                    sg.Text("", size=(25, 1), pad=((0, 0), (10, 10)), justification="c", key="__STATUS__")
                ],
                [
                    sg.Button("Cancel", pad=((0, 0), (10, 10)), disabled=True, key="__CANCEL__")
                ]
            ])
        ]]

    def show(self):
        self.window = sg.Window(
            title="Backup restore",
            layout=self.layout,
            use_custom_titlebar=True,
            no_titlebar=True,
            titlebar_font="Any 11",
            modal=True,
            keep_on_top=True,
            disable_close=True,
            alpha_channel=0.95,
            element_justification="c"
        )
        self.event_loop()

    def event_loop(self):
        while True:
            event, values = self.window.read(timeout=50)

            if event == sg.WINDOW_CLOSED or self.restorer.action == "__EXIT__":
                break
            elif event == "__CANCEL__":
                # TODO: Implement restore cancel
                pass

            if self.restorer.action == "__SERVER_STOP__":
                self.window["__STATUS__"].update("Stopping server...")
            elif self.restorer.action == "__UPLOAD__":
                self.window["__STATUS__"].update("Uploading files...")
                if ftp is not None:
                    if hasattr(ftp, "up_stream"):
                        self.window["__PROGRESS__"].update((ftp.up_stream.cum_size/ftp.up_stream.total_size) * 100)
            elif self.restorer.action == "__SERVER_START__":
                self.window["__STATUS__"].update("Starting server...")

        self.window.close()


class AboutWindow:
    def __init__(self):
        today = datetime.datetime.today().strftime("%Y")
        self.layout = [
            [
                sg.Text(__title__, pad=((0, 0), (30, 0)), font="Any 13 bold")
            ],
            [
                sg.Text("v " + __version__, font="Any 10")
            ],
            [
                sg.Text("© " + (
                    str(__year__) if str(__year__) == today else str(__year__) + " - " + today
                ) + " " + __author__, pad=((0, 0), (20, 30)))
            ],
            [
                sg.Button("Close")
            ]
        ]

        self.window = sg.Window(
            layout=self.layout,
            title="About " + __abbrev__,
            modal=True,
            keep_on_top=True,
            use_custom_titlebar=True,
            use_ttk_buttons=True,
            use_default_focus=False,
            titlebar_font="Any 10",
            titlebar_icon=DEFAULT_ICON,
            element_justification="c",
            size=(300, 230)
        )

        self.window.read()
        self.window.close()


class ImageViewer:
    def __init__(self, img_path: str, *args, **kwargs):
        self.layout = [
            [
                sg.Image(data=Util.image_preprocessor(img_path, *args, **kwargs))
            ]
        ]

        self.window = sg.Window(
            layout=self.layout,
            title="",
            modal=True,
            keep_on_top=True,
            use_custom_titlebar=True,
            titlebar_icon=DEFAULT_ICON,
        )
        self.window.read()


class DetailsWindow:
    def __init__(self, backup: Backup):
        self.backup = backup

        self.layout = [
            [
                sg.Frame("", border_width=0, pad=((50, 50), (50, 50)), layout=[

                    [
                        sg.Frame("", border_width=0, pad=((0, 30), (0, 0)), layout=[
                            [
                                sg.Text("Name", font="Any 11 bold"),
                                sg.Text(self.backup.name)
                            ],
                            [
                                sg.Text("Size: ", font="Any 11 bold"),
                                sg.Text("{:.2f} MB".format(self.backup.size))
                            ],
                            [
                                sg.Text("Date: ", font="Any 11 bold"),
                                sg.Text(self.backup.date)
                            ]
                        ]),
                        sg.Frame("", border_width=1, layout=[
                            [
                                sg.Image(data=Util.image_preprocessor(self.backup.thumbnail, (400, 150)), key="__IMG__",
                                         enable_events=True, tooltip="Click to enlarge")
                            ]
                        ])
                    ]

                ])
            ],
            [
                sg.Frame("", border_width=0, pad=((0, 0), (0, 15)), layout=[
                    [
                        sg.Button("Restore", font="Any 10 bold", button_color=("#00ff00", sg.theme_button_color()[1]),
                                  key="__RESTORE__"),
                        sg.Button("Open location", key="__OPEN__"),
                        sg.Button("Delete", button_color=("red", sg.theme_button_color()[1]), key="__DELETE__"),
                        sg.Button("Close", pad=((230, 0), (0, 0)), key="__CLOSE__")
                    ]
                ])
            ]
        ]
        self.window = None

    def show(self):
        self.window = sg.Window(
            layout=self.layout,
            title="Backup details",
            modal=True,
            keep_on_top=True,
            use_custom_titlebar=True,
            use_ttk_buttons=True,
            use_default_focus=False,
            titlebar_font="Any 10",
            element_justification="c",
            titlebar_icon=DEFAULT_ICON,
            alpha_channel=0.95
        )

        self.event_loop()

    def event_loop(self):
        while True:
            event, values = self.window.read()

            if event == sg.WINDOW_CLOSED or event == "__CLOSE__":
                break
            elif event == "__OPEN__":
                os.startfile(self.backup.abspath)
            elif event == "__DELETE__":
                if Util.popup(
                        "Delete backup",
                        "\nAre you sure you want to delete this backup?"
                        "\n\nIf you do, IT WILL BE LOST FOREVER (a long time).\n",
                        [
                            sg.Button("Delete backup", button_color=(sg.theme_button_color()[0], "red"),
                                      pad=((50, 50), (0, 20))),
                            sg.Button("Cancel", pad=((0, 0), (0, 20)))
                        ],
                        keep_on_top=True) == "Delete backup":
                    shutil.rmtree(self.backup.abspath, ignore_errors=True)
                    BACKUPS.remove(self.backup)
                    self.window.close()
                    window.redraw("__TAB_BACKUPS__")
                    break
            elif event == "__IMG__":
                ImageViewer(self.backup.thumbnail, (1200, 1000))
            elif event == "__RESTORE__":
                if Util.popup("Restore backup",
                              "Are you sure you want to restore this backup?"
                              "\nThe server will restart during the process.",
                              [sg.Button("Restore"), sg.Button("Cancel")], modal=True, keep_on_top=True) == "Restore":
                    restorer = Util.BackupRestorer(self.backup)
                    threading.Thread(target=lambda: restorer.run(), daemon=True).start()
                    RestoreWindow(restorer).show()

        self.window.close()


class EditorWindow:
    def __init__(self, filename: str):
        self.filename = filename
        self.lines = open(self.filename, "r", encoding="utf-8").readlines()
        self.window = None
        self.changes = False

        self.menu = [["File", ["Save          Ctrl+S", "Close         Alt+F4"]]]

        self.layout = [
            [
                Util.menu_bar(self.menu, pad=(5, 0)),
                sg.Image(data=ICON_WHITE_DOT, tooltip="There are unsaved changes", pad=((00, 8), (7, 0)),
                         visible=False, key="__UNSAVED__")
            ],
            [
                sg.Multiline(size=(150, 30), enable_events=True, background_color="#1f1f1f", text_color="#ffffff",
                             border_width=0, right_click_menu=self.menu[0], key="__TEXT__")
            ],
            [
                sg.Button("Save"), sg.Button("Close")
            ]
        ]

    def show(self):
        self.window = sg.Window(
            title="Editor - " + self.filename,
            layout=self.layout,
            size=(600, 400),
            element_justification="c",
            use_custom_titlebar=True,
            titlebar_icon=ICON_SETTINGS,
            titlebar_text_color="white",
            titlebar_font="Any 10 bold",
            resizable=True,
            enable_close_attempted_event=True,
            alpha_channel=0.95,
            use_ttk_buttons=True,
            use_default_focus=False,
            keep_on_top=True
        ).Finalize()

        for line in self.lines:
            self.window["__TEXT__"].print(line.replace("\n", ""))

        self.window["__TEXT__"].bind("<Control-s>", "SAVE__")

        self.window.TKroot.title("Abdsfdcd")

        self.event_loop()

    def event_loop(self):
        while True:
            event, values = self.window.read()

            if event == sg.WINDOW_CLOSED:
                break
            elif event == "Close" or event == "Close         Alt+F4" or event == sg.WIN_CLOSE_ATTEMPTED_EVENT:
                if self.changes:
                    tmp = Util.popup("Unsaved changes", "Do you want to save the file?",
                                     buttons=[sg.Button("Save"), sg.Button("Don't save"), sg.Button("Cancel")],
                                     keep_on_top=True, modal=True)
                    if tmp == "Save":
                        self.save(values)
                        break
                    elif tmp == "Don't save":
                        break
                else:
                    break
            elif event == "Save" or event == "__TEXT__SAVE__" or event == "Save          Ctrl+S":
                self.save(values)
            elif event == "__TEXT__" and not self.changes:
                self.changes = True

            self.window["__UNSAVED__"].update(visible=self.changes)

        self.window.close()

    def save(self, values):
        with open(self.filename, "w", encoding="utf-8") as file:
            file.write(values["__TEXT__"])
        self.changes = False


class TrayIcon:
    def __init__(self):
        self.menu = [None, ["Start", "---", "Config", "About", "---", "Exit"]]
        self.tray_icon = None
        self.event = None

    def show(self):
        threading.Thread(target=lambda: self._show(), daemon=True).start()

    def _show(self):
        self.tray_icon = sgqt.SystemTray(self.menu, data_base64=DEFAULT_ICON)
        self.event_loop()

    def event_loop(self):
        while True:
            self.event = self.tray_icon.read()


class MainWindow:
    def __init__(self, default_tab: str = None):
        self.default_tab = default_tab
        self.init_check = False
        self.hidden = False
        self.backup_frames = []

        overview_tab_layout = [
            [
                sg.Image(pad=((0, 0), (30, 0)), key="__STATUS_ICON__"),
                sg.Text("loading...", size=(8, 1), justification="c", pad=((0, 0), (30, 0)), font="Any 15 bold",
                        key="__STATUS__")

            ],
            [
                sg.Button("Start", enable_events=True, pad=((0, 0), (30, 0)), key="__START__", ),
                sg.Button("Stop", enable_events=True, pad=((15, 15), (30, 0)), key="__STOP__"),
                sg.Button("Restart", enable_events=True, pad=((0, 0), (30, 0)), key="__RESTART__")
            ],
            [
                sg.HorizontalSeparator(color=_COLOR_LIGHT_GREY, pad=((0, 0), (20, 20)))
            ],
            [
                sg.Frame("", border_width=0, element_justification="c", pad=((0, 0), (20, 20)), layout=[
                    [
                        sg.Frame("", border_width=0, pad=((50, 0), (0, 0)), layout=[
                            [
                                sg.Text("Map: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__MAP__"),
                            ],
                            [
                                sg.Text("IP: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__IP__"),
                            ],
                            [
                                sg.Text("Port: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__PORT__"),
                            ],
                            [
                                sg.Text("Players: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(1, 1), key="__PLAYER_COUNT__"),
                                sg.Text("/"),
                                sg.Text("loading...", size=(1, 1), key="__MAX_PLAYERS__"),
                            ],
                            [
                                sg.Text("Player list: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__PLAYERS__"),
                            ],
                        ]
                                 ),
                        sg.Frame("", border_width=0, layout=[
                            [
                                sg.Text("CPU: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__CPU__"),
                            ],
                            [
                                sg.Text("Memory: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__MEMORY__"),
                            ],
                            [
                                sg.Text("Disk: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__DISK__"),
                            ],
                            [
                                sg.Text("Paid: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__PAID__"),
                            ],
                            [
                                sg.Text("Expiry date: ", font="Any 10 bold"),
                                sg.Text("loading...", size=(15, 1), key="__EXPIRY_DATE__"),
                            ]
                        ]
                                 )
                    ],
                ]
                         )
            ]
        ]

        backups_tab_column_layout = []

        for backup in BACKUPS:
            odd = len(self.backup_frames) % 2 != 0
            backups_tab_column_layout.append([
                sg.Frame("", background_color=_LIST_FOREGROUND_COLOR if odd else None, border_width=0, key=backup.path,
                         layout=[[
                             sg.Text(backup.name, size=(22, 1),
                                     background_color=_LIST_FOREGROUND_COLOR if odd else None, justification="c",
                                     key="__NAME__" + str(BACKUPS.index(backup))),
                             sg.Text("{:.2f} MB".format(backup.size),
                                     background_color=_LIST_FOREGROUND_COLOR if odd else None, size=(10, 1),
                                     key="__SIZE__" + str(BACKUPS.index(backup))),
                             sg.Text(backup.date, size=(16, 1),
                                     background_color=_LIST_FOREGROUND_COLOR if odd else None, pad=((20, 0), (0, 0)),
                                     key="__DATE__" + str(BACKUPS.index(backup))),
                             sg.Button("Details", pad=((40, 35), (5, 5)),
                                       key="__DETAILS__" + str(BACKUPS.index(backup)))
                         ]])
            ])
            self.backup_frames.append(backup.path)

        if not BACKUPS:
            backups_tab_column_layout.append(
                [sg.Text("It's very empty here...", font="Any 11", pad=((230, 0), (100, 0)))]
            )
            backups_tab_column_layout.append([sg.Text("Kinda sus ngl", font="Any 7", pad=((260, 0), (5, 0)))])

        backups_tab_layout = [
            [
                sg.Text("Name", pad=((85, 90), (10, 0)), font="Any 11 bold"),
                sg.Text("Size", pad=((0, 100), (10, 0)), font="Any 11 bold"),
                sg.Text("Date", pad=((0, 95), (10, 0)), font="Any 11 bold"),
                sg.Text("Details", pad=((0, 0), (10, 0)), font="Any 11 bold"),
                sg.Button(
                    image_data=ICON_RELOAD, key="__RELOAD__",
                    button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0,
                    tooltip="Reload", use_ttk_buttons=False, pad=((20, 0), (5, 0)),
                    # Button disabled until implemented
                    # TODO: Actually make reloading work
                    visible=False
                )
            ],
            [
                sg.HorizontalSeparator(color=_COLOR_LIGHT_GREY)
            ],
            [
                sg.Column(backups_tab_column_layout, size=(600, 300), scrollable=len(self.backup_frames) > 9,
                          vertical_scroll_only=True)
            ],
        ]

        auto_backup = Util.get_config().auto_backup

        auto_backup_tab_layout = [
            [
                sg.Text("Auto-backup", font="Any 18 bold", pad=((0, 0), (40, 0)))
            ],
            [
                sg.Image(pad=((80, 0), (47, 0)), data=ICON_SUCCESS, key="__TASK_IMG__"),
                sg.Text(size=(15, 1), font=("Any", 15), pad=((5, 0), (45, 0)), key="__TASK_STATUS__")
            ],
            [
                sg.Text("", font=("Any", 8), pad=((0, 0), (5, 20)), size=(30, 1), justification="c", key="__LAST_RUN__")
            ],
            [
                sg.Text("Backup every"),
                sg.Combo(
                    values=[*range(MIN_AUTO_BACKUP_INTERVAL, MAX_AUTO_BACKUP_INTERVAL + 1)],
                    size=(5, 1),
                    default_value=Util.get_config().interval,
                    disabled=auto_backup,
                    key="__TASK_INTERVAL__"
                ),
                sg.Text("minutes")],
            [
                sg.Button("Enable", pad=((0, 5), (20, 0)), disabled=auto_backup, key="__ENABLE_TASK__"),
                sg.Button("Disable", pad=((5, 0), (20, 0)), disabled=(not auto_backup), key="__DISABLE_TASK__")
            ]
        ]

        menu = [
            [__abbrev__, ["Minimize to tray", "Exit"]],
            ["AutoBackup", ["Enable", "Disable"]],
            ["Server", ["Start", "Stop", "Restart"]],
            ["Settings", ["Config"]],
            ["Help", ["About " + __abbrev__]]
        ]

        self.layout = [
            [
                Util.menu_bar(menu, pad=((5, 0), (5, 0)))
            ],
            [
                sg.Text("loading...", font="Any 30 bold", pad=((0, 0), (20, 0)), key="__TITLE__"),
            ],
            [
                sg.TabGroup([
                    [
                        sg.Tab("Overview", overview_tab_layout, element_justification="c", key="__TAB_OVERVIEW__"),
                        sg.Tab("Auto-backup", auto_backup_tab_layout, element_justification="c",
                               key="__TAB_AUTO_BACKUP__"),
                        sg.Tab("Backups", backups_tab_layout, key="__TAB_BACKUPS__"),
                    ]
                ], key="__TAB_GROUP__")
            ]
        ]

        self.window = None

    def show(self):
        self.window = sg.Window(
            title=__title__,
            layout=self.layout,
            size=(600, 520),
            element_justification="c",
            use_custom_titlebar=True,
            titlebar_icon=DEFAULT_ICON,
            titlebar_text_color="white",
            titlebar_font="Any 10 bold",
            resizable=False,
            enable_close_attempted_event=True,
            alpha_channel=0.95,
            use_ttk_buttons=True,
            use_default_focus=False,
            keep_on_top=True
        ).Finalize()

        print("[MAIN_WINDOW] Window start" + (
            (" (tab=" + repr(self.default_tab) + ")") if self.default_tab is not None else "")
              )
        if self.default_tab is not None:
            self.change_tab(self.default_tab)

        self.event_loop()

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.window.Hide()

    def unhide(self):
        if self.hidden:
            self.hidden = False
            self.window.UnHide()

    def change_tab(self, tab_key: str):
        self.window[tab_key].select()

    def event_loop(self):
        global ftp
        while True:
            event, values = self.window.read(timeout=250)

            # Event handler
            if event is not None and event != sg.TIMEOUT_EVENT:
                if event in values.keys():
                    event = values.get(event)
                print("[EVENT]: " + str(event))

            if event == sg.WINDOW_CLOSED or event == "Exit":
                break
            elif event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                self.hide()
            elif event == "__START__" or event == "Start":
                server.start()
            elif event == "__STOP__" or event == "Stop":
                server.stop()
            elif event == "__RESTART__" or event == "Restart":
                server.restart()
            elif event.startswith("__DETAILS__"):
                index = int(event.split("__DETAILS__")[1])
                DetailsWindow(BACKUPS[index]).show()
            elif (event == "__ENABLE_TASK__" or event == "Enable") and not (scheduler.running or scheduler.running):
                self.start_scheduler()
            elif event == "__DISABLE_TASK__" or event == "Disable":
                self.stop_scheduler()
            elif event == "Config":
                EditorWindow(CONFIG_FILENAME).show()
            elif event == "About " + __abbrev__:
                AboutWindow()
            elif event == "Minimize to tray" and not self.hidden:
                self.hide()
            elif event == "__RELOAD__":
                self.redraw("__TAB_BACKUPS__")
                # A new event loop is now running inside this one, so we must exit to avoid reading destroyed widgets
                break

            # Enable/Disable scheduler on start-up
            if not self.init_check:
                self.init_check = True
                if Util.get_config().auto_backup:
                    self.window["__TASK_STATUS__"].update("Enabled")
                    self.window["__TASK_IMG__"].update(data=ICON_SUCCESS)
                    self.window["__LAST_RUN__"].update(visible=True)
                    self.start_scheduler()
                else:
                    self.window["__TASK_STATUS__"].update("Disabled")
                    self.window["__TASK_IMG__"].update(data=ICON_ERROR)
                    self.window["__LAST_RUN__"].update(visible=False)

            # Only update elements if the window is not hidden
            if status is not None and status and not self.hidden:

                # Update status
                status_ = status.hostname
                if status_ is not None:
                    self.window["__TITLE__"].update(status_)

                status_ = status.is_running
                if status_ is not None:
                    self.window["__STATUS__"].update("Online" if status_ else "Offline")

                    if status_:
                        self.window["__STATUS_ICON__"].update(data=ICON_SUCCESS)
                        self.window["__START__"].update(disabled=True)
                        self.window["__STOP__"].update(disabled=False)
                        self.window["__RESTART__"].update(disabled=False)
                    else:
                        self.window["__STATUS_ICON__"].update(data=ICON_ERROR)
                        self.window["__START__"].update(disabled=False)
                        self.window["__STOP__"].update(disabled=True)
                        self.window["__RESTART__"].update(disabled=True)

                if scheduler.running or scheduler.thread_running:
                    self.window["__TASK_STATUS__"].update("Enabled")
                    self.window["__TASK_IMG__"].update(data=ICON_SUCCESS)

                    if scheduler.thread_running:
                        last = "Downloading backup... "
                        if ftp is not None:
                            if hasattr(ftp, "stream"):
                                if ftp.stream is not None:
                                    last += "(" + ftp.stream.progress + ")"

                    else:
                        last = "Last run: " + datetime.datetime.fromtimestamp(
                            Util.get_config().last_run).strftime("%Y-%m-%d %H:%M:%S")

                    self.window["__LAST_RUN__"].update(last, visible=True)

                else:
                    self.window["__TASK_STATUS__"].update("Disabled")
                    self.window["__TASK_IMG__"].update(data=ICON_ERROR)
                    self.window["__LAST_RUN__"].update(visible=False)

                # Update elements
                self.window["__MAP__"].update(status.map)
                self.window["__IP__"].update(status.ip)
                self.window["__PORT__"].update(status.port)
                self.window["__PLAYER_COUNT__"].update(status.players)
                self.window["__MAX_PLAYERS__"].update(status.slots)
                self.window["__CPU__"].update(str(status.cpu_usage) + " %")
                self.window["__MEMORY__"].update(Util.to_megabytes(status.memory_usage).split(".")[0] + " MB")
                self.window["__DISK__"].update(Util.to_megabytes(status.disk_usage).split(".")[0] + " MB")
                self.window["__PAID__"].update("Yes" if status.is_payed else "No")

                exp_date = status.payed_till
                delta = datetime.datetime.strptime(exp_date, "%Y-%m-%d") - datetime.datetime.today()
                self.window["__EXPIRY_DATE__"].update(exp_date + " (" + str(delta.days) + " days)")

                players = [Player(Util.ObjectifiedDict(player_data)) for player_data in status.players_list]
                self.window["__PLAYERS__"].update(
                    ", ".join([player.name for player in players])
                    if players else "No players")

                # Remove deleted backups
                # for key in [key for key in self.backup_frames if key not in [backup.path for backup in BACKUPS]]:
                # self.window[key].update(visible=False)

            # Tray icon events
            if tray_icon.event is not None and tray_icon.event != sg.TIMEOUT_EVENT:
                tray_event = tray_icon.event
                tray_icon.event = None
                print("[TRAY_EVENT] " + tray_event)

                if (tray_event == sgqt.EVENT_SYSTEM_TRAY_ICON_ACTIVATED
                        or tray_event == sgqt.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                    if self.hidden:
                        self.unhide()
                    else:
                        self.hide()
                elif tray_event == "Exit":
                    break
                elif tray_event == "Config":
                    EditorWindow(CONFIG_FILENAME).show()

        self.window.close()

    def redraw(self, default_tab: str = None):
        print("[MAIN_WINDOW] Redrawing window...")
        self.window.close()
        self.__init__(default_tab)
        self.show()

    def stop_scheduler(self):
        scheduler.stop()
        config = Util.get_config()
        config.auto_backup = False
        Util.save_config(config)
        self.window["__ENABLE_TASK__"].update(disabled=False)
        self.window["__DISABLE_TASK__"].update(disabled=True)
        self.window["__TASK_INTERVAL__"].update(disabled=False)

    def start_scheduler(self):
        scheduler.start()
        config = Util.get_config()
        config.auto_backup = True
        Util.save_config(config)
        self.window["__ENABLE_TASK__"].update(disabled=True)
        self.window["__DISABLE_TASK__"].update(disabled=False)
        self.window["__TASK_INTERVAL__"].update(disabled=True)


if __name__ == '__main__':
    # Redirect stdout and stderr
    if REDIRECT_STDOUT_STDERR_TO_FILE:
        LOG_FILE = open(LOG_FILENAME, "w", encoding="utf-8")
        sys.stdout = Logger(LOG_FILE, Logger.INPUT_STREAM_STDOUT)
        sys.stderr = Logger(LOG_FILE, Logger.INPUT_STREAM_STDERR)
        print("[MAIN] **Both stdout and stderr are redirected to this file. It may be used as a log for debugging "
              "reasons.**\n\n")

    # INIT
    status = Util.ObjectifiedDict()
    ftp = None

    # Create config if not exists
    if not os.path.exists(CONFIG_FILENAME):
        Util.save_config(_DEFAULT_CONFIG)

    try:
        CONFIG = Util.get_config()

        # FAKAHEDA API
        API_BASE_URL = CONFIG.fakaheda.api_url
        SERVER_ID = CONFIG.fakaheda.server_id
        TOKEN = CONFIG.fakaheda.api_token
        JSON_FEED_URL = CONFIG.fakaheda.json_feed_url

        # FTP
        FTP_HOST = CONFIG.ftp.host
        FTP_USER = CONFIG.ftp.user
        FTP_PASSWORD = CONFIG.ftp.password
        FTP_DIR = CONFIG.ftp.dir
        FTP_BLACKLIST = CONFIG.ftp.blacklist

        # PATHS
        BACKUPS_DIR = CONFIG.backups_dir
    except Exception as e:
        print("[CONFIG_LOADER] ERROR: Couldn't load " + CONFIG_FILENAME + ": " + str(e))
        sys.exit(1)
    print(
        "[CONFIG_LOADER] Succesfully loaded " + str(len(CONFIG.keys())) + " properties from " + CONFIG_FILENAME + "\n"
    )

    # Create backups dir if not exists
    if not os.path.exists(BACKUPS_DIR):
        os.makedirs(BACKUPS_DIR)

    # Get list of all backups in backup folder
    print("[BACKUP_LOADER] Loading backups...")
    BACKUPS = []
    for path_ in next(os.walk(BACKUPS_DIR))[1]:
        try:
            backup_ = Backup(path_)
            Image.open(backup_.thumbnail)
        except Exception as e:
            print("[BACKUP_LOADER] ERROR: Could not load backup " + repr(path_) + ": " + str(e))
            continue
        BACKUPS.append(backup_)
    print("[BACKUP_LOADER] Loaded " + str(len(BACKUPS)) + " backups\n")

    # Print out environmental variables
    print("[MAIN] **Start environmental vars**")
    for glob in [(glob, globals().get(glob)) for glob in globals().keys() if (
            glob.isupper()
            and "ICON" not in glob
            and not glob.startswith("_")
    )]:
        print(glob[0] + ": " + repr(glob[1]))
    print("[MAIN] **End environmental vars**\n")

    # MAIN BLOCK
    server = Server(API_BASE_URL, SERVER_ID, TOKEN, JSON_FEED_URL)
    scheduler = Scheduler()
    threading.Thread(target=lambda: update_status(), daemon=True).start()

    # sg.ChangeLookAndFeel("DarkGrey14")
    sg.ChangeLookAndFeel("DarkGrey11")
    tray_icon = TrayIcon()
    tray_icon.show()
    window = MainWindow()
    window.show()

    if REDIRECT_STDOUT_STDERR_TO_FILE:
        print("[MAIN] **Program end**")
