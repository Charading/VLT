"""Minimal KLE reader: returns (x, y, w, h, label) in key units, y DOWN like KLE."""
import json


def read_kle(path):
    data = json.load(open(path, encoding="utf-8"))
    keys = []
    cy = 0.0
    for row in data:
        if isinstance(row, dict):      # metadata
            continue
        cx = 0.0
        w = h = 1.0
        for item in row:
            if isinstance(item, dict):
                cx += item.get("x", 0.0)
                cy += item.get("y", 0.0)
                w = item.get("w", 1.0)
                h = item.get("h", 1.0)
            else:
                keys.append((cx, cy, w, h, item))
                cx += w
                w = h = 1.0
        cy += 1.0
    return keys


def key_centres_mm(path, U=19.05):
    """(cx, cy, w_u, label) in the PLATE frame (mm, y negated so 'up the board' is +y)."""
    out = []
    for x, y, w, h, label in read_kle(path):
        out.append(((x + w / 2) * U, -(y + h / 2) * U, w, label))
    return out


if __name__ == "__main__":
    import sys
    ks = read_kle(sys.argv[1])
    print(len(ks), "keys")
    for k in ks:
        print(k)
