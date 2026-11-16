"""Reproduce the discarded radial clearance study in millimetres.

Run with Blender's Python for NumPy and BVHTree. This script uses numerical
arrays only and does not create or modify a Blender scene.
"""

from itertools import combinations
import json
import math
from pathlib import Path

from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np


OUT = Path(__file__).resolve().parent
SEAT_X = 45.0
ROOT_WIDTH = 44.0
FULL_WIDTH_X = 76.0
HALF_SKIN = .8

# Name, direction, reach, width, radius, ease, bend plane, root drop, lateral offset.
FOLDS = (
    ('Right', 5, 600, 165, 52, 24, 72, 32, -28),
    ('Upper left', 158, 588, 152, 48, 22, 74, 42, 30),
    ('Lower', 258, 570, 138, 44, 20, 70, 49, -7),
)


def eased_arc(radius, ramp, turn):
    """Integrate the unit tangent with linear curvature ramps at the ends."""
    length = radius * turn + ramp
    n = 8192
    step = length / n
    s = (np.arange(n) + .5) * step
    heading = np.where(s < ramp, s**2 / (2 * radius * ramp), (s - ramp / 2) / radius)
    heading = np.where(s > length - ramp, turn - (length - s)**2 / (2 * radius * ramp), heading)
    increments = np.column_stack((np.cos(heading), np.sin(heading))) * step
    return np.vstack((np.zeros(2), increments.cumsum(axis=0)))


def solve_fold(spec, spacing):
    name, azimuth, reach, width, radius, ramp, incline, top, lateral_offset = spec

    def endpoints(turn):
        arc = eased_arc(radius, ramp, turn)
        bend_x = reach - arc[:, 0].max()
        exit_point = arc[-1] + [bend_x, 0]
        return_length = (SEAT_X - exit_point[0]) / math.cos(turn)
        seat_h = exit_point[1] + return_length * math.sin(turn)
        return arc, bend_x, exit_point, return_length, seat_h

    if name == 'Right':
        turn = math.radians(190)
    else:
        # Solve the turn from a 17 mm gap at the two seats in the bend plane.
        low, high = math.pi, math.radians(205)
        for _ in range(32):
            middle = (low + high) / 2
            if endpoints(middle)[-1] > 17:
                low = middle
            else:
                high = middle
        turn = (low + high) / 2
    arc, bend_x, exit_point, return_length, seat_h = endpoints(turn)
    bend_length = radius * turn + ramp
    start = np.array([SEAT_X, 0])
    end = np.array([SEAT_X, seat_h])
    outbound_length = bend_x - SEAT_X

    def straight(first, last, length):
        return np.linspace(first, last, math.ceil(length / spacing) + 1)

    outward = straight(start, [bend_x, 0], outbound_length)
    samples = np.linspace(0, len(arc) - 1, math.ceil(bend_length / spacing) + 1)
    bend = np.column_stack([np.interp(samples, np.arange(len(arc)), axis) for axis in arc.T])
    bend += [bend_x, 0]
    returning = straight(exit_point, end, return_length)
    path = np.vstack((outward[:-1], bend[:-1], returning))

    az = math.radians(azimuth)
    tilt = math.radians(incline)
    along = np.array([math.cos(az), math.sin(az), 0])
    sideways = np.array([-math.sin(az), math.cos(az), 0])
    down = np.array([0, 0, 1])
    across_bend = math.cos(tilt) * sideways + math.sin(tilt) * down
    across_width = -math.sin(tilt) * sideways + math.cos(tilt) * down
    centres = path[:, :1] * along + path[:, 1:] * across_bend + top * down + lateral_offset * sideways

    t = np.clip((path[:, 0] - SEAT_X) / (FULL_WIDTH_X - SEAT_X), 0, 1)
    widths = ROOT_WIDTH + (width - ROOT_WIDTH) * t**3 * (10 + t * (-15 + 6 * t))
    tangents = np.gradient(centres, axis=0)
    normals = np.cross(tangents, across_width)
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    columns = math.ceil(width / spacing) + 1
    midsheet = centres[:, None] + widths[:, None, None] * np.linspace(-.5, .5, columns)[None, :, None] * across_width
    vertices = np.stack((midsheet + HALF_SKIN * normals[:, None], midsheet - HALF_SKIN * normals[:, None]))
    outline = np.vstack((midsheet[:, 0], midsheet[::-1, -1]))
    seats = centres[[0, -1]]
    seat_edges = midsheet[[0, -1]][:, [0, -1]]
    first_bend_row = len(outward) - 1
    last_bend_row = first_bend_row + len(bend) - 1
    summary = {
        'azimuth_deg': azimuth, 'reach_along_axis_mm': reach, 'width_mm': width,
        'lateral_offset_mm': lateral_offset,
        'bend_plane_deg': incline, 'core_radius_mm': radius, 'ramp_each_mm': ramp,
        'turn_deg': round(math.degrees(turn), 3), 'bend_start_x_mm': round(bend_x, 2),
        'outward_mm': round(outbound_length, 2), 'bend_mm': round(bend_length, 2),
        'return_mm': round(return_length, 2), 'path_mm': round(outbound_length + bend_length + return_length, 2),
        'bend_entry_xyz_mm': centres[first_bend_row].round(2).tolist(),
        'bend_exit_xyz_mm': centres[last_bend_row].round(2).tolist(),
        'seat_centres_xyz_mm': seats.round(2).tolist(),
        'seat_edge_max_radius_mm': round(float(np.linalg.norm(seat_edges[:, :, :2], axis=-1).max()), 2),
        'seat_edge_max_drop_mm': round(float(seat_edges[..., 2].max()) + HALF_SKIN, 2),
        'lowest_edge_mm': round(float(vertices[..., 2].max()), 2),
    }
    return name, summary, vertices, centres, outline


def shell_tree(grid):
    _, rows, cols, _ = grid.shape
    layer_size = rows * cols
    faces = []
    for layer in range(2):
        offset = layer * layer_size
        for row in range(rows - 1):
            for column in range(cols - 1):
                i = offset + row * cols + column
                faces.extend(((i, i + cols, i + 1), (i + 1, i + cols, i + cols + 1)))
    boundary = [*range(cols), *range(2 * cols - 1, layer_size, cols),
                *range(layer_size - 2, layer_size - cols - 1, -1),
                *range(layer_size - 2 * cols, 0, -cols)]
    for a, b in zip(boundary, boundary[1:] + boundary[:1]):
        faces.extend(((a, b, a + layer_size), (b, b + layer_size, a + layer_size)))
    return BVHTree.FromPolygons(grid.reshape(-1, 3), faces, all_triangles=True)


def calculate(spacing):
    folds = [solve_fold(spec, spacing) for spec in FOLDS]
    trees = [shell_tree(fold[2]) for fold in folds]
    comparisons = {}
    for a, b in combinations(range(len(folds)), 2):
        name = f'{folds[a][0]} / {folds[b][0]}'
        hits = trees[a].overlap(trees[b])
        smallest = min(trees[b].find_nearest(Vector(v))[3] for v in folds[a][2].reshape(-1, 3))
        smallest = min(smallest, min(trees[a].find_nearest(Vector(v))[3] for v in folds[b][2].reshape(-1, 3)))
        comparisons[name] = {'intersecting_triangle_pairs': len(hits), 'sampled_gap_mm': round(smallest, 2)}
    all_vertices = np.concatenate([fold[2].reshape(-1, 3) for fold in folds])
    return folds, {
        'root_width_mm': ROOT_WIDTH, 'full_width_at_x_mm': FULL_WIDTH_X,
        'nominal_skin_mm': HALF_SKIN * 2, 'nominal_sampling_interval_mm': spacing,
        'folds': {fold[0]: fold[1] for fold in folds}, 'pair_checks': comparisons,
        'width_length_skin_height_mm': np.ptp(all_vertices, axis=0).round(2).tolist(),
        'max_drop_from_mounting_datum_mm': round(float(all_vertices[:, 2].max()), 2),
    }


if __name__ == '__main__':
    folds, summary = calculate(2.0)
    OUT.mkdir(exist_ok=True)
    (OUT / 'Geometry.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2), flush=True)
