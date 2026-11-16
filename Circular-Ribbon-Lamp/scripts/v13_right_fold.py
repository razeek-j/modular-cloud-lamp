"""Shape the right ribbon from a centre path, width, and bank angle."""

import math

import numpy as np


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * t * (10 + t * (-15 + 6 * t))


def direction(vector):
    return vector / np.linalg.norm(vector)


def connect(start, end, tangent_start, tangent_end, samples):
    """Blend two spans with matching tangent directions at their join."""
    handle = np.linalg.norm(end - start) / 3
    control1 = start + direction(tangent_start) * handle
    control2 = end - direction(tangent_end) * handle
    t = np.linspace(0, 1, samples)[:, None]
    u = 1 - t
    return u**3 * start + 3 * u**2 * t * control1 + 3 * u * t**2 * control2 + t**3 * end


def eased_turn(start, end_height, heading, angle, radius, easing, samples):
    """Integrate curvature ramps on both sides of a constant-radius plan arc."""
    length = radius * angle + easing
    distance = np.linspace(0, length, 2049)
    entry = np.minimum(distance / easing, 1)
    exit = np.maximum((distance - length + easing) / easing, 0)
    entry_integral = entry**3 - entry**4 / 2
    exit_integral = exit**3 - exit**4 / 2
    heading = heading + (
        easing * entry_integral + np.maximum(distance - easing, 0) - easing * exit_integral
    ) / radius
    tangents = np.column_stack((np.cos(heading), np.sin(heading)))
    xy = np.vstack((np.zeros(2), np.cumsum((tangents[1:] + tangents[:-1]) / 2, axis=0)))
    xy *= distance[1]
    xy += start[:2]
    fraction = distance / length
    height = start[2] + (end_height - start[2]) * smoothstep(fraction)
    height -= .021 * np.sin(np.pi * fraction) ** 2
    sample_distance = np.linspace(0, length, samples)
    return np.column_stack([np.interp(sample_distance, distance, col) for col in (*xy.T, height)])


def right_fold(rails, camber):
    """Replace the visible turn and gradually hand the section back to V12."""
    points_per_station = 16
    centre = (rails[:, :3] + rails[:, 3:]) / 2
    centre[:, 2] -= camber
    original_across = rails[:, 3:] - rails[:, :3]
    width = np.linalg.norm(original_across, axis=1)
    bank = np.arctan2(original_across[:, 2], np.linalg.norm(original_across[:, :2], axis=1))

    # A 240 mm run measured along the old centre path supplies the approach.
    arc_length = np.r_[0, np.cumsum(np.linalg.norm(np.diff(centre, axis=0), axis=1))]
    run_start = 4 * points_per_station
    run_end = int(np.argmin(abs(arc_length - arc_length[run_start] - .240)))
    run_fraction = (arc_length[run_start:run_end + 1] - arc_length[run_start])
    run_fraction /= run_fraction[-1]
    chord = centre[run_start] + run_fraction[:, None] * (centre[run_end] - centre[run_start])
    blend_to_chord = np.sin(np.pi * run_fraction) ** 2
    centre[run_start:run_end + 1] += (chord - centre[run_start:run_end + 1]) * blend_to_chord[:, None]

    lead_join = 156
    arc_start = 172
    arc_end = 229
    return_join = 270
    turn_heading = math.radians(110)
    turn_angle = math.radians(120)
    radius = .110
    easing = .036
    turn = eased_turn(np.array([.303, .027, -.175]), -.143, turn_heading, turn_angle,
                      radius, easing, arc_end - arc_start + 1)
    centre[lead_join:arc_start + 1] = connect(
        centre[lead_join], turn[0], centre[lead_join + 1] - centre[lead_join - 1],
        np.array([math.cos(turn_heading), math.sin(turn_heading), 0]), arc_start - lead_join + 1)
    centre[arc_start:arc_end + 1] = turn
    end_heading = turn_heading + turn_angle
    centre[arc_end:return_join + 1] = connect(
        turn[-1], centre[return_join], np.array([math.cos(end_heading), math.sin(end_heading), 0]),
        centre[return_join + 1] - centre[return_join - 1], return_join - arc_end + 1)

    blend_start = 38
    blend_end = 293
    width[blend_start:run_start] += smoothstep(np.linspace(0, 1, run_start - blend_start, endpoint=False)) * (
        .130 - width[blend_start:run_start])
    width[run_start:run_end + 1] = .130 + .035 * smoothstep(run_fraction)
    width[run_end:arc_end + 1] = .165
    width[arc_end:blend_end] += (1 - smoothstep(np.linspace(0, 1, blend_end - arc_end, endpoint=False))) * (
        .165 - width[arc_end:blend_end])

    # Roll the ribbon face across the turn independently of the path curvature.
    bank[arc_start:arc_end + 1] = np.radians(-21 + 62 * smoothstep(np.linspace(0, 1, len(turn))))
    bank[lead_join:arc_start] += smoothstep(np.linspace(0, 1, arc_start - lead_join, endpoint=False)) * (
        bank[arc_start] - bank[lead_join:arc_start])
    bank[arc_end:blend_end] += (1 - smoothstep(np.linspace(0, 1, blend_end - arc_end, endpoint=False))) * (
        np.radians(41) - bank[arc_end:blend_end])
    tangent = np.roll(centre, -1, axis=0) - np.roll(centre, 1, axis=0)
    across = np.column_stack((-tangent[:, 1], tangent[:, 0], np.zeros(len(tangent))))
    across /= np.linalg.norm(across, axis=1)[:, None]
    across *= np.cos(bank)[:, None]
    across[:, 2] = np.sin(bank)
    across *= width[:, None]
    # Fade into the original section skew at the edges of the edited region.
    blend = smoothstep((np.arange(len(rails)) - blend_start) / (run_start - blend_start))
    blend *= smoothstep((blend_end - np.arange(len(rails))) / (blend_end - return_join))
    across = original_across + blend[:, None] * (across - original_across)
    centre[:, 2] += camber
    return np.column_stack((centre - across / 2, centre + across / 2)), {
        'approach_rows': [run_start, run_end], 'turn_rows': [arc_start, arc_end],
        'bend_radius_in_plan_mm': radius * 1000, 'turn_degrees': math.degrees(turn_angle),
        'curvature_ramp_each_mm': easing * 1000,
        'turn_length_in_plan_mm': (radius * turn_angle + easing) * 1000,
        'bend_width_mm': 165, 'bank_angles_degrees': [-21, 41],
    }
