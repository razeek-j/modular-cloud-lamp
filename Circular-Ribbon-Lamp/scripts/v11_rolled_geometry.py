"""Banked ribbon stations for the V11 rolled revision, in millimetres.

Each station is (x, y, centre drop, projected width, edge-to-edge drop,
cross-section camber). Positive crossfall lowers the left edge of the
ordered path. The other ribbons constrain height only near overlaps.
"""
import math

import numpy as np
from mathutils.kdtree import KDTree

PATHS = {
    "A · Wide upper ribbon": [
        (-82,-55,44,132,-30,8),(-215,-110,48,147,-54,13),
        (-382,-126,61,161,54,12),(-488,-195,58,185,110,19),
        (-417,-323,48,219,86,22),(-250,-409,55,230,-95,14),
        (-92,-334,58,185,-82,20),(104,-259,46,153,-25,9),
        (272,-329,58,190,66,15),(426,-319,60,209,104,21),
        (483,-240,68,193,-102,17),(407,-159,60,158,-74,14),
        (238,-128,49,131,22,12),(83,-84,45,115,-36,8),(13,-59,49,119,-40,8),
    ],
    "B · Middle crossing ribbon": [
        (-481,147,94,196,-88,18),(-536,43,88,207,-118,25),
        (-467,-56,85,189,93,21),(-319,-71,80,166,39,12),
        (-175,-33,95,162,-47,13),(-27,-33,89,129,-51,9),
        (137,-100,88,179,62,13),(299,-150,81,221,102,20),
        (449,-105,91,235,116,24),(521,2,94,209,142,26),
        (475,128,104,200,127,25),(377,199,102,182,78,19),
        (278,176,91,149,30,13),(204,96,79,133,-46,10),
        (91,104,83,119,-56,12),(-45,110,91,116,-42,12),
        (-178,145,91,161,57,15),(-333,203,92,178,99,18),
    ],
    "C · Lower return ribbon": [
        (-408,284,112,181,128,23),(-420,194,111,174,109,21),
        (-344,132,113,188,-97,19),(-184,105,121,193,-72,17),
        (-62,111,122,155,31,11),(81,166,123,166,48,14),
        (192,194,128,169,-88,20),(303,193,117,183,-100,19),
        (395,277,121,181,105,23),(359,357,128,171,122,21),
        (223,403,124,187,-95,24),(83,417,126,202,-110,23),
        (-59,469,125,211,108,22),(-198,435,114,200,108,19),
        (-302,375,114,170,-72,16),
    ],
}


def smoothstep(value):
    x = np.clip(value, 0.0, 1.0)
    return x*x*(3-2*x)


def rolled_grids(catmull, smooth, unit):
    # Dense XY samples make the nearest-neighbor test conservative around
    # crossing edges, while allowing the isolated outer rolls to bank freely.
    raw = {}
    for label, stations in PATHS.items():
        count = len(stations)*21
        source = np.array(stations, dtype=float)
        p = smooth(np.array([catmull(source, t, True)
                             for t in np.linspace(0, len(stations), count, endpoint=False)])*.001, 4.1)
        xy = p[:, :2]
        velocity = (np.roll(xy, -1, axis=0)-np.roll(xy, 1, axis=0))/2
        tangent = unit(velocity)
        cross = np.column_stack((-tangent[:, 1], tangent[:, 0]))
        curvature = smooth(np.sum((np.roll(tangent, -1, axis=0)-np.roll(tangent, 1, axis=0))*cross,
                                  axis=1)/(2*np.linalg.norm(velocity, axis=1)), 5.0)
        half = p[:, 3]*.5
        def inner_width(sign):
            scale = np.maximum(sign*curvature, 0)*half/.54
            return smooth(half/np.power(1+scale**4, .25), 4.2)
        u = np.linspace(0, 1, 113)
        left, right = inner_width(1), inner_width(-1)
        width = left+right
        offset = left[:, None]*u-right[:, None]*(1-u)
        camber = p[:, 5, None]*np.sin(np.pi*u)**1.45
        depth = p[:, 2, None]+p[:, 4, None]*(u-.5)+camber

        # Locally curve the outside edge past vertical. The face blends
        # into the curl with a continuous tangent at the starting station.
        # A rolled return gives a pocket between the lip and facing sheet.
        returns = {
            "A": [],
            "B": [(1.1, .77, .34, 1.88, 1), (9.5, .94, .35, 1.84, -1)],
            "C": [(11.75, 1.22, .38, 1.85, -1)],
        }
        along=np.linspace(0,len(stations),count,endpoint=False)
        for centre,reach,fraction,angle,down in returns[label[0]]:
            delta=(along-centre+len(stations)/2)%len(stations)-len(stations)/2
            weight=np.exp(-.5*(delta/reach)**2)[:,None]
            t=np.maximum((fraction-u)/fraction,0)
            arc=width[:,None]*fraction/angle
            offset += weight*arc*(angle*t-np.sin(angle*t))
            depth += down*weight*arc*(1-np.cos(angle*t))
        grid_xy = xy[:, None, :]+cross[:, None, :]*offset[:, :, None]
        raw[label[0]] = grid_xy, depth

    coverage = {}
    for band, (xy, _) in raw.items():
        points = xy.reshape(-1, 2)
        search = KDTree(len(points))
        for i, (x, y) in enumerate(points):
            search.insert((x, y, 0), i)
        search.balance()
        coverage[band] = search

    grids = {}
    for band, (xy, nominal) in raw.items():
        shape = xy.shape[:2]
        lo = np.full(shape, .019)
        hi = np.full(shape, .158)
        weights = {}
        for other, search in coverage.items():
            if other == band:
                continue
            distance = np.array([search.find((x, y, 0))[2]
                                 for x, y in xy.reshape(-1, 2)]).reshape(shape)
            weights[other] = 1-smoothstep((distance-.016)/.067)

        # Only apply lane separation within projected overlaps. The soft
        # falloff allows the bands to occupy the same heights elsewhere.
        near_centre = 1-smoothstep((np.linalg.norm(xy, axis=2)-.104)/.040)
        lo = np.maximum(lo, .019+.030*near_centre)
        if band == "A":
            hi = np.minimum(hi, .158-.090*weights["B"])
            hi = np.minimum(hi, .158-.051*weights["C"])
        elif band == "B":
            lo = np.maximum(lo, .019+.053*weights["A"])
            hi = np.minimum(hi, .158-.047*weights["C"])
        else:
            lo = np.maximum(lo, .019+.092*weights["A"])
            lo = np.maximum(lo, .019+.096*weights["B"])

        midpoint, travel = (lo+hi)*.5, (hi-lo)*.5
        depth = midpoint+travel*np.tanh((nominal-midpoint)/travel)
        grid = np.dstack((xy, -depth))
        tangent = (np.roll(grid, -1, axis=0)-np.roll(grid, 1, axis=0))/2
        normals = unit(np.cross(tangent, np.gradient(grid, axis=1)))
        u = np.linspace(0, 1, shape[1])
        ripple = .00034*np.cos(2*math.pi*22*u)*np.sin(math.pi*u)**.55
        grid += normals*ripple[None, :, None]
        grids[band] = grid, normals
    return grids
