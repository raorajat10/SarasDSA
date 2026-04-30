# Module 5 Assignment: Visualization Framework Exploration (Week 1)

**Student:** Sara  
**Date:** April 30, 2026  
**Repository:** `metacomp/dsa-project`

## Section 1: Visualization Summary

### Selected Visualization
I selected **SimpleArraySort** from `PythonVisualizations/SimpleSorting.py`.

### How the visualization is implemented
The implementation uses a layered architecture:

1. `Visualization` (`Visualization.py`) manages the Tk canvas and animation primitives (`moveItemsBy`, `moveItemsTo`, `moveItemsOnCurve`).
2. `VisualizationApp` (`VisualizationApp.py`) adds the operations panel, argument entry, animation controls, and code-highlighting workflow (`createCallEnvironment`, `highlightCode`, `cleanUp`).
3. `SortingBase` (`SortingBase.py`) adds array-specific visual behavior such as array cell drawing, index arrows, swaps, and value-move animations.
4. `SimpleArraySort` (`SimpleSorting.py`) implements specific sorting algorithms and connects them to buttons.

### How the data structure and algorithm are represented
The array is represented as a Python list of visualized values:

```python
self.list = []  # list of drawnValue objects
```

Each `drawnValue` stores:
- `val`: logical numeric value
- `items`: canvas item IDs for the rectangle/text that render that value

This gives a direct model-to-visual mapping: when values are compared, moved, or swapped in code, the same steps are animated on screen.

### How step-by-step execution is shown
The visualization mirrors algorithm flow using three synchronized channels:

1. **Code panel highlighting** via `highlightCode(...)`.
2. **Pointer movement** (e.g., `inner`, `last`, `left`, `right`) via `createIndex(...)` and animated movement.
3. **Value movement** via `swap(...)` and assignment helpers.

For example, Bubble Sort in `SimpleArraySort`:
- highlights loop/condition lines,
- moves `inner` and `last` pointers,
- animates each swap when `self.__a[inner] > self.__a[inner+1]`.

This makes the algorithm trace visually equivalent to the actual control flow.

---

## Section 2: New Visualization Guidelines

### Step-by-step approach to implementing a new visualization

1. Create a new module under `PythonVisualizations`.
2. Choose the right base class:
- Extend `SortingBase` for array/sorting behavior.
- Extend `VisualizationApp` for other structures/algorithms.
3. Build initial state in `__init__` (model + initial drawing).
4. Add operations using `addOperation(...)` in `makeButtons(...)`.
5. For each algorithm operation:
- define a display code string,
- create a call environment with `createCallEnvironment(...)`,
- call `highlightCode(...)` at each decision point,
- animate updates to pointers/data values,
- finish with `cleanUp(...)`.
6. Ensure the class is discoverable by the launcher (`runVisualization()` entry in the module).
7. Optionally place it in a preferred menu group in `runAllVisualizationsMenu.py`.

### Key framework components to modify or extend
- `PythonVisualizations/<NewModule>.py` (main new code)
- `PythonVisualizations/runAllVisualizationsMenu.py` (optional menu grouping)
- `SortingBase.py` / `VisualizationApp.py` only if shared reusable behavior is needed

### Best practices
- Keep model state and canvas state synchronized.
- Highlight all key control points (loops, comparisons, updates).
- Keep temporary visuals in the call environment for automatic cleanup.
- Use clear operation labels and helpful error messages for invalid input.
- Prefer small reusable animation helpers over duplicate drawing logic.

---

## Section 3: Algorithm Augmentation

### Modification completed
I augmented `SimpleArraySort` by adding **Cocktail Sort** in `PythonVisualizations/SimpleSorting.py`.

Added elements:
- `cocktailSortCode` pseudocode string for code-panel display
- `cocktailSort(...)` method with full animation
- `"Cocktail Sort"` operation button in `makeButtons(...)`

### Code snippet (augmentation)

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

### How it changes the algorithm/visualization
Bubble Sort moves in one direction per pass. Cocktail Sort is a **bidirectional** variant:

1. Left-to-right pass pushes larger values right.
2. Right-to-left pass pushes smaller values left.
3. Active boundaries shrink from both ends (`left++`, `right--`).

Visualization impact:
- Students see two pass directions in one outer loop.
- New `left` and `right` pointers make boundary contraction explicit.
- Early exit (`if not swapped: break`) demonstrates optimization behavior.

This is a meaningful paradigm variation while staying fully inside the existing framework.

---

## Section 4 (Optional): Improvement Proposals

1. Add live counters for comparisons and swaps in the control panel.
2. Add side-by-side comparison mode for two sorting algorithms on identical data.
3. Add preset datasets (nearly sorted, reverse sorted, duplicates-heavy).
4. Add a run summary panel (time, comparisons, swaps, final status).
5. Improve large-array performance with adaptive frame skipping.

---

## Grading Coverage Checklist (50 + 5 bonus)

- **Visualization Implementation Summary (20):** Completed in Section 1.
- **New Visualization Guidelines (15):** Completed in Section 2.
- **Algorithm Augmentation & Explanation (15):** Completed in Section 3.
- **Bonus Improvement Suggestions (+5):** Completed in Section 4.

