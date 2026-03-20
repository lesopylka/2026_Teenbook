import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import math

NODE_H = 0.08

nodes = {
    "Подросток":      (0.50, 0.92),
    "Родитель":       (0.12, 0.72),
    "Общение":        (0.88, 0.72),
    "Конфликт":       (0.50, 0.52),
    "Ссора":          (0.12, 0.32),
    "Агрессия":       (0.88, 0.32),
    "Гордость":       (0.10, 0.12),
    "Примирение":     (0.50, 0.12),
    "Социальная сеть":(0.90, 0.12),
    "Эмпатия":        (0.25, -0.08),
    "Прощение":       (0.75, -0.08),
}

edges = [
    ("Подросток",       "Родитель",       "взаимодействует с",  0.0,   0.02),
    ("Подросток",       "Общение",        "участвует в",        0.0,   0.02),
    ("Подросток",       "Конфликт",       "участвует в",        0.0,   0.025),
    ("Общение",         "Конфликт",       "может приводить к",  0.0,   0.02),
    ("Конфликт",        "Ссора",          "проявляется как",    0.0,   0.02),
    ("Конфликт",        "Агрессия",       "может вызывать",     0.0,   0.02),
    ("Конфликт",        "Примирение",     "разрешается через",  0.0,   0.025),
    ("Гордость",        "Примирение",     "может мешать",       0.0,   0.02),
    ("Эмпатия",         "Примирение",     "способствует",       0.0,   0.02),
    ("Примирение",      "Прощение",       "включает",           0.0,   0.02),
    ("Социальная сеть", "Конфликт",       "среда для",          0.0,   0.02),
]


def node_half_w(label):
    return 0.12 if len(label) > 12 else 0.10


def box_edge(cx, cy, hw, hh, tx, ty):
    dx = tx - cx
    dy = ty - cy
    if dx == 0 and dy == 0:
        return cx, cy + hh
    angle = math.atan2(dy, dx)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    sx = hw / abs(cos_a) if cos_a != 0 else 1e9
    sy = hh / abs(sin_a) if sin_a != 0 else 1e9
    r = min(sx, sy)
    return cx + r * cos_a, cy + r * sin_a


def draw_node(ax, label, x, y):
    hw = node_half_w(label)
    w = hw * 2
    h = NODE_H
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.5,
        edgecolor="black",
        facecolor="white",
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=11)


def draw_edge(ax, start, end, text, dx, dy):
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    hw1 = node_half_w(start)
    hw2 = node_half_w(end)
    hh = NODE_H / 2 + 0.005

    ex1, ey1 = box_edge(x1, y1, hw1, hh, x2, y2)
    ex2, ey2 = box_edge(x2, y2, hw2, hh, x1, y1)

    ax.annotate(
        "",
        xy=(ex2, ey2),
        xytext=(ex1, ey1),
        arrowprops=dict(arrowstyle="->", lw=1.4),
    )

    mx = (x1 + x2) / 2 + dx
    my = (y1 + y2) / 2 + dy
    ax.text(mx, my, text, ha="center", va="center", fontsize=9)


fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.17, 1.00)
ax.axis("off")

for label, (x, y) in nodes.items():
    draw_node(ax, label, x, y)

for start, end, label, dx, dy in edges:
    draw_edge(ax, start, end, label, dx, dy)

plt.savefig("../images/ontology.png", dpi=300, bbox_inches="tight")
plt.close()

print("Схема сохранена в ../images/ontology.png")
