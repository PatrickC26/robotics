#!/usr/bin/env python3
import argparse
import sys
import json
import numpy as np
import cv2

# ---------------- Circle color detection ----------------

def detect_color(frame, center, radius):
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (int(center[0]), int(center[1])), int(max(1.0, radius * 0.8)), 255, -1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    H, S, V = cv2.split(hsv)
    H = H[mask == 255]
    S = S[mask == 255]
    V = V[mask == 255]
    valid = (S > 50) & (V > 50)
    H = H[valid]
    if len(H) == 0:
        return "green"
    red_mask = ((H <= 10) | (H >= 170))
    green_mask = ((H >= 35) & (H <= 85))
    red_ratio = np.sum(red_mask) / len(H) if len(H) > 0 else 0.0
    green_ratio = np.sum(green_mask) / len(H) if len(H) > 0 else 0.0
    if red_ratio > green_ratio and red_ratio > 0.1:
        return "red"
    elif green_ratio > red_ratio and green_ratio > 0.1:
        return "green"
    else:
        return "unknown"

def detect_circles_and_overlay(img_bgr, out_path):
    frame = img_bgr.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=30, minRadius=10, maxRadius=100)
    results = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = circles[0].astype(np.float32)
        circles = circles[np.argsort(circles[:, 0])]
        for (u, v, r) in circles:
            color = detect_color(frame, (u, v), r)
            results.append({
                "center": [float(u), float(v)],
                "radius": float(r),
                "color": color
            })
            cv2.circle(frame, (int(u), int(v)), int(r), (0, 255, 0), 2)
            cv2.circle(frame, (int(u), int(v)), 2, (0, 255, 0), 3)
            cv2.putText(frame, color, (int(u) + 10, int(v) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imwrite(out_path, frame)
    return results

# ---------------- Grid + walls ----------------

def binarize_walls(gray: np.ndarray, adaptive: bool) -> np.ndarray:
    if adaptive:
        block = 35 if min(gray.shape[:2]) > 400 else 21
        th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, block, 5)
    else:
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return th

def morph(mask: np.ndarray, k_open: int, k_close: int) -> np.ndarray:
    m = mask.copy()
    if k_open > 0:
        ko = cv2.getStructuringElement(cv2.MORPH_RECT, (2*k_open+1, 2*k_open+1))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, ko, iterations=1)
    if k_close > 0:
        kc = cv2.getStructuringElement(cv2.MORPH_RECT, (2*k_close+1, 2*k_close+1))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, kc, iterations=1)
    return m

def draw_grid_lines(img: np.ndarray, grid: int) -> np.ndarray:
    out = img.copy()
    h, w = out.shape[:2]
    color = (255, 255, 255)
    for y in range(0, h, grid):
        cv2.line(out, (0, y), (w-1, y), color, 1)
    for x in range(0, w, grid):
        cv2.line(out, (x, 0), (x, h-1), color, 1)
    return out

def draw_grid_with_values(img: np.ndarray, grid: int, values_mat: np.ndarray,
                          font_scale: float, thickness: int) -> np.ndarray:
    out = draw_grid_lines(img, grid)
    h, w = out.shape[:2]
    gh, gw = values_mat.shape
    for gy in range(gh):
        y0 = gy * grid
        y1 = min((gy + 1) * grid, h)
        cy = int((y0 + y1) / 2)
        for gx in range(gw):
            x0 = gx * grid
            x1 = min((gx + 1) * grid, w)
            cx = int((x0 + x1) / 2)
            text = str(int(values_mat[gy, gx]))
            cv2.putText(out, text, (cx-6, cy+5), cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, (0,0,0), thickness+2, cv2.LINE_AA)
            cv2.putText(out, text, (cx-6, cy+5), cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, (255,255,255), thickness, cv2.LINE_AA)
    return out

# ---------------- Main ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default = "part_2_maze_solution/02_maze_warp.png")
    ap.add_argument("--grid", type=int, default=25)
    ap.add_argument("--adaptive", type=int, default=0)
    ap.add_argument("--blur", type=int, default=5)
    ap.add_argument("--open", type=int, default=0)
    ap.add_argument("--close", type=int, default=0)
    ap.add_argument("--threshold", type=float, default=10.0)

    ap.add_argument("--circles-overlay-out", default="part_2_maze_solution/03_circles_overlay.png")
    ap.add_argument("--grid-overlay-out", default="part_2_maze_solution/03_grid_overlay.png")
    ap.add_argument("--grid-overlay-annot-out", default="part_2_maze_solution/03_grid_overlay_annot.png")
    ap.add_argument("--walls-mask-out", default="part_2_maze_solution/03_walls_mask.png")
    ap.add_argument("--json-out", default="part_2_maze_solution/03_result.json")

    ap.add_argument("--font-scale", type=float, default=0.4)
    ap.add_argument("--thickness", type=int, default=1)

    args = ap.parse_args()

    img = cv2.imread(args.input, cv2.IMREAD_COLOR)
    if img is None:
        print(f"Error: cannot read image '{args.input}'", file=sys.stderr)
        sys.exit(1)

    grid = max(1, args.grid)

    # 1. Detect circles
    circles_info = detect_circles_and_overlay(img, args.circles_overlay_out)

    # 2a. Grid overlay
    grid_overlay = draw_grid_lines(img, grid)
    cv2.imwrite(args.grid_overlay_out, grid_overlay)

    # 2b. Walls mask
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if args.blur > 0:
        k = max(1, args.blur | 1)
        gray = cv2.medianBlur(gray, k)
    walls_mask = binarize_walls(gray, adaptive=bool(args.adaptive))
    walls_mask = morph(walls_mask, k_open=max(0, args.open), k_close=max(0, args.close))

    # RASE walls where circles are
    for c in circles_info:
        cx, cy = int(c["center"][0]), int(c["center"][1])
        r = int(c["radius"] * 1.2)
        cv2.circle(walls_mask, (cx, cy), r, 0, -1)  # set to 0 (non-wall)

    cv2.imwrite(args.walls_mask_out, walls_mask)

    # 2c. Build grid cells
    h, w = walls_mask.shape[:2]
    gh = (h + grid - 1) // grid
    gw = (w + grid - 1) // grid
    values_mat = np.zeros((gh, gw), dtype=np.uint8)
    cells = []
    for gy in range(gh):
        y0 = gy * grid
        y1 = min((gy + 1) * grid, h)
        cy = int((y0 + y1) / 2)
        for gx in range(gw):
            x0 = gx * grid
            x1 = min((gx + 1) * grid, w)
            cx = int((x0 + x1) / 2)
            blk = walls_mask[y0:y1, x0:x1]
            wall_pct = (blk > 0).mean() * 100.0 if blk.size > 0 else 0.0
            value = 0 if wall_pct >= args.threshold else 1
            values_mat[gy, gx] = value
            cells.append({
                "row": int(gy),
                "col": int(gx),
                "value": int(value),
                "center_px": [int(cx), int(cy)]
            })

    # 2d. Annotated grid
    grid_overlay_annot = draw_grid_with_values(img, grid, values_mat, args.font_scale, args.thickness)
    cv2.imwrite(args.grid_overlay_annot_out, grid_overlay_annot)

    # 3. Write JSON
    meta = {
        "input": args.input,
        "circles_overlay_path": args.circles_overlay_out,
        "grid_size_px": grid,
        "grid_rows": int(gh),
        "grid_cols": int(gw),
        "threshold_percent": args.threshold,
        "grid_overlay_path": args.grid_overlay_out,
        "grid_overlay_annot_path": args.grid_overlay_annot_out,
        "walls_mask_path": args.walls_mask_out,
        "circles": circles_info,
        "cells": cells
    }
    with open(args.json_out, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Circles overlay saved to: {args.circles_overlay_out}")
    print(f"Grid overlay saved to: {args.grid_overlay_out}")
    print(f"Walls mask saved to: {args.walls_mask_out}")
    print(f"Annotated grid overlay saved to: {args.grid_overlay_annot_out}")
    print(f"JSON saved to: {args.json_out}")
    print("Legend: cell value 1 = path, 0 = wall")

if __name__ == "__main__":
    main()
