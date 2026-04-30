# Module 5 Assignment: Visualization Framework Exploration

Author: Sara  
Course Project Milestone: Module 5  
Date: April 30, 2026

## Setup and Run Notes

I used the provided project entry point `DatastructureVisualizations.py`, which launches a menu of available visualizations by scanning modules under `PythonVisualizations`.

Core startup path:

```python
# DatastructureVisualizations.py
runAllVisualizationsMenu.showVisualizations(
    runAllVisualizationsMenu.findVisualizations([dirname]))
```

Expected local run command:

```bash
python DatastructureVisualizations.py
```

## Section 1: Visualization Summary (Selected Visualization: `SimpleArraySort`)

### 1.1 How the visualization is implemented

The selected visualization is implemented as a layered class hierarchy:

1. `Visualization` provides the Tkinter canvas and low-level animation primitives such as `moveItemsBy`, `moveItemsTo`, and `moveItemsOnCurve`.
2. `VisualizationApp` adds the control panel, operation buttons, code window, animation controls, and code-highlighting lifecycle (`createCallEnvironment`, `highlightCode`, `cleanUp`).
3. `SortingBase` adds array-specific rendering and behaviors (array cells, index arrows, cell swaps, insertion/deletion helpers).
4. `SimpleArraySort` adds concrete algorithms (Bubble, Selection, Insertion, and now Cocktail sort).

Relevant framework anchors:

- `DatastructureVisualizations.py:19-27`
- `PythonVisualizations/allVisualizationsCommon.py` (`findVisualizations`, `findVisualizationClasses`)
- `PythonVisualizations/runAllVisualizationsMenu.py` (`showVisualizations`)
- `PythonVisualizations/Visualization.py` (`Animation`, canvas motion methods)
- `PythonVisualizations/VisualizationApp.py` (`addOperation`, `createCallEnvironment`, `highlightCode`)
- `PythonVisualizations/SortingBase.py` (`swap`, `createIndex`, `display`, `cleanUp`)
- `PythonVisualizations/SimpleSorting.py` (`SimpleArraySort` algorithms)

### 1.2 How the data structure and algorithm are represented

The underlying array is stored as:

```python
self.list = []  # list of drawnValue objects
```

Each `drawnValue` stores:

- a numeric key (`val`)
- canvas item IDs (`items`) for visual objects (rectangle and optional text)

So each logical element has both model state and visual state, which allows direct synchronization during each algorithm step.

Algorithm logic is represented in two parallel forms:

1. A code-string template (`bubbleSortCode`, `selectionSortCode`, etc.) shown in the code panel.
2. The actual executable method (`bubbleSort`, `selectionSort`, etc.) that performs comparisons/swaps and triggers animation/highlighting calls.

### 1.3 How the visualization reflects step-by-step execution

`SimpleArraySort.bubbleSort` demonstrates the standard pattern:

1. Call `createCallEnvironment(...)` to push a visual execution frame.
2. Create index arrows (`last`, `inner`) with `createIndex`.
3. Highlight each pseudocode fragment using `highlightCode(...)`.
4. Animate comparisons and swaps (`swap` uses curved motion for visual clarity).
5. Move indices after each iteration.
6. Call `cleanUp(...)` and restore final canonical positions.

This creates a one-to-one mapping between algorithm control flow and what the learner sees: loop entry, comparison checks, conditional swaps, and loop boundary updates.

## Section 2: New Visualization Guidelines

### 2.1 Step-by-step process for adding a new visualization program

1. Choose a base class:
- Use `SortingBase` for array/sorting behavior.
- Use `VisualizationApp` for a custom structure that needs control panel and code window.

2. Create a new module under `PythonVisualizations` and define a `VisualizationApp` subclass.

3. Implement constructor setup:
- initialize data model
- render initial state (`display`-style function)
- create operation buttons (`makeButtons`)

4. For each operation/algorithm:
- define a code-string snippet for display
- implement method logic with `createCallEnvironment`, `highlightCode`, and animation calls
- keep canvas artifacts inside the call environment so `cleanUp` can remove temporary visuals

5. Expose user actions in `makeButtons` using `addOperation(...)` and finish with animation controls (`addAnimationButtons`).

6. Ensure module is discoverable:
- include an executable block that calls `runVisualization()` for standalone mode
- optionally update menu grouping in `runAllVisualizationsMenu.py` (`PREFERRED_ARRANGEMENT`)

### 2.2 Key framework components to modify or extend

- `PythonVisualizations/<YourModule>.py` (new class and operations)
- optional: `PythonVisualizations/runAllVisualizationsMenu.py` for menu placement
- optional shared helpers in `SortingBase` or `VisualizationApp` if reusable behavior is needed

### 2.3 Best practices

- Keep model state (`self.list`, node arrays, etc.) and canvas state tightly synchronized.
- Reuse framework animation primitives instead of ad hoc direct coordinate edits.
- Highlight every meaningful decision point (loop conditions, comparisons, swaps/assignments).
- Use index arrows and short pauses so learners can track control flow.
- Add early-exit conditions where algorithmically meaningful to show optimization opportunities.
- Keep button labels and help text explicit and consistent.

## Section 3: Algorithm Augmentation

### 3.1 Modification performed

I augmented the existing `SimpleArraySort` visualization by adding **Cocktail Sort** (a bidirectional exchange sort) to `PythonVisualizations/SimpleSorting.py`.

Added items:

- `cocktailSortCode` (displayed pseudocode)
- `cocktailSort(...)` method (animated implementation)
- `"Cocktail Sort"` button in `makeButtons(...)`

### 3.2 Why this is a meaningful algorithmic variation

Bubble Sort only scans left-to-right per pass and pushes the largest element rightward.
Cocktail Sort scans in both directions:

1. Forward pass moves large elements right.
2. Backward pass moves small elements left.

This changes runtime behavior on partially sorted inputs and visually demonstrates bidirectional boundary tightening (`left` and `right` pointers), which is a distinct strategy from one-direction bubble passes.

### 3.3 Code excerpt of augmentation

```python
def cocktailSort(self):
   left = 0
   right = self.__nItems - 1
   swapped = True
   while swapped and left < right:
      swapped = False
      for inner in range(left, right):
         if self.__a[inner] > self.__a[inner+1]:
            self.swap(inner, inner+1)
            swapped = True
      right -= 1
      if not swapped:
         break
      swapped = False
      for inner in range(right, left, -1):
         if self.__a[inner-1] > self.__a[inner]:
            self.swap(inner-1, inner)
            swapped = True
      left += 1
```

The animation implementation mirrors this control flow with:

- three dynamic pointers (`left`, `right`, `inner`)
- dual-direction traversal animation
- comparison and swap highlighting
- early-exit visualization when no swaps occur

## Section 4 (Optional): Improvement Proposals

1. Add an operation logger panel that records each comparison/swap count in real time.
2. Add algorithm complexity overlays (current pass, comparisons, swaps, estimated Big-O context).
3. Add side-by-side mode to compare two algorithms on the same dataset.
4. Add preset datasets (nearly sorted, reverse sorted, duplicates-heavy) for controlled demonstrations.
5. Add exportable animation timeline snapshots for lecture notes/reporting.
6. Add unit-like invariant checks (e.g., `isSorted`) exposed in the UI after each algorithm run.
7. Improve scalability for larger arrays by adaptive frame skipping and batched canvas updates.

## Appendix: Files Used in This Analysis

- `DatastructureVisualizations.py`
- `PythonVisualizations/allVisualizationsCommon.py`
- `PythonVisualizations/runAllVisualizationsMenu.py`
- `PythonVisualizations/Visualization.py`
- `PythonVisualizations/VisualizationApp.py`
- `PythonVisualizations/SortingBase.py`
- `PythonVisualizations/SimpleSorting.py`
