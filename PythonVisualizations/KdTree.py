from tkinter import *
import random

try:
    from tkUtilities import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .tkUtilities import *
    from .VisualizationApp import *


def distance2(x0, y0, x1, y1):
    dx = x0 - x1
    dy = y0 - y1
    return dx * dx + dy * dy


class KDNode(object):
    def __init__(self, x, y, label, axis, bbox):
        self.x = x
        self.y = y
        self.label = label
        self.axis = axis  # 0 -> x split (vertical), 1 -> y split (horizontal)
        self.bbox = bbox  # (left, bottom, right, top) in user coordinates
        self.left = None
        self.right = None
        self.items = ()

    def __str__(self):
        return '<{} @ ({}, {}) axis={}>'.format(self.label, self.x, self.y, self.axis)


class KdTree(VisualizationApp):
    MAX_ARG_WIDTH = 5
    CIRCLE_RADIUS = 5
    ROOT_OUTLINE = 'yellow'
    POINT_COLOR = 'black'
    LABEL_COLOR = 'red'
    TEXT_FONT = ('Helvetica', -10)
    X_SPLIT_COLOR = 'SteelBlue4'
    Y_SPLIT_COLOR = 'dark green'
    POINT_REGION_COLOR = 'honeydew2'
    BUFFER_ZONE = (-30, -60, 60, 5)
    CROSSHAIR_SIZE = 15
    CROSSHAIR_COLOR = 'blue'
    CROSSHAIR_FONT = (VisualizationApp.VARIABLE_FONT[0], -10)

    def __init__(
            self, maxArgWidth=MAX_ARG_WIDTH,
            title="Kd-Tree - SarasAI - Introduction to Data Structures and Algorithms",
            pointRegion=None, **kwargs):
        super().__init__(title=title, maxArgWidth=maxArgWidth, **kwargs)
        if pointRegion is None:
            pointRegion = V((0, 0, 800, 400)) - V(self.BUFFER_ZONE)
        self.pointRegion = pointRegion
        self.showSplits = IntVar()
        self.showSplits.set(1)
        self.root = None
        self.makeButtons()
        self.new()

    def canvasCoords(self, userX, userY):
        dims = widgetDimensions(self.canvas)
        return (max(0, min(dims[0], self.pointRegion[0] + userX)),
                max(0, min(dims[1], self.pointRegion[3] - userY)))

    def userCoords(self, canvasX, canvasY):
        return canvasX - self.pointRegion[0], self.pointRegion[3] - canvasY

    def userBBox(self, canvasBBox):
        return (canvasBBox[0] - self.pointRegion[0],
                self.pointRegion[3] - canvasBBox[3],
                canvasBBox[2] - self.pointRegion[0],
                self.pointRegion[3] - canvasBBox[1])

    def canvasBBox(self, userBBox):
        return (self.pointRegion[0] + userBBox[0],
                self.pointRegion[3] - userBBox[3],
                self.pointRegion[0] + userBBox[2],
                self.pointRegion[3] - userBBox[1])

    def display(self):
        self.canvas.delete('all')
        self.pointRegionRectangle = self.canvas.create_rectangle(
            *self.pointRegion, fill=self.POINT_REGION_COLOR, width=0, outline='')
        self.canvas.tag_bind(self.pointRegionRectangle, '<Button>', self.setXY)
        self.canvas.tag_bind(self.pointRegionRectangle, '<Double-Button-1>',
                             self.createNode)
        for button in range(2, 4):
            self.canvas.tag_bind(
                self.pointRegionRectangle, '<Double-Button-{}>'.format(button),
                lambda ev: self.new())
        self.redrawTree()

    def iterNodes(self, node='__root__'):
        if node == '__root__':
            node = self.root
        if node is None:
            return
        yield node
        for child in self.iterNodes(node.left):
            yield child
        for child in self.iterNodes(node.right):
            yield child

    def redrawTree(self):
        self.canvas.delete('split')
        self.canvas.delete('point')
        self.canvas.delete('label')
        self.canvas.delete('root')
        if self.root is None:
            return
        for node in self.iterNodes():
            node.items = self.createPointItems(node, isRoot=(node is self.root))
        self.updateSplitDisplay()

    def nodeSplitCoords(self, node):
        bbox = node.bbox
        if node.axis == 0:
            x = self.canvasCoords(node.x, 0)[0]
            yTop = self.canvasCoords(0, bbox[3])[1]
            yBottom = self.canvasCoords(0, bbox[1])[1]
            return (x, yTop, x, yBottom)
        y = self.canvasCoords(0, node.y)[1]
        xLeft = self.canvasCoords(bbox[0], 0)[0]
        xRight = self.canvasCoords(bbox[2], 0)[0]
        return (xLeft, y, xRight, y)

    def createPointItems(self, node, isRoot=False):
        r = self.CIRCLE_RADIUS
        x, y = self.canvasCoords(node.x, node.y)
        splitColor = self.X_SPLIT_COLOR if node.axis == 0 else self.Y_SPLIT_COLOR
        splitLine = self.canvas.create_line(
            *self.nodeSplitCoords(node), fill=splitColor, width=2,
            tags=('split',))
        circle = self.canvas.create_oval(
            x - r, y - r, x + r, y + r, fill=self.POINT_COLOR,
            outline='', tags=('point',))
        label = self.canvas.create_text(
            x, y - r * 3, text=node.label, fill=self.LABEL_COLOR,
            font=self.TEXT_FONT, tags=('label',))
        self.canvas.tag_bind(
            circle, '<Button-1>',
            lambda e, n=node: self.setArguments(str(n.x), str(n.y), n.label))
        items = (splitLine, circle, label)
        if isRoot:
            ring = self.canvas.create_oval(
                x - r - 3, y - r - 3, x + r + 3, y + r + 3,
                outline=self.ROOT_OUTLINE, width=2, tags=('root',))
            self.canvas.tag_lower(ring, 'point')
            items += (ring,)
        return items

    def createLabeledArrow(self, nodeOrCoords, label, level=1, color=None):
        if color is None:
            color = self.VARIABLE_COLOR
        if isinstance(nodeOrCoords, KDNode):
            x, y = self.canvasCoords(nodeOrCoords.x, nodeOrCoords.y)
        else:
            x, y = self.canvasCoords(*nodeOrCoords)
        tip = (x, y - self.CIRCLE_RADIUS - 2)
        base = (x, tip[1] - abs(self.VARIABLE_FONT[1]) * level)
        arrow = self.canvas.create_line(
            base[0], base[1], tip[0], tip[1], arrow=LAST, fill=color)
        text = self.canvas.create_text(
            base[0], base[1], text=label, anchor=S, fill=color,
            font=self.VARIABLE_FONT)
        return arrow, text

    def crosshairCoords(self, x, y):
        cx, cy = self.canvasCoords(x, y)
        return ((cx, cy - self.CROSSHAIR_SIZE, cx, cy + self.CROSSHAIR_SIZE),
                (cx - self.CROSSHAIR_SIZE, cy, cx + self.CROSSHAIR_SIZE, cy),
                (cx, cy - self.CROSSHAIR_SIZE - 3),
                (cx - self.CROSSHAIR_SIZE - 3, cy))

    def createCrosshairItems(
            self, vertCoords, horizCoords, xCoords, yCoords,
            xLabel='x', yLabel='y'):
        vert = self.canvas.create_line(*vertCoords, fill=self.CROSSHAIR_COLOR, width=1)
        horiz = self.canvas.create_line(*horizCoords, fill=self.CROSSHAIR_COLOR, width=1)
        xText = self.canvas.create_text(
            *xCoords, text=xLabel, anchor=S, font=self.CROSSHAIR_FONT,
            fill=self.CROSSHAIR_COLOR)
        yText = self.canvas.create_text(
            *yCoords, text=yLabel, anchor=E, font=self.CROSSHAIR_FONT,
            fill=self.CROSSHAIR_COLOR)
        return vert, horiz, xText, yText

    insertCode = '''
def insert(self, x={x}, y={y}, label={label!r}):
   self.__root = self.__insert(self.__root, x, y, label, depth=0)
'''

    _insertCode = '''
def __insert(self, n={nVal}, x={x}, y={y}, label={label!r}, depth={depth}):
   if not n: return KDNode(x, y, label, depth % 2)
   if n.x == x and n.y == y:
      n.label = label
      return n
   axis = depth % 2
   if axis == 0:
      if x < n.x:
         n.left = self.__insert(n.left, x, y, label, depth + 1)
      else:
         n.right = self.__insert(n.right, x, y, label, depth + 1)
   else:
      if y < n.y:
         n.left = self.__insert(n.left, x, y, label, depth + 1)
      else:
         n.right = self.__insert(n.right, x, y, label, depth + 1)
   return n
'''

    def childBBox(self, parent, goLeft):
        l, b, r, t = parent.bbox
        if parent.axis == 0:
            return (l, b, parent.x, t) if goLeft else (parent.x, b, r, t)
        return (l, b, r, parent.y) if goLeft else (l, parent.y, r, t)

    def insert(self, x, y, label, start=True, code=insertCode, wait=0.08):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start,
            sleepTime=wait / 8)
        crosshair = self.createCrosshairItems(*self.crosshairCoords(x, y))
        callEnviron |= set(crosshair)
        self.highlightCode(
            'self.__root = self.__insert(self.__root, x, y, label, depth=0)',
            callEnviron)
        bbox = self.userBBox(self.pointRegion)
        self.root, created = self.__insert(self.root, x, y, label, 0, bbox, wait=wait)
        self.redrawTree()
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 8)
        return created

    def __insert(self, n, x, y, label, depth, bbox, code=_insertCode, wait=0.08):
        nVal = str(n)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 8)
        arrowTarget = n if n else (x, y)
        nArrow = self.createLabeledArrow(arrowTarget, 'n')
        callEnviron |= set(nArrow)

        self.highlightCode('not n', callEnviron, wait=wait)
        if not n:
            self.highlightCode('return KDNode(x, y, label, depth % 2)', callEnviron)
            node = KDNode(x, y, label, depth % 2, bbox)
            self.cleanUp(callEnviron, sleepTime=wait / 8)
            return node, True

        if (self.highlightCode('n.x == x', callEnviron, wait=wait, returnValue=n.x == x) and
                self.highlightCode('n.y == y', callEnviron, wait=wait, returnValue=n.y == y)):
            self.highlightCode('n.label = label', callEnviron, wait=wait)
            n.label = label
            self.highlightCode('return n', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 8)
            return n, False

        self.highlightCode('axis = depth % 2', callEnviron, wait=wait)
        axis = depth % 2
        if self.highlightCode('axis == 0', callEnviron, wait=wait, returnValue=axis == 0):
            if self.highlightCode('x < n.x', callEnviron, wait=wait, returnValue=x < n.x):
                self.highlightCode(
                    'n.left = self.__insert(n.left, x, y, label, depth + 1)',
                    callEnviron)
                colors = self.canvas.fadeItems(nArrow)
                left, created = self.__insert(
                    n.left, x, y, label, depth + 1, self.childBBox(n, True),
                    code=code, wait=wait)
                n.left = left
                self.canvas.restoreItems(nArrow, colors)
            else:
                self.highlightCode(
                    'n.right = self.__insert(n.right, x, y, label, depth + 1)',
                    callEnviron)
                colors = self.canvas.fadeItems(nArrow)
                right, created = self.__insert(
                    n.right, x, y, label, depth + 1, self.childBBox(n, False),
                    code=code, wait=wait)
                n.right = right
                self.canvas.restoreItems(nArrow, colors)
        else:
            if self.highlightCode('y < n.y', callEnviron, wait=wait, returnValue=y < n.y):
                self.highlightCode(
                    'n.left = self.__insert(n.left, x, y, label, depth + 1)',
                    callEnviron)
                colors = self.canvas.fadeItems(nArrow)
                left, created = self.__insert(
                    n.left, x, y, label, depth + 1, self.childBBox(n, True),
                    code=code, wait=wait)
                n.left = left
                self.canvas.restoreItems(nArrow, colors)
            else:
                self.highlightCode(
                    'n.right = self.__insert(n.right, x, y, label, depth + 1)',
                    callEnviron)
                colors = self.canvas.fadeItems(nArrow)
                right, created = self.__insert(
                    n.right, x, y, label, depth + 1, self.childBBox(n, False),
                    code=code, wait=wait)
                n.right = right
                self.canvas.restoreItems(nArrow, colors)

        self.highlightCode(('return n', 2), callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 8)
        return n, created

    findCode = '''
def findExact(self, x={x}, y={y}):
   return self.__findExact(self.__root, x, y, depth=0)
'''

    _findCode = '''
def __findExact(self, n={nVal}, x={x}, y={y}, depth={depth}):
   if not n: return None
   if n.x == x and n.y == y: return n
   axis = depth % 2
   if axis == 0:
      if x < n.x:
         return self.__findExact(n.left, x, y, depth + 1)
      return self.__findExact(n.right, x, y, depth + 1)
   if y < n.y:
      return self.__findExact(n.left, x, y, depth + 1)
   return self.__findExact(n.right, x, y, depth + 1)
'''

    def findExact(self, x, y, start=True, code=findCode, wait=0.08):
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), startAnimations=start,
            sleepTime=wait / 8)
        crosshair = self.createCrosshairItems(*self.crosshairCoords(x, y))
        callEnviron |= set(crosshair)
        self.highlightCode('return self.__findExact(self.__root, x, y, depth=0)',
                           callEnviron)
        result = self.__findExact(self.root, x, y, 0, wait=wait)
        self.highlightCode([], callEnviron)
        self.cleanUp(callEnviron, sleepTime=wait / 8)
        return result

    def __findExact(self, n, x, y, depth, code=_findCode, wait=0.08):
        nVal = str(n)
        callEnviron = self.createCallEnvironment(
            code=code.format(**locals()), sleepTime=wait / 8)
        nArrow = self.createLabeledArrow(n if n else (x, y), 'n')
        callEnviron |= set(nArrow)

        self.highlightCode('not n', callEnviron, wait=wait)
        if not n:
            self.highlightCode('return None', callEnviron)
            self.cleanUp(callEnviron, sleepTime=wait / 8)
            return None

        if (self.highlightCode('n.x == x', callEnviron, wait=wait, returnValue=n.x == x) and
                self.highlightCode('n.y == y', callEnviron, wait=wait, returnValue=n.y == y)):
            self.highlightCode('return n', callEnviron, wait=wait)
            self.cleanUp(callEnviron, sleepTime=wait / 8)
            return n

        self.highlightCode('axis = depth % 2', callEnviron, wait=wait)
        axis = depth % 2
        if self.highlightCode('axis == 0', callEnviron, wait=wait, returnValue=axis == 0):
            if self.highlightCode('x < n.x', callEnviron, wait=wait, returnValue=x < n.x):
                self.highlightCode(
                    'return self.__findExact(n.left, x, y, depth + 1)',
                    callEnviron)
                colors = self.canvas.fadeItems(nArrow)
                result = self.__findExact(n.left, x, y, depth + 1, code=code, wait=wait)
                self.canvas.restoreItems(nArrow, colors)
            else:
                self.highlightCode(
                    'return self.__findExact(n.right, x, y, depth + 1)',
                    callEnviron)
                colors = self.canvas.fadeItems(nArrow)
                result = self.__findExact(n.right, x, y, depth + 1, code=code, wait=wait)
                self.canvas.restoreItems(nArrow, colors)
        elif self.highlightCode('y < n.y', callEnviron, wait=wait, returnValue=y < n.y):
            self.highlightCode(
                'return self.__findExact(n.left, x, y, depth + 1)',
                callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            result = self.__findExact(n.left, x, y, depth + 1, code=code, wait=wait)
            self.canvas.restoreItems(nArrow, colors)
        else:
            self.highlightCode(
                'return self.__findExact(n.right, x, y, depth + 1)',
                callEnviron)
            colors = self.canvas.fadeItems(nArrow)
            result = self.__findExact(n.right, x, y, depth + 1, code=code, wait=wait)
            self.canvas.restoreItems(nArrow, colors)

        self.cleanUp(callEnviron, sleepTime=wait / 8)
        return result

    def new(self):
        self.root = None
        self.display()
        self.setMessage(
            'Created empty Kd-tree | Inputs: top box = X, middle box = Y, bottom box = Label (e.g., P1)')

    def randomFill(self, nPoints=1):
        gap = 5
        regionSize = V(BBoxSize(self.pointRegion)) - V((gap * 2, gap * 2))
        inserted = 0
        n = len(list(self.iterNodes()))
        for _ in range(nPoints):
            x = random.randrange(gap, gap + regionSize[0])
            y = random.randrange(gap, gap + regionSize[1])
            label = 'P{}'.format(n)
            while self.findLabel(label):
                n += 1
                label = 'P{}'.format(n)
            if self.findExact(x, y, start=False, code='', wait=0) is None:
                self.root, _ = self.__insert(
                    self.root, x, y, label, 0, self.userBBox(self.pointRegion),
                    code='', wait=0)
                inserted += 1
                n += 1
        self.redrawTree()
        return inserted

    def findLabel(self, label):
        for node in self.iterNodes():
            if node.label == label:
                return node
        return None

    def setXY(self, event):
        x, y = self.userCoords(event.x, event.y)
        self.setArguments(str(x), str(y), '')

    def createNode(self, event):
        self.recordModifierKeyState(event=event)
        x, y = self.userCoords(event.x, event.y)
        n = len(list(self.iterNodes())) if self.root else 0
        label = 'P{}'.format(n)
        while self.findLabel(label):
            n += 1
            label = 'P{}'.format(n)
        self.setArguments(str(x), str(y), label)
        self.insertButton.invoke()

    def validArgument(self, nArgs=3):
        x, y, label = [arg.strip() for arg in self.getArguments()]
        msg = ''
        bbox = self.userBBox(self.pointRegion)
        if nArgs == 1 and not x.isdigit():
            msg = 'Number of points must be an integer'
        if nArgs > 1 and not (x.isdigit() and y.isdigit() and BBoxContains(bbox, (int(x), int(y)))):
            msg = '({}, {}) is outside {}'.format(x, y, bbox)
            self.setArgumentHighlight(0, self.ERROR_HIGHLIGHT)
            self.setArgumentHighlight(1, self.ERROR_HIGHLIGHT)
        if nArgs > 2 and not (0 < len(label) <= self.maxArgWidth):
            if msg:
                msg += '\n'
            msg += 'Label must be between 1 and {} chars'.format(self.maxArgWidth)
            self.setArgumentHighlight(2, self.ERROR_HIGHLIGHT)
        if nArgs > 2 and (',' in label or ' ' in label):
            if msg:
                msg += '\n'
            msg += 'Label may not include commas or spaces'
            self.setArgumentHighlight(2, self.ERROR_HIGHLIGHT)
        return msg if msg else (x, y, label)

    def clickInsert(self):
        val = self.validArgument()
        if isinstance(val, tuple):
            x, y, label = val
            created = self.insert(int(x), int(y), label, start=self.startMode())
            self.setMessage('Point {} {}'.format(label, 'inserted' if created else 'updated'))
            self.clearArguments()
        else:
            self.setMessage(val)

    def clickFindExact(self):
        val = self.validArgument(nArgs=2)
        if isinstance(val, tuple):
            x, y, _ = val
            node = self.findExact(int(x), int(y), start=self.startMode())
            self.setMessage('Found {!r} at ({}, {})'.format(node.label, x, y)
                            if node else 'No point at ({}, {})'.format(x, y))
            self.clearArguments()
        else:
            self.setMessage(val)

    def clickRandomFill(self):
        val = self.validArgument(nArgs=1)
        if isinstance(val, tuple):
            nPoints, _, _ = val
            added = self.randomFill(int(nPoints))
            self.setMessage('Added {} point{}'.format(added, '' if added == 1 else 's'))
            self.clearArguments()
        else:
            self.setMessage(val)

    def updateSplitDisplay(self):
        self.canvas.itemConfig('split', state=NORMAL if self.showSplits.get() else HIDDEN)

    def makeButtons(self):
        vcmd = (self.window.register(makeFilterValidate(self.maxArgWidth)), '%P')
        self.insertButton = self.addOperation(
            'Insert', lambda: self.clickInsert(), numArguments=3,
            argHelpText=('X coordinate', 'Y coordinate', 'Label'),
            helpText='Insert/update a point in the Kd-tree', validationCmd=vcmd)
        self.findExactButton = self.addOperation(
            'Find Exact', lambda: self.clickFindExact(), numArguments=2,
            argHelpText=('X coordinate', 'Y coordinate'),
            helpText='Find point at exact coordinate', validationCmd=vcmd)
        self.randomFillButton = self.addOperation(
            'Random Fill', lambda: self.clickRandomFill(), numArguments=1,
            argHelpText=('# of points',),
            helpText='Insert N random points', validationCmd=vcmd)
        self.addOperation('New', lambda: self.new(), helpText='Create empty Kd-tree')
        self.showSplitsCheckbutton = self.addOperation(
            'Show Splits', lambda: self.updateSplitDisplay(),
            buttonType=Checkbutton, variable=self.showSplits,
            cleanUpBefore=False, mutex=False,
            helpText='Toggle display of Kd-tree split lines')
        self.addAnimationButtons()

    def enableButtons(self, enable=True):
        super().enableButtons(enable)
        widgetState(self.showSplitsCheckbutton, NORMAL)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Visualize basic Kd-tree operations',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-d', '--debug', default=False, action='store_true',
        help='Show debugging information.')
    parser.add_argument(
        '-r', '--random', default=None, type=int, metavar='N',
        help='Fill with N random points.')
    parser.add_argument(
        '-s', '--seed', default=None,
        help='Seed the random generator with a string')
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)

    kdtree = KdTree()
    kdtree.DEBUG = args.debug
    if args.random:
        kdtree.randomFill(args.random)
    kdtree.runVisualization()
