import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

nodes = {
    "Средняя школа": (0.5, 0.88),
    "Учитель": (0.2, 0.63),
    "Ученик": (0.8, 0.63),
    "Общение": (0.5, 0.45),
    "Дружба": (0.22, 0.2),
    "Конфликт": (0.78, 0.2),
    "Травля": (0.5, 0.03),
}

edges = [
    ("Средняя школа", "Учитель", "включает"),
    ("Средняя школа", "Ученик", "включает"),
    ("Учитель", "Ученик", "взаимодействует с"),
    ("Ученик", "Общение", "участвует в"),
    ("Общение", "Дружба", "может приводить к"),
    ("Общение", "Конфликт", "может приводить к"),
    ("Конфликт", "Травля", "может перерасти в"),
]


def draw_node(ax, label, x, y, w=0.24, h=0.09):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.5,
        edgecolor="black",
        facecolor="white"
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=11)


def draw_edge(ax, start, end, text):
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]

    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            lw=1.4,
            shrinkA=20,
            shrinkB=20
        )
    )

    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    ax.text(mx, my + 0.025, text, ha="center", va="center", fontsize=9)


fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(0, 1)
ax.set_ylim(-0.05, 1)
ax.axis("off")

for label, (x, y) in nodes.items():
    draw_node(ax, label, x, y)

for start, end, label in edges:
    draw_edge(ax, start, end, label)

plt.savefig("../images/ontology.png", dpi=300, bbox_inches="tight")
plt.close()

print("Схема сохранена в ../images/ontology.png")