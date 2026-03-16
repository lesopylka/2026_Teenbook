import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import math

NODE_H = 0.02

nodes = {
    "Подросток":           (0.50, 0.98),
    "Родители":            (0.25, 0.82),
    "Брат/сестра":         (0.75, 0.82),
    
    "Сепарация":           (0.50, 0.72),
    "Конфликт":            (0.20, 0.52),
    "Примирение":          (0.80, 0.52),
    "Развод":              (0.50, 0.45),
    
    "Просьба":             (0.00, 0.25),
    "Границы":             (0.35, 0.10),
    "Традиции":            (0.55, 0.00),
    "Общение":             (1, 0.25),
    
    "Эмпатия":             (0.30, -0.08),
    "Прощение":            (0.70, -0.08),
}

edges = [
    ("Подросток",       "Родители",        "взаимодействует с",    0.0,   0.003),
    ("Подросток",       "Сепарация",       "проходит через",       0.0,   0.002),
    ("Родители",        "Сепарация",       "влияют на",            -0.003, 0.001),
    ("Сепарация",       "Конфликт",        "может вызывать",       0.0,   0.002),
    
    ("Подросток",       "Брат/сестра",     "делит опыт с",         0.0,   0.003),
    ("Брат/сестра",     "Конфликт",        "могут иметь",          0.003,  0.001),
    ("Брат/сестра",     "Примирение",      "достигают",            0.003,  0.001),
    
    ("Развод",          "Подросток",       "влияет на",            0.0,   0.002),
    ("Развод",          "Конфликт",        "обостряет",            0.002,  0.001),
    ("Развод",          "Родители",        "разделяет",            -0.002, -0.001),
    ("Развод",          "Брат/сестра",     "сближает или ссорит",  0.0,   0.002),
    ("Развод",          "Традиции",        "меняет или разрушает", 0.002,  0.0),
    ("Примирение",      "Развод",          "редко достижимо",      0.003,  -0.002),
    
    ("Конфликт",        "Примирение",      "разрешается через",    0.007,  0.0),
    ("Конфликт",        "Просьба",         "может быть решён",     -0.003, 0.001),
    
    ("Просьба",         "Родители",        "обращена к",           0.0,   0.001),
    ("Просьба",         "Границы",         "учитывает",            -0.002, 0.0),
    ("Просьба",         "Общение",         "требует",              0.002,  0.001),
    ("Просьба",         "Примирение",      "помогает в",           -0.002, -0.001),
    ("Просьба",         "Эмпатия",         "требует",              -0.002, 0.00),
    
    ("Традиции",        "Родители",        "объединяют с",         0.003,  0.00),
    ("Традиции",        "Брат/сестра",     "сближают",             0.003,  0.00),
    ("Традиции",        "Общение",         "поддерживают",         0.00,   0.002),
    ("Традиции",        "Развод",          "могут пострадать",     0.002,  0.001),
    ("Традиции",        "Подросток",       "дают опору",           0.00,   0.002),
    ("Традиции",        "Примирение",      "способствуют",         0.002,  0.001),
    
    ("Границы",         "Родители",        "нужны с",              0.00,   0.001),
    ("Границы",         "Конфликт",        "снижают риск",         -0.003, -0.001),
    ("Общение",         "Конфликт",        "может предотвращать",  -0.004, 0.001),
    ("Общение",         "Примирение",      "необходимо для",       0.004,  0.001),
    ("Эмпатия",         "Примирение",      "способствует",         0.002,  0.001),
    ("Прощение",        "Примирение",      "завершает",            -0.002, 0.001),
]


def node_half_w(label):
    if len(label) > 10:
        return 0.07
    elif len(label) > 6:
        return 0.05
    else:
        return 0.03


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
        zorder=2,
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=10, weight="bold", zorder=3)


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
        arrowprops=dict(
            arrowstyle="->",
            lw=1.0,
            color="gray",
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=1,
    )
    
    mx = (x1 * 0.7 + x2 * 0.3 ) + dx
    my = (y1 * 0.7 + y2 * 0.3 ) + dy
    
    ax.text(
        mx, my, text,
        ha="center", va="center",
        fontsize=7,
        style="italic",
        color="darkblue",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85, edgecolor="lightgray", linewidth=0.5),
        zorder=4,
    )


fig, ax = plt.subplots(figsize=(20, 15))
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.15, 1.08)
ax.axis("off")

for label, (x, y) in nodes.items():
    draw_node(ax, label, x, y)

for start, end, label, dx, dy in edges:
    draw_edge(ax, start, end, label, dx, dy)

plt.savefig("./images/family_ontology.png", dpi=300, bbox_inches="tight")
plt.close()