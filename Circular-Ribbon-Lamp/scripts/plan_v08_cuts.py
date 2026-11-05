"""Draft a bed-size cut map in the V07 context scene using the original ripple grids."""
import json
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def plan_cuts(scene, directory):
    root = Path(__file__).resolve().parents[1]
    attachments = json.loads((root / "checks/v07-report.json").read_text())["attachments"]
    bands = sorted((ob for ob in scene.objects if ob.type == 'MESH' and
                    ob.name.startswith(tuple(f"W{i:02d} " for i in range(1, 7)))),
                   key=lambda ob: ob.name)
    assert len(bands) == 6
    guide = bpy.data.collections.new("V08 · Draft cut lines (viewport only)")
    scene.collection.children.link(guide)
    guide.hide_render = True
    paint = bpy.data.materials.new("V08 · Cut line marker")
    paint.diffuse_color = (.76, .18, .05, 1)

    grids = {}
    trees = {}
    for band in bands:
        index = band["shape_index"]
        rows, columns = (600, 193) if index < 3 else (241, 97)
        coords = np.empty(len(band.data.vertices) * 3, dtype=np.float32)
        band.data.vertices.foreach_get("co", coords)
        matrix = np.array(band.matrix_world)
        grid = coords.reshape(rows, columns, 3) @ matrix[:3, :3].T + matrix[:3, 3]
        grids[band.name] = grid
        band.data.calc_loop_triangles()
        trees[band.name] = BVHTree.FromPolygons(
            grid.reshape(-1, 3).tolist(),
            [tuple(tri.vertices) for tri in band.data.loop_triangles], all_triangles=True)

    direction = Vector((0, 0, 1))
    schedule = []
    for band in bands:
        grid = grids[band.name]
        count, columns, _ = grid.shape
        closed = band["shape_index"] < 3
        centre = grid[:, columns // 2]
        candidates = list(range(0, count - 1, 8))
        sample_cols = np.linspace(10, columns - 11, 9, dtype=int)
        pads = [np.asarray(pad["location_mm"]) / 1000 for pad in attachments
                if pad["band"] == band.name]
        cut_cost, cover = {}, {}
        for row in candidates:
            points = grid[row, sample_cols]
            cover[row] = sum(any(tree.ray_cast(Vector(pt) - direction * .19, direction, .184)[0]
                                 is not None for name, tree in trees.items() if name != band.name)
                             for pt in points)
            near_pad = any(np.min(np.linalg.norm(grid[row] - pad, axis=1)) < .040 for pad in pads)
            cut_cost[row] = (len(points) - cover[row]) * .055 + (1.0 if near_pad else 0)
        if closed:
            # Put the wrap seam at a screened position, then solve the unwrapped path.
            anchor = min(candidates, key=lambda row: cut_cost[row])
            nodes = sorted(row if row >= anchor else row + count for row in candidates)
            nodes.append(anchor + count)
            work = np.concatenate((grid, grid))
        else:
            nodes = [*candidates, count - 1]
            work = grid
        centreline = work[:, columns // 2]
        distances = np.r_[0, np.cumsum(np.linalg.norm(np.diff(centreline, axis=0), axis=1))]
        best = {nodes[0]: (0, [])}
        for i, first in enumerate(nodes[:-1]):
            if first not in best:
                continue
            axis_z = centreline[first + 1] - centreline[max(0, first - 1)]
            axis_z /= np.linalg.norm(axis_z)
            axis_x = work[first, -1] - work[first, 0]
            axis_x -= np.dot(axis_x, axis_z) * axis_z
            axis_x /= np.linalg.norm(axis_x)
            axis_y = np.cross(axis_z, axis_x)
            projected = work[first:min(first + 130, len(work))] @ np.stack((axis_x, axis_y, axis_z), axis=1)
            for last in nodes[i+1:]:
                if last - first >= len(projected) or distances[last] - distances[first] > .365:
                    break
                if distances[last] - distances[first] < .066:
                    continue
                # Full grid bounds in a seam-edge-up trial orientation, with 2 mm wall allowance.
                size = np.ptp(projected[:last-first+1].reshape(-1, 3), axis=0) * 1000 + 2
                if max(size) > 285:
                    continue
                seam_cost = 0 if last == nodes[-1] else cut_cost[last % count]
                cost = best[first][0] + 1 + seam_cost
                if last not in best or cost < best[last][0]:
                    piece = dict(start_row=first % count, end_row=last % count,
                                 extents_mm=[round(float(value), 1) for value in size])
                    best[last] = (cost, [*best[first][1], piece])

        pieces = best[nodes[-1]][1]
        seams = [piece["end_row"] for piece in pieces[:-1]]
        if closed:
            seams.append(nodes[0])
        for seq, row in enumerate(seams, start=1):
            name = f"{band.name[:3]} · draft cut {seq:02d} (row {row})"
            curve = bpy.data.curves.new(name, 'CURVE')
            curve.dimensions = '3D'
            curve.bevel_depth = .0011
            curve.bevel_resolution = 2
            spline = curve.splines.new('POLY')
            coords = grid[row, ::2]
            spline.points.add(len(coords) - 1)
            for p, q in zip(spline.points, coords):
                p.co = (*q, 1)
            curve.materials.append(paint)
            guide.objects.link(bpy.data.objects.new(name, curve))

        schedule.append(dict(band=band.name, pieces=pieces, seams=[
            dict(row=row, screened_samples_directly_below=cover[row], total_samples=9)
            for row in seams]))

    scene.view_layers[0].layer_collection.children[guide.name].hide_viewport = True
    report = dict(part_count=sum(len(band["pieces"]) for band in schedule),
                  nominal_envelope_cap_mm=285, bands=schedule,
                  scope="Planning bounds in one trial orientation. Vertical screening by another skin is sampled; room angles, final joints and slicing remain open.")
    (directory / "draft-cut-map.json").write_text(json.dumps(report, indent=2) + '\n')
    return report
