# -*- coding: utf-8 -*-
import numpy
import math


def get_collision(start, end, edges):
    for i in range(len(edges) // 4):
        edge = (edges[i * 4 + 0], edges[i * 4 + 1], edges[i * 4 + 2], edges[i * 4 + 3])
        if edge[0] == edge[2]:  # same x value
            distance = max(0.001, abs(start[0] - end[0]))
            distance_start = abs(start[0] - edge[0]) / distance
            distance_end = abs(end[0] - edge[0]) / distance

            x = edge[0]
            y = start[1] * distance_end + end[1] * distance_start
            if min(edge[1], edge[3]) - 0.0001 < y < max(
                edge[1], edge[3]
            ) + 0.0001 and min(start[0], end[0]) < x < max(start[0], end[0]):
                return True

        elif edge[1] == edge[3]:  # same y value
            distance = max(0.001, abs(start[1] - end[1]))
            distance_start = abs(start[1] - edge[1]) / distance
            distance_end = abs(end[1] - edge[1]) / distance

            y = edge[1]
            x = start[0] * distance_end + end[0] * distance_start
            if min(edge[0], edge[2]) - 0.0001 < x < max(
                edge[0], edge[2]
            ) + 0.0001 and min(start[1], end[1]) < y < max(start[1], end[1]):
                return True
    return False


def find_collision_point(start, end, edges):
    collision_point = [None, None, None]  # Distance, x, y

    for i in range(len(edges) // 4):
        edge = (edges[i * 4 + 0], edges[i * 4 + 1], edges[i * 4 + 2], edges[i * 4 + 3])
        if edge[0] == edge[2]:  # same x value
            distance = max(0.001, abs(start[0] - end[0]))
            distance_start = abs(start[0] - edge[0]) / distance
            distance_end = abs(end[0] - edge[0]) / distance

            x = edge[0]
            y = start[1] * distance_end + end[1] * distance_start
            if min(edge[1], edge[3]) < y < max(edge[1], edge[3]) and min(
                start[0], end[0]
            ) < x < max(start[0], end[0]):
                d = math.sqrt((start[0] - x) ** 2 + (start[1] - y) ** 2)
                if collision_point[0] is None or collision_point[0] > d:
                    collision_point[0] = d
                    collision_point[1] = x
                    collision_point[2] = y

        elif edge[1] == edge[3]:  # same y value
            distance = max(0.001, abs(start[1] - end[1]))
            distance_start = abs(start[1] - edge[1]) / distance
            distance_end = abs(end[1] - edge[1]) / distance

            y = edge[1]
            x = start[0] * distance_end + end[0] * distance_start
            if min(edge[0], edge[2]) < x < max(edge[0], edge[2]) and min(
                start[1], end[1]
            ) < y < max(start[1], end[1]):
                d = math.sqrt((start[0] - x) ** 2 + (start[1] - y) ** 2)
                if collision_point[0] is None or collision_point[0] > d:
                    collision_point[0] = d
                    collision_point[1] = x
                    collision_point[2] = y
    return collision_point


def get_triangle_points(
    view=numpy.array([[]]), light_source=[], corners=numpy.array([[]]), edges=[]
):
    corner_angles = []
    for corner in corners:
        collision = get_collision(light_source, corner, edges)
        if collision:
            continue

        angle = math.atan2(corner[1] - light_source[1], corner[0] - light_source[0])
        corner_angles.append([angle, *corner])

        for variation in (-0.0001, 0.0001):
            v_angle = angle + variation
            v_corner = (
                math.cos(v_angle) * 100 + light_source[0],
                math.sin(v_angle) * 100 + light_source[1],
            )

            collision = find_collision_point(light_source, v_corner, edges)
            if collision[0] != -1:
                v_corner = collision[1:]
                if (
                    corner[0] != v_corner[0]
                    and corner[1] != v_corner[1]
                    and None not in v_corner
                ):
                    corner_angles.append([v_angle, *v_corner])

    return corner_angles


def find_corners(array: numpy.array):
    # Create copy
    view = array.copy()
    view[0, :] = 0
    view[:, 0] = 0
    view[view.shape[0] - 1, :] = 0
    view[:, view.shape[1] - 1] = 0

    # Shifted view
    view_shifted_right = numpy.roll(view, shift=-1, axis=0)
    view_shifted_down = numpy.roll(view, shift=-1, axis=1)
    view_shifted_diagonal = numpy.roll(view, shift=(-1, -1), axis=(0, 1))

    # Find corners
    # Contains all corners if blocks, which have 1 or 3 blocks near them.
    count_air_blocks = (
        (view == 0).astype(int)
        + (view_shifted_right == 0).astype(int)
        + (view_shifted_down == 0).astype(int)
        + (view_shifted_diagonal == 0).astype(int)
    )
    corner_indices = numpy.where((count_air_blocks == 1) | (count_air_blocks == 3))
    corners = set(zip(corner_indices[0], corner_indices[1]))
    additional_corners = numpy.where(
        (count_air_blocks == 2) & (view == 0) == (view_shifted_diagonal == 0)
    )
    additional_corners = set(zip(additional_corners[0], additional_corners[1]))
    # corners = corners.union(set(zip(additional_corners[0], additional_corners[1])))

    # Add window corners
    corners.add((-1, -1))
    corners.add((-1, view.shape[1] - 1))
    corners.add((view.shape[0] - 1, -1))
    corners.add((view.shape[0] - 1, view.shape[1] - 1))

    return corners, additional_corners


def get_edges(corners):
    # Find vertical edges
    sorted_corners = sorted(corners, key=lambda corner: (corner[0], corner[1]))
    flattened_corners = [coord for corner in sorted_corners for coord in corner]
    edges = flattened_corners

    # Find horizontal edges
    sorted_corners = sorted(corners, key=lambda corner: (corner[1], corner[0]))
    flattened_corners = [coord for corner in sorted_corners for coord in corner]
    edges.extend(flattened_corners)

    return edges
