#!/usr/bin/env python3
"""Reproducible screening calculations for the reference-led ribbon plan.

All path lengths, widths, print allowances, and load factors are explicit
design assumptions. This script does not reconstruct a unique 3D surface or
validate a printable part.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


G = 9.81
PETG_DENSITY_G_CM3 = 1.27
EFFECTIVE_PETG_E_MPA = 1500.0

RIBBONS = [
    {"id": "A", "name": "upper-left sweep", "run_chord_px": [(345, 361), (617, 379)], "path_m": 1.9, "mean_width_mm": 170, "turn_width_mm": 170, "radius_mm": 120, "turn_deg": 150, "ramp_mm": 35},
    {"id": "B", "name": "front-right fold", "run_chord_px": [(617, 412), (897, 457)], "path_m": 1.8, "mean_width_mm": 150, "turn_width_mm": 180, "radius_mm": 125, "turn_deg": 165, "ramp_mm": 35},
    {"id": "C", "name": "lower sweep", "run_chord_px": [(259, 770), (580, 565)], "path_m": 2.0, "mean_width_mm": 170, "turn_width_mm": 170, "radius_mm": 120, "turn_deg": 150, "ramp_mm": 35},
]

IMAGE_BOUNDS_PX = {"x_min": 41, "x_max": 1208, "y_min": 196, "y_max": 1065}
IMAGE_HUB_PX = (648, 316)
IMAGE_FOLD_MARKERS_PX = {"A": (128, 521), "B": (862, 809), "C": (213, 914)}
TARGET_MAX_SPAN_MM = 1200.0
FOOTPRINT_TARGET_MM = [1200.0, 1050.0]

SKIN_THICKNESS_MM = 1.6
RETURN_DEPTH_MM = 12.0
RETURN_THICKNESS_MM = 1.6
PANEL_NET_ADVANCE_MM = [240.0, 260.0]
PANEL_LAP_MM = 20.0
PRINTER_VOLUME_MM = [350.0, 350.0, 350.0]
WORKING_BOX_MM = [320.0, 320.0, 320.0]

FULL_ASSEMBLY_BUDGET_KG = 4.0
SCREEN_LOAD_MULTIPLIER = 5.0
TOTAL_PATH_M = sum(r["path_m"] for r in RIBBONS)


def clothoid_turn(radius_mm: float, turn_deg: float, ramp_mm: float) -> dict[str, float]:
    theta = math.radians(turn_deg)
    ramp_heading = ramp_mm / radius_mm
    core_angle = theta - ramp_heading
    return {
        "ramp_total_heading_deg": math.degrees(ramp_heading),
        "core_angle_deg": math.degrees(core_angle),
        "core_arc_mm": radius_mm * core_angle,
        "full_turn_mm": radius_mm * theta + ramp_mm,
    }


def section_properties(width_mm: float) -> dict[str, float]:
    """Open U-section, face at z=0..t, webs from z=t to z=t+h."""
    t = RETURN_THICKNESS_MM
    h = RETURN_DEPTH_MM
    face_area = width_mm * t
    web_area = t * h
    face_z = t / 2
    web_z = t + h / 2
    total_area = face_area + 2 * web_area
    centroid_z = (face_area * face_z + 2 * web_area * web_z) / total_area
    face_i = width_mm * t**3 / 12 + face_area * (face_z - centroid_z) ** 2
    web_i = t * h**3 / 12 + web_area * (web_z - centroid_z) ** 2
    i_mm4 = face_i + 2 * web_i
    mass_kg_per_m = total_area * PETG_DENSITY_G_CM3 / 1000
    return {
        "area_mm2": total_area,
        "centroid_from_outer_face_mm": centroid_z,
        "i_about_width_axis_mm4": i_mm4,
        "linear_mass_kg_per_m": mass_kg_per_m,
    }


scale_mm_per_px = TARGET_MAX_SPAN_MM / (IMAGE_BOUNDS_PX["x_max"] - IMAGE_BOUNDS_PX["x_min"])
image_center_px = (
    (IMAGE_BOUNDS_PX["x_min"] + IMAGE_BOUNDS_PX["x_max"]) / 2,
    (IMAGE_BOUNDS_PX["y_min"] + IMAGE_BOUNDS_PX["y_max"]) / 2,
)

def project_point(point_px: tuple[float, float]) -> tuple[float, float]:
    """Map pixels to mm about the outline center, with positive Y upward."""
    return (
        (point_px[0] - image_center_px[0]) * scale_mm_per_px,
        (image_center_px[1] - point_px[1]) * scale_mm_per_px,
    )

geometry = []
for ribbon in RIBBONS:
    (x1, y1), (x2, y2) = ribbon["run_chord_px"]
    dx = (x2 - x1) * scale_mm_per_px
    dy_up = -(y2 - y1) * scale_mm_per_px
    chord_mm = math.hypot(dx, dy_up)
    turn = clothoid_turn(ribbon["radius_mm"], ribbon["turn_deg"], ribbon["ramp_mm"])
    geometry.append({
        "id": ribbon["id"],
        "name": ribbon["name"],
        "projected_run_chord_mm": chord_mm,
        "projected_heading_deg_x_right_y_up": math.degrees(math.atan2(dy_up, dx)),
        "candidate_mean_width_mm": ribbon["mean_width_mm"],
        "candidate_turn_width_mm": ribbon["turn_width_mm"],
        "centerline_radius_mm": ribbon["radius_mm"],
        "inner_edge_radius_mm": ribbon["radius_mm"] - ribbon["turn_width_mm"] / 2,
        "outer_edge_radius_mm": ribbon["radius_mm"] + ribbon["turn_width_mm"] / 2,
        "turn_deg": ribbon["turn_deg"],
        **turn,
        "candidate_total_path_m": ribbon["path_m"],
        "residual_for_hidden_return_and_approach_m": ribbon["path_m"] - chord_mm / 1000 - turn["full_turn_mm"] / 1000,
    })

areas_m2 = [r["path_m"] * r["mean_width_mm"] / 1000 for r in RIBBONS]
area_total_m2 = sum(areas_m2)
skin_volume_cm3 = area_total_m2 * 1_000_000 * SKIN_THICKNESS_MM / 1000
skin_mass_kg = skin_volume_cm3 * PETG_DENSITY_G_CM3 / 1000
return_volume_cm3 = (
    2 * RETURN_DEPTH_MM * RETURN_THICKNESS_MM * TOTAL_PATH_M * 1000 / 1000
)
return_mass_kg = return_volume_cm3 * PETG_DENSITY_G_CM3 / 1000

# Three open root-to-root ribbons have N-1 panel joints each.
lap_joint_count_range = [20, 22]
lap_width_mm_range = [140, 180]
lap_volume_cm3_range = [
    n * PANEL_LAP_MM * w * SKIN_THICKNESS_MM / 1000
    for n, w in [(lap_joint_count_range[0], lap_width_mm_range[0]), (lap_joint_count_range[1], lap_width_mm_range[1])]
]
lap_mass_kg_range = [v * PETG_DENSITY_G_CM3 / 1000 for v in lap_volume_cm3_range]

total_mass_kg_range = [2.70, 3.17]  # skin, two returns, seam/capture allowance, light hardware, hub; driver excluded
total_mass_with_driver_kg_range = [2.80, 3.42]
static_load_N_range = [m * G for m in total_mass_kg_range]
static_load_design_envelope_N = FULL_ASSEMBLY_BUDGET_KG * G
screen_load_N = static_load_design_envelope_N * SCREEN_LOAD_MULTIPLIER
per_root_equal_share_N = screen_load_N / 6
line_load_N_per_m = static_load_design_envelope_N / TOTAL_PATH_M

beam = []
for width in (170.0, 150.0):
    section = section_properties(width)
    spans = {}
    for span_mm in (400.0, 450.0, 500.0, 600.0):
        q_n_per_mm = line_load_N_per_m / 1000
        delta_mm = 5 * q_n_per_mm * span_mm**4 / (
            384 * EFFECTIVE_PETG_E_MPA * section["i_about_width_axis_mm4"]
        )
        spans[str(int(span_mm))] = {
            "static_deflection_mm": delta_mm,
            "five_x_screen_deflection_mm": delta_mm * SCREEN_LOAD_MULTIPLIER,
        }
    beam.append({"face_width_mm": width, **section, "span_deflection": spans})

panel_counts = {}
for ribbon in RIBBONS:
    panel_counts[ribbon["id"]] = {
        "path_m": ribbon["path_m"],
        "pieces_at_260mm_net_advance": math.ceil(ribbon["path_m"] * 1000 / 260),
        "pieces_at_240mm_net_advance": math.ceil(ribbon["path_m"] * 1000 / 240),
    }

total_panel_count_range = [
    sum(x["pieces_at_260mm_net_advance"] for x in panel_counts.values()),
    sum(x["pieces_at_240mm_net_advance"] for x in panel_counts.values()),
]

result = {
    "status": "planning estimate; no unique 3D solution or strength validation",
    "reference_scale": {
        "image_bounds_px": IMAGE_BOUNDS_PX,
        "scale_mm_per_px": scale_mm_per_px,
        "projected_outline_mm": [TARGET_MAX_SPAN_MM, (IMAGE_BOUNDS_PX["y_max"] - IMAGE_BOUNDS_PX["y_min"]) * scale_mm_per_px],
        "candidate_rounder_footprint_mm": FOOTPRINT_TARGET_MM,
        "short_axis_extension_mm_total": FOOTPRINT_TARGET_MM[1] - (IMAGE_BOUNDS_PX["y_max"] - IMAGE_BOUNDS_PX["y_min"]) * scale_mm_per_px,
        "short_axis_extension_if_centered_mm_each_end": (FOOTPRINT_TARGET_MM[1] - (IMAGE_BOUNDS_PX["y_max"] - IMAGE_BOUNDS_PX["y_min"]) * scale_mm_per_px) / 2,
        "hub_projection_mm_x_right_y_up": project_point(IMAGE_HUB_PX),
        "fold_marker_projection_mm_x_right_y_up": {k: project_point(v) for k, v in IMAGE_FOLD_MARKERS_PX.items()},
        "visible_runs": geometry,
    },
    "mass": {
        "nominal_petg_density_g_cm3": PETG_DENSITY_G_CM3,
        "mean_width_path_area_m2_per_ribbon": dict(zip((r["id"] for r in RIBBONS), areas_m2)),
        "total_surface_area_m2": area_total_m2,
        "skin_thickness_mm": SKIN_THICKNESS_MM,
        "skin_volume_cm3": skin_volume_cm3,
        "skin_mass_kg": skin_mass_kg,
        "return_web_geometry": {"count_per_path": 2, "depth_mm": RETURN_DEPTH_MM, "thickness_mm": RETURN_THICKNESS_MM, "total_path_m": TOTAL_PATH_M},
        "return_web_volume_cm3": return_volume_cm3,
        "return_web_mass_kg": return_mass_kg,
        "seam_lap_only_volume_cm3_range": lap_volume_cm3_range,
        "seam_lap_only_mass_kg_range": lap_mass_kg_range,
        "candidate_assembled_mass_kg_excluding_driver": total_mass_kg_range,
        "candidate_assembled_mass_kg_with_driver": total_mass_with_driver_kg_range,
        "4kg_design_mass_envelope": FULL_ASSEMBLY_BUDGET_KG,
    },
    "support_screen": {
        "g_m_s2": G,
        "static_design_envelope_N": static_load_design_envelope_N,
        "screen_multiplier": SCREEN_LOAD_MULTIPLIER,
        "whole_lamp_screen_load_N": screen_load_N,
        "six_root_equal_share_N_at_screen_load": per_root_equal_share_N,
        "individual_root_bench_target_N": 300.0,
        "total_centerline_length_m": TOTAL_PATH_M,
        "uniform_full_mass_line_load_N_m": line_load_N_per_m,
        "assumed_effective_petg_modulus_MPa": EFFECTIVE_PETG_E_MPA,
        "open_u_section_models": beam,
        "eccentric_static_moment_Nm_at_4kg": {str(mm): FULL_ASSEMBLY_BUDGET_KG * G * mm / 1000 for mm in (10, 40)},
    },
    "print_plan": {
        "nominal_printer_volume_mm": PRINTER_VOLUME_MM,
        "planning_working_box_mm": WORKING_BOX_MM,
        "panel_net_advance_mm": PANEL_NET_ADVANCE_MM,
        "integral_lap_mm": PANEL_LAP_MM,
        "panel_count_range_per_ribbon": panel_counts,
        "total_panel_count_range": total_panel_count_range,
        "panel_to_panel_lap_count_range_for_three_open_paths": [total_panel_count_range[0] - len(RIBBONS), total_panel_count_range[1] - len(RIBBONS)],
    },
}

print(json.dumps(result, indent=2))
