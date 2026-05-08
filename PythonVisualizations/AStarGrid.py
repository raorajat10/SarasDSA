from tkinter import *
import random
import heapq
import math

try:
    from VisualizationApp import *
    from tkUtilities import *
except ModuleNotFoundError:
    from .VisualizationApp import *
    from .tkUtilities import *


class AStarGrid(VisualizationApp):
    ROWS = 14
    COLS = 20
    GRID_PADDING = 20
    CELL_BORDER = 1
    BLOCK_PROB = 0.25
    GRID_BG = 'white'
    BLOCK_COLOR = 'gray25'
    OPEN_COLOR = 'LightSkyBlue1'
    CLOSED_COLOR = 'LightSteelBlue3'
    PATH_COLOR = 'gold'
    START_COLOR = 'SpringGreen3'
    GOAL_COLOR = 'tomato'
    CURRENT_COLOR = 'orange'
    TEXT_FONT = ('Helvetica', -10)

    def __init__(
            self,
            title="A* Grid Search - SarasAI - Introduction to Data Structures and Algorithms",
            rows=ROWS, cols=COLS, **kwargs):
        super().__init__(title=title, **kwargs)
        self.rows = rows
        self.cols = cols
        self.blockProb = self.BLOCK_PROB
        self.start = (0, 0)
        self.goal = (rows - 1, cols - 1)
        self.blocked = set()
        self.rects = {}
        self.searchState = {}
        self.makeButtons()
        self.newGrid(randomize=True)

    def gridBBox(self):
        canvasW, canvasH = widgetDimensions(self.canvas)
        left = self.GRID_PADDING
        top = self.GRID_PADDING
        right = canvasW - self.GRID_PADDING
        bottom = canvasH - self.GRID_PADDING
        return left, top, right, bottom

    def cellSize(self):
        left, top, right, bottom = self.gridBBox()
        return ((right - left) / self.cols, (bottom - top) / self.rows)

    def cellCoords(self, row, col):
        left, top, _, _ = self.gridBBox()
        cw, ch = self.cellSize()
        x0 = left + col * cw
        y0 = top + row * ch
        x1 = x0 + cw
        y1 = y0 + ch
        return x0, y0, x1, y1

    def eventToCell(self, event):
        left, top, right, bottom = self.gridBBox()
        if not (left <= event.x <= right and top <= event.y <= bottom):
            return None
        cw, ch = self.cellSize()
        col = int((event.x - left) // cw)
        row = int((event.y - top) // ch)
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return None

    def inBounds(self, cell):
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(self, cell):
        r, c = cell
        options = ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
        return [n for n in options if self.inBounds(n) and n not in self.blocked]

    def clearSearchState(self):
        self.searchState = {
            'open': set(),
            'closed': set(),
            'path': set(),
            'current': None,
        }

    def cellColor(self, cell):
        if cell == self.start:
            return self.START_COLOR
        if cell == self.goal:
            return self.GOAL_COLOR
        if cell in self.searchState.get('path', set()):
            return self.PATH_COLOR
        if cell == self.searchState.get('current'):
            return self.CURRENT_COLOR
        if cell in self.searchState.get('closed', set()):
            return self.CLOSED_COLOR
        if cell in self.searchState.get('open', set()):
            return self.OPEN_COLOR
        if cell in self.blocked:
            return self.BLOCK_COLOR
        return self.GRID_BG

    def redrawGrid(self):
        self.canvas.delete('all')
        self.rects = {}
        for r in range(self.rows):
            for c in range(self.cols):
                cell = (r, c)
                rect = self.canvas.create_rectangle(
                    *self.cellCoords(r, c),
                    fill=self.cellColor(cell),
                    outline='gray80',
                    width=self.CELL_BORDER)
                self.rects[cell] = rect

        # Rebind every rectangle for click operations
        for cell, rect in self.rects.items():
            self.canvas.tag_bind(rect, '<Button-1>', self.onLeftClick)
            self.canvas.tag_bind(rect, '<Button-3>', self.onRightClick)
            self.canvas.tag_bind(rect, '<Shift-Button-1>', self.onShiftLeftClick)

    def repaintCells(self, cells):
        for cell in cells:
            rect = self.rects.get(cell)
            if rect:
                self.canvas.itemconfig(rect, fill=self.cellColor(cell))

    def repaintAll(self):
        self.repaintCells(self.rects.keys())

    def randomBlocks(self, blockProb=None):
        if blockProb is None:
            blockProb = self.blockProb
        self.blocked = set()
        for r in range(self.rows):
            for c in range(self.cols):
                cell = (r, c)
                if cell in (self.start, self.goal):
                    continue
                if random.random() < blockProb:
                    self.blocked.add(cell)

    def newGrid(self, randomize=True):
        self.clearSearchState()
        if randomize:
            self.randomBlocks()
        else:
            self.blocked = set()
        self.redrawGrid()
        self.setMessage(
            'Left click: toggle block | Shift+Left: set Start | Right click: set Goal | Run Solve A*')

    def clearPath(self):
        self.clearSearchState()
        self.repaintAll()
        self.setMessage('Cleared previous search path')

    def onLeftClick(self, event):
        cell = self.eventToCell(event)
        if not cell or cell in (self.start, self.goal):
            return
        if cell in self.blocked:
            self.blocked.remove(cell)
        else:
            self.blocked.add(cell)
        self.clearSearchState()
        self.repaintCells([cell])

    def onRightClick(self, event):
        cell = self.eventToCell(event)
        if not cell or cell == self.start or cell in self.blocked:
            return
        prev = self.goal
        self.goal = cell
        self.clearSearchState()
        self.repaintCells([prev, self.goal])

    def onShiftLeftClick(self, event):
        cell = self.eventToCell(event)
        if not cell or cell == self.goal or cell in self.blocked:
            return
        prev = self.start
        self.start = cell
        self.clearSearchState()
        self.repaintCells([prev, self.start])

    solveCode = '''
def solveAStar(self, start, goal):
   openHeap = [(h(start, goal), 0, start)]
   openSet = {start}
   cameFrom = {}
   gScore = {start: 0}
   while openHeap:
      current = heappop(openHeap)[2]
      if current == goal:
         return reconstruct(cameFrom, current)
      openSet.remove(current)
      for neighbor in neighbors(current):
         tentative = gScore[current] + 1
         if tentative < gScore.get(neighbor, inf):
            cameFrom[neighbor] = current
            gScore[neighbor] = tentative
            fScore = tentative + h(neighbor, goal)
            heappush(openHeap, (fScore, tentative, neighbor))
            openSet.add(neighbor)
   return None
'''

    def reconstructPath(self, cameFrom, current):
        path = [current]
        while current in cameFrom:
            current = cameFrom[current]
            path.append(current)
        path.reverse()
        return path

    def solveAStar(self, start=True, code=solveCode, wait=0.02):
        callEnviron = self.createCallEnvironment(
            code=code, startAnimations=start, sleepTime=wait / 4)
        self.clearSearchState()
        self.repaintAll()

        openHeap = []
        openSet = set([self.start])
        cameFrom = {}
        gScore = {self.start: 0}
        firstF = self.heuristic(self.start, self.goal)
        heapq.heappush(openHeap, (firstF, 0, self.start))

        self.searchState['open'] = set(openSet)
        self.highlightCode(
            'openHeap = [(h(start, goal), 0, start)]', callEnviron, wait=wait)
        self.highlightCode('openSet = {start}', callEnviron, wait=wait)
        self.highlightCode('gScore = {start: 0}', callEnviron, wait=wait)
        self.repaintAll()

        foundPath = None
        visitedOrder = 0
        while openHeap:
            self.highlightCode('while openHeap', callEnviron, wait=wait)

            _, _, current = heapq.heappop(openHeap)
            while current not in openSet and openHeap:
                _, _, current = heapq.heappop(openHeap)
            if current not in openSet:
                break

            self.highlightCode('current = heappop(openHeap)[2]', callEnviron,
                               wait=wait)
            openSet.remove(current)
            self.searchState['open'] = set(openSet)
            self.searchState['current'] = current
            self.searchState['closed'].add(current)
            self.repaintAll()
            self.wait(wait)

            self.highlightCode('current == goal', callEnviron, wait=wait)
            if current == self.goal:
                self.highlightCode(
                    'return reconstruct(cameFrom, current)', callEnviron, wait=wait)
                foundPath = self.reconstructPath(cameFrom, current)
                break

            self.highlightCode('for neighbor in neighbors(current)', callEnviron,
                               wait=wait)
            for neighbor in self.neighbors(current):
                self.highlightCode(
                    'tentative = gScore[current] + 1', callEnviron, wait=wait)
                tentative = gScore[current] + 1
                self.highlightCode(
                    'tentative < gScore.get(neighbor, inf)', callEnviron, wait=wait)
                if tentative < gScore.get(neighbor, math.inf):
                    self.highlightCode('cameFrom[neighbor] = current',
                                       callEnviron, wait=wait)
                    cameFrom[neighbor] = current
                    self.highlightCode('gScore[neighbor] = tentative',
                                       callEnviron, wait=wait)
                    gScore[neighbor] = tentative
                    self.highlightCode(
                        'fScore = tentative + h(neighbor, goal)',
                        callEnviron, wait=wait)
                    fScore = tentative + self.heuristic(neighbor, self.goal)
                    self.highlightCode(
                        'heappush(openHeap, (fScore, tentative, neighbor))',
                        callEnviron, wait=wait)
                    visitedOrder += 1
                    heapq.heappush(openHeap, (fScore, visitedOrder, neighbor))
                    self.highlightCode('openSet.add(neighbor)',
                                       callEnviron, wait=wait)
                    openSet.add(neighbor)
                    self.searchState['open'] = set(openSet)
                    self.repaintCells([neighbor])
                    self.wait(wait / 2)

        self.searchState['current'] = None
        if foundPath:
            self.searchState['path'] = set(foundPath)
            self.repaintAll()
            self.setMessage('Path found with {} steps'.format(max(0, len(foundPath) - 1)))
        else:
            self.repaintAll()
            self.highlightCode('return None', callEnviron, wait=wait)
            self.setMessage('No path found. Try reducing obstacles.')

        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 4)

    def clickNew(self):
        self.newGrid(randomize=True)

    def clickClearPath(self):
        self.clearPath()

    def clickClearBlocks(self):
        self.blocked = set()
        self.clearPath()
        self.repaintAll()
        self.setMessage('Cleared all blocked cells')

    def clickSolve(self):
        if self.start in self.blocked or self.goal in self.blocked:
            self.setMessage('Start/Goal cannot be blocked')
            return
        self.solveAStar(start=self.startMode())

    def makeButtons(self):
        self.addOperation('New Grid', lambda: self.clickNew(),
                          helpText='Create new random obstacle grid')
        self.addOperation('Clear Path', lambda: self.clickClearPath(),
                          helpText='Clear only search visualization state')
        self.addOperation('Clear Blocks', lambda: self.clickClearBlocks(),
                          helpText='Remove all obstacle cells')
        self.addOperation('Solve A*', lambda: self.clickSolve(),
                          helpText='Run A* search from start to goal')
        self.addAnimationButtons()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Visualize A* on a 2D grid',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-d', '--debug', default=False, action='store_true',
        help='Show debugging information.')
    parser.add_argument(
        '-s', '--seed', default=None,
        help='Seed the random generator with a string')
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)

    app = AStarGrid()
    app.DEBUG = args.debug
    app.runVisualization()
