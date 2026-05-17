from tkinter import *
import itertools
import math
import random

try:
    from VisualizationApp import *
    from tkUtilities import *
except ModuleNotFoundError:
    from .VisualizationApp import *
    from .tkUtilities import *


def normalize_edge(u, v):
    if u == v:
        return None
    return (u, v) if u < v else (v, u)


def canonical_edges(edges):
    normalized = []
    for u, v in edges:
        edge = normalize_edge(u, v)
        if edge:
            normalized.append(edge)
    return sorted(set(normalized))


def build_incident_map(vertices, edges):
    incident = {v: set() for v in vertices}
    for u, v in edges:
        if u in incident:
            incident[u].add((u, v))
        if v in incident:
            incident[v].add((u, v))
    return incident


def is_vertex_cover(cover, edges):
    return all(u in cover or v in cover for u, v in edges)


def two_approx_vertex_cover(vertices, edges, capture_steps=False):
    remaining = set(canonical_edges(edges))
    incident = build_incident_map(vertices, remaining)
    cover = set()
    steps = []

    while remaining:
        chosen = min(remaining)
        u, v = chosen
        cover.add(u)
        cover.add(v)
        removed = []
        for edge in sorted(incident[u] | incident[v]):
            if edge in remaining:
                remaining.remove(edge)
                removed.append(edge)
        if capture_steps:
            steps.append(
                {
                    'chosen_edge': chosen,
                    'removed_edges': removed,
                    'cover_after': set(cover),
                    'remaining_edges': set(remaining),
                }
            )
    return cover, steps


def brute_force_min_vertex_cover(vertices, edges):
    edges = canonical_edges(edges)
    if not edges:
        return set()
    ordered_vertices = list(vertices)
    for r in range(len(ordered_vertices) + 1):
        for subset in itertools.combinations(ordered_vertices, r):
            candidate = set(subset)
            if is_vertex_cover(candidate, edges):
                return candidate
    return set(ordered_vertices)


def random_graph(vertex_count=8, edge_probability=0.35):
    vertex_count = max(2, min(12, int(vertex_count)))
    edge_probability = max(0.05, min(0.9, float(edge_probability)))
    vertices = [chr(ord('A') + i) for i in range(vertex_count)]
    edges = []
    for i in range(vertex_count):
        for j in range(i + 1, vertex_count):
            if random.random() < edge_probability:
                edges.append((vertices[i], vertices[j]))
    if not edges:
        i = random.randrange(vertex_count - 1)
        edges.append((vertices[i], vertices[i + 1]))
    return vertices, canonical_edges(edges)


class ApproxVertexCover(VisualizationApp):
    NODE_RADIUS = 20
    EDGE_DEFAULT_COLOR = 'gray45'
    EDGE_COVERED_COLOR = 'seagreen4'
    EDGE_ACTIVE_COLOR = 'orange2'
    NODE_DEFAULT_FILL = 'light sky blue'
    NODE_COVER_FILL = 'gold'
    NODE_ACTIVE_FILL = 'orange'
    NODE_TEXT_COLOR = 'black'
    BACKGROUND_COLOR = 'old lace'
    LEGEND_FONT = ('Helvetica', -11)
    TITLE_FONT = ('Helvetica', -16)
    STEP_WAIT = 0.24

    SAMPLE_VERTICES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    SAMPLE_EDGES = canonical_edges(
        [
            ('A', 'B'),
            ('A', 'C'),
            ('B', 'D'),
            ('C', 'D'),
            ('C', 'E'),
            ('D', 'F'),
            ('E', 'F'),
            ('E', 'G'),
            ('F', 'H'),
            ('G', 'H'),
        ]
    )

    approxCode = '''
def twoApproxVertexCover(G=(V, E)):
   C = set()
   uncovered = set(E)
   while uncovered:
      (u, v) = choose_any_edge(uncovered)
      C.add(u)
      C.add(v)
      for e in incident_edges(u) U incident_edges(v):
         uncovered.discard(e)
   return C
'''

    def __init__(
        self,
        title='2-Approx Vertex Cover - SarasAI - Approximation Algorithms',
        **kwargs
    ):
        super().__init__(title=title, **kwargs)
        self.vertices = []
        self.edges = []
        self.vertexItems = {}
        self.edgeItems = {}
        self.positions = {}
        self.coverSet = set()
        self.coveredEdges = set()
        self.activeEdge = None
        self.makeButtons()
        self.loadGraph(self.SAMPLE_VERTICES, self.SAMPLE_EDGES)

    def makeButtons(self):
        self.addOperation(
            'Load Example',
            self.clickLoadExample,
            helpText='Load a deterministic sample graph for repeatable analysis',
        )
        self.addOperation(
            'Random Graph',
            self.clickRandomGraph,
            helpText='Generate a random graph and reset approximation state',
        )
        self.addOperation(
            'Run 2-Approx',
            self.clickRunApprox,
            helpText='Run the standard 2-approximation for Vertex Cover',
        )
        self.addOperation(
            'Reset Colors',
            self.clickResetState,
            helpText='Reset graph state without changing graph structure',
        )
        self.addAnimationButtons()

    def computePositions(self):
        n = len(self.vertices)
        if n == 0:
            return {}
        width, height = widgetDimensions(self.canvas)
        if width < 100 or height < 100:
            width = self.targetCanvasWidth
            height = self.targetCanvasHeight
        cx = width * 0.48
        cy = height * 0.45
        radius = min(width * 0.3, height * 0.3)
        positions = {}
        for i, vertex in enumerate(self.vertices):
            angle = (2 * math.pi * i / n) - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions[vertex] = (x, y)
        return positions

    def loadGraph(self, vertices, edges):
        self.vertices = list(vertices)
        self.edges = canonical_edges(edges)
        self.coverSet = set()
        self.coveredEdges = set()
        self.activeEdge = None
        self.positions = self.computePositions()
        self.drawGraph()
        self.setMessage(
            'Loaded graph with {} vertices and {} edges'.format(
                len(self.vertices), len(self.edges)
            )
        )

    def drawGraph(self):
        self.canvas.delete('all')
        self.vertexItems = {}
        self.edgeItems = {}
        self.canvas.create_rectangle(
            *self.visibleCanvas(), fill=self.BACKGROUND_COLOR, outline=''
        )
        self.canvas.create_text(
            12,
            12,
            anchor=NW,
            text='NP-Complete Problem: Vertex Cover (2-Approximation)',
            font=self.TITLE_FONT,
            fill='black',
        )

        for edge in self.edges:
            u, v = edge
            line = self.canvas.create_line(
                *self.positions[u],
                *self.positions[v],
                fill=self.EDGE_DEFAULT_COLOR,
                width=2,
            )
            self.edgeItems[edge] = line

        for vertex in self.vertices:
            x, y = self.positions[vertex]
            oval = self.canvas.create_oval(
                x - self.NODE_RADIUS,
                y - self.NODE_RADIUS,
                x + self.NODE_RADIUS,
                y + self.NODE_RADIUS,
                fill=self.NODE_DEFAULT_FILL,
                outline='black',
                width=1,
            )
            label = self.canvas.create_text(
                x, y, text=vertex, font=('Helvetica', -13, 'bold')
            )
            self.vertexItems[vertex] = (oval, label)

        legend_y = int(widgetDimensions(self.canvas)[1]) - 48
        self.canvas.create_line(
            24,
            legend_y,
            64,
            legend_y,
            fill=self.EDGE_DEFAULT_COLOR,
            width=2,
        )
        self.canvas.create_text(
            84,
            legend_y,
            anchor=W,
            text='Uncovered edge',
            font=self.LEGEND_FONT,
        )
        self.canvas.create_line(
            214,
            legend_y,
            254,
            legend_y,
            fill=self.EDGE_ACTIVE_COLOR,
            width=4,
        )
        self.canvas.create_text(
            274, legend_y, anchor=W, text='Chosen edge', font=self.LEGEND_FONT
        )
        self.canvas.create_line(
            384,
            legend_y,
            424,
            legend_y,
            fill=self.EDGE_COVERED_COLOR,
            width=3,
        )
        self.canvas.create_text(
            444, legend_y, anchor=W, text='Covered edge', font=self.LEGEND_FONT
        )
        self.updateAppearance()

    def updateAppearance(self):
        for edge, line in self.edgeItems.items():
            if edge == self.activeEdge:
                color = self.EDGE_ACTIVE_COLOR
                width = 4
            elif edge in self.coveredEdges:
                color = self.EDGE_COVERED_COLOR
                width = 3
            else:
                color = self.EDGE_DEFAULT_COLOR
                width = 2
            self.canvas.itemconfigure(line, fill=color, width=width)

        active_vertices = set(self.activeEdge or ())
        for vertex, items in self.vertexItems.items():
            if vertex in active_vertices:
                fill = self.NODE_ACTIVE_FILL
            elif vertex in self.coverSet:
                fill = self.NODE_COVER_FILL
            else:
                fill = self.NODE_DEFAULT_FILL
            self.canvas.itemconfigure(items[0], fill=fill)
            self.canvas.itemconfigure(items[1], fill=self.NODE_TEXT_COLOR)

    def resetState(self):
        self.coverSet = set()
        self.coveredEdges = set()
        self.activeEdge = None
        self.updateAppearance()

    def runApproximation(self, start=True, code=approxCode, wait=STEP_WAIT):
        if not self.edges:
            self.setMessage('Graph has no edges. Vertex cover is empty.')
            return

        self.resetState()
        remaining = set(self.edges)
        incident = build_incident_map(self.vertices, self.edges)
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start, sleepTime=wait / 4
        )

        self.highlightCode('C = set()', callEnviron, wait=wait)
        self.highlightCode('uncovered = set(E)', callEnviron, wait=wait)

        while remaining:
            self.highlightCode('while uncovered', callEnviron, wait=wait)
            chosen = min(remaining)
            u, v = chosen
            self.activeEdge = chosen
            self.updateAppearance()
            self.highlightCode(
                '(u, v) = choose_any_edge(uncovered)', callEnviron, wait=wait
            )
            self.setMessage(
                'Choose edge ({}, {}) and add both endpoints to cover'.format(
                    u, v
                )
            )

            self.coverSet.add(u)
            self.highlightCode('C.add(u)', callEnviron, wait=wait / 2)
            self.updateAppearance()

            self.coverSet.add(v)
            self.highlightCode('C.add(v)', callEnviron, wait=wait / 2)
            self.updateAppearance()

            self.highlightCode(
                'for e in incident_edges(u) U incident_edges(v)',
                callEnviron,
                wait=wait / 2,
            )
            for edge in sorted(incident[u] | incident[v]):
                if edge in remaining:
                    remaining.remove(edge)
                    self.coveredEdges.add(edge)
                    self.highlightCode(
                        'uncovered.discard(e)', callEnviron, wait=wait / 4
                    )
                    self.updateAppearance()

            self.activeEdge = None
            self.updateAppearance()

        self.highlightCode('return C', callEnviron, wait=wait)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 4)

        cover = set(self.coverSet)
        optimal = brute_force_min_vertex_cover(self.vertices, self.edges)
        ratio = (len(cover) / len(optimal)) if optimal else 1.0
        self.setMessage(
            'Approx cover size = {} | optimal size = {} | ratio = {:.2f}'.format(
                len(cover), len(optimal), ratio
            )
        )

    def clickLoadExample(self):
        self.loadGraph(self.SAMPLE_VERTICES, self.SAMPLE_EDGES)

    def clickRandomGraph(self):
        vertices, edges = random_graph(
            vertex_count=random.randint(6, 10),
            edge_probability=random.uniform(0.25, 0.45),
        )
        self.loadGraph(vertices, edges)

    def clickRunApprox(self):
        self.runApproximation(start=self.startMode())

    def clickResetState(self):
        self.resetState()
        self.setMessage(
            'State reset. Run 2-Approx to visualize construction again.'
        )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Visualize 2-approximation for Vertex Cover',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-s', '--seed', default=None, help='Seed the random generator'
    )
    parser.add_argument(
        '-d',
        '--debug',
        default=False,
        action='store_true',
        help='Show debugging information.',
    )
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)

    app = ApproxVertexCover()
    app.DEBUG = args.debug
    app.runVisualization()
