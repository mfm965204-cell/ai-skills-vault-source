---
name: virtualized-data-table
description: Render a 100,000-row table that scrolls at 60 fps - windowing, fixed row heights, server-side sort and filter, and the profiling that proves it.
version: 1.0.0
license: MIT
tags: [frontend, performance, tables, react, virtualization]
---

# Virtualized Data Table

A table that renders every row is a table that dies at 5,000. The browser creates 5,000 DOM nodes, every keystroke in a filter re-renders all of them, and the tab locks for 2 seconds while the user decides the app is broken. The fix is not a faster machine; it is rendering 20 rows and pretending the other 99,980 exist.

This skill converts a naive table into a windowed one: fixed row height, a scroll container sized to the total, an overscan buffer, and sorting and filtering pushed to the server or to a worker so the main thread stays free. It ends with a profile that shows the frame time before and after, because "feels faster" is not a measurement.

The number that decides the design: rows on screen. If that is under 100, you need windowing; if it is 40,000, you need pagination and a different conversation with the product owner.

## When to use this skill

- A table with more than 2,000 rows freezes while scrolling or typing in a filter.
- The browser tab uses 800 MB and the fans spin.
- You need sticky headers, selection and inline editing on a large dataset.
- A report says "the dashboard is slow" and the table is the reason.
- **Do NOT use for:** chart rendering performance, general bundle-size work, or spreadsheet-style formulas - this covers one table component and its data flow.

## Stage 1 - Measure the table before changing it

Performance work without a baseline is guesswork, and guesswork produces a table that is fast on your laptop and slow on the user's phone.

1.1 Record the row count and the column count at the moment of the complaint.

1.2 Profile a 10-second scroll with the browser's performance panel and record the frame time and the longest task.

1.3 Record the DOM node count from the elements panel - above 5,000 nodes, layout cost dominates.

1.4 Record the memory footprint after 30 seconds of use, not at load.

1.5 Time one keystroke in the filter box, from keydown to painted result.

1.6 Write all five numbers down. They are the before column of the report.

| Metric | Before | Target |
|---|---|---|
| DOM nodes | 41,200 | under 2,000 |
| Longest task on scroll | 1,840 ms | under 50 ms |
| Filter keystroke to paint | 2,100 ms | under 100 ms |
| Memory after 30 s | 780 MB | under 150 MB |
| Frame time at 60 fps | 180 ms | under 16 ms |

Gate: five baseline numbers recorded, with the device and browser named.

## Stage 2 - Decide windowing, pagination or server-side paging

Not every large table should be virtualized. Choose by how the user actually reads the data, not by the row count alone.

2.1 If the user scrolls to scan and compare, virtualize: the scrollbar should represent the whole dataset.

2.2 If the user jumps to page 14, paginate: scrolling through 100,000 rows is not a workflow.

2.3 If the dataset exceeds 50,000 rows or the query is expensive, push sorting and filtering to the server and keep windowing on the client.

2.4 If the user needs totals and exports, compute them server-side; never sum 100,000 rows in the browser on every keystroke.

2.5 If rows have variable height, either fix the height or accept a measured-height virtualizer with a known cost.

2.6 Write the decision down with the row count that justified it.

| Dataset | Interaction | Choice |
|---|---|---|
| 500 rows | Scroll and edit | Plain table, no windowing |
| 8,000 rows | Scroll and filter | Client windowing, client filter |
| 120,000 rows | Scroll, sort, filter | Client windowing, server sort and filter |
| 2,000,000 rows | Search and jump | Server paging, 50 per page |

Gate: one of the three approaches is chosen, with the row count and the user's workflow written beside it.

## Stage 3 - Fix the row height and the scroll container

Windowing needs geometry it can compute. Fixed row height makes the maths trivial and the scrollbar honest.

3.1 Set an explicit row height in pixels, and enforce it with `box-sizing` and a single line of text or a clamped two lines.

3.2 Give the scroll container a fixed height, either viewport-based or a fixed pixel value, never `auto`.

3.3 Create an inner spacer with height `rows.length * rowHeight` so the scrollbar reflects the whole dataset.

3.4 Position the rendered window absolutely, or translate it by `scrollTop`, inside the spacer.

3.5 Listen to `scroll` passively and read `scrollTop` in a `requestAnimationFrame`, not in the event handler.

3.6 Keep the header outside the scrolling element so it does not repaint on every scroll frame.

```tsx
const ROW = 36;
const viewportRef = useRef<HTMLDivElement>(null);
const [start, setStart] = useState(0);
const visible = Math.ceil(600 / ROW) + 8; // viewport plus overscan

const onScroll = () => {
  requestAnimationFrame(() => {
    const top = viewportRef.current!.scrollTop;
    setStart(Math.max(0, Math.floor(top / ROW) - 4));
  });
};

return (
  <div ref={viewportRef} onScroll={onScroll} style={{ height: 600, overflow: "auto" }}>
    <div style={{ height: rows.length * ROW, position: "relative" }}>
      <div style={{ transform: `translateY(${start * ROW}px)` }}>
        {rows.slice(start, start + visible).map((r) => <Row key={r.id} row={r} />)}
      </div>
    </div>
  </div>
);
```

Gate: the scrollbar reaches the bottom of the dataset, and the visible row count stays under 40 at any scroll position.

## Stage 4 - Add overscan and handle the edges

Windowing artefacts are almost always edge cases: a blank flash at the top, a missing last row, a jump when the data changes.

4.1 Render 4-8 rows beyond the viewport on each side so fast scrolling does not show blank space.

4.2 Clamp the start index so the last page still fills the viewport instead of showing a short list.

4.3 Recompute the window when the container resizes, using a `ResizeObserver`, not a window `resize` listener.

4.4 Reset the scroll position when the filter changes, or the user sees an empty area of the new result set.

4.5 Keep row keys stable across sort and filter - use the record id, never the index.

4.6 Test with 0 rows, 1 row, and exactly one screenful; those three states break naive virtualizers.

Gate: no blank flash during a fast scroll, the last row is reachable, and the empty state renders without errors.

## Stage 5 - Move sorting and filtering off the render path

The window fixes rendering. The filter box is the other half, and a filter that re-sorts 100,000 rows per keystroke will still freeze the tab.

5.1 Debounce the filter input by 250-300 ms.

5.2 Push sort and filter to the server when the dataset is large, and send the window offset with the query.

5.3 If the filter stays client-side, run it in a web worker and post the result back.

5.4 Keep the sort comparator pure and avoid creating objects inside it; sort an array of indices when the records are large.

5.5 Cache the last result per query string so a repeated keystroke does not repeat the work.

5.6 Show a pending state that does not unmount the table, or the scroll position resets on every keystroke.

```ts
const worker = new Worker(new URL("./filter.worker.ts", import.meta.url));
worker.onmessage = (e) => setRows(e.data);

const onQuery = useMemo(
  () => debounce((q: string) => worker.postMessage({ q, rows: allRows }), 280),
  [allRows],
);
```

Gate: a keystroke in the filter paints in under 100 ms with 100,000 rows loaded.

## Stage 6 - Keep rows cheap and re-renders rare

A virtualized table with expensive rows is still slow: 20 rows that each re-render on every scroll frame will drop frames.

6.1 Wrap the row component in `React.memo` with a stable prop signature.

6.2 Pass primitives, not new object literals, to the row; an inline `style={{}}` creates a new object each render.

6.3 Hoist cell formatters and formatters' locale objects out of the render function.

6.4 Avoid inline arrow functions in props for the row; bind the handler once per row id.

6.5 Move per-row derived values into the row component, computed once, not in the parent's map.

6.6 Check with the profiler that a scroll frame re-renders only the rows entering the viewport.

Gate: a scroll frame re-renders at most the newly visible rows, confirmed in the profiler.

## Stage 7 - Handle selection, sticky columns and inline edit

Real tables need state that fights with windowing. Selection must survive scrolling; edit must not unmount.

7.1 Store selection as a `Set` of ids in the parent, never as row-local state, so a row can unmount and return selected.

7.2 Implement select-all as an explicit action over the whole dataset, and label it with the count it will affect.

7.3 Keep sticky columns outside the transform, positioned with `position: sticky` and a `left` or `inset-inline-start` value.

7.4 For inline edit, keep the editing row id in the parent and render the input only for that id.

7.5 Commit an edit on blur and on Enter, and revert on Escape; do not commit on every keystroke.

7.6 Test selection across a filter change: rows filtered out must keep their selection or be cleared explicitly.

Gate: selection survives scrolling and filtering, and an open editor does not lose focus when the window shifts.

## Stage 8 - Profile again and compare with the baseline

The only proof is the after column, measured the same way as the before column, on the same device.

8.1 Repeat the five measurements from Stage 1 on the same browser and device.

8.2 Confirm DOM nodes stay under 2,000 while scrolling the whole dataset.

8.3 Confirm the longest task during a fast scroll is under 50 ms.

8.4 Confirm memory after 30 seconds is under 150 MB.

8.5 Test on a mid-range Android phone, not only on the development machine.

8.6 Write both columns into the pull request, so the change is justified with numbers.

Gate: all five metrics improved and the two columns are recorded in the pull request.

## Stage 9 - Guard the table against regression

A table that is fast today gets slow again after three feature additions. Add the checks that catch it.

9.1 Add a test that renders 50,000 rows and asserts the DOM node count stays under 2,000.

9.2 Add a filter timing test with a generous ceiling, so CI fails on a real regression rather than on a slow runner.

9.3 Document the fixed row height as a constraint; changing it changes the virtualizer's maths.

9.4 Keep a fixture with 0, 1 and exactly one screenful of rows in the test suite.

9.5 Record the device used for the manual profile, so the next person compares like with like.

9.6 Review any new column for its cost: a column with a formatter or a computed value is a per-row cost multiplied by the window.

Gate: a DOM-node test and a filter-timing test exist in CI, and the row height is documented as a constraint.

## Quality checklist

- [ ] Baseline metrics are recorded before any change.
- [ ] The approach - windowing, pagination or server paging - is chosen with a written reason.
- [ ] Row height is a fixed pixel value enforced in CSS.
- [ ] The scroll container has an explicit height.
- [ ] A spacer element gives the scrollbar the full dataset height.
- [ ] Scroll position is read inside `requestAnimationFrame`.
- [ ] Overscan renders 4-8 rows beyond the viewport.
- [ ] The last row is reachable and the empty state renders.
- [ ] The filter is debounced by at least 250 ms.
- [ ] Sort and filter do not run on the render path.
- [ ] Row components are memoised with stable props.
- [ ] Selection is stored by id in the parent, not per row.
- [ ] An open inline editor survives a window shift.
- [ ] DOM nodes stay under 2,000 with 50,000 rows.
- [ ] A DOM-node test and a filter-timing test run in CI.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Blank space flashes while scrolling fast | Overscan too small for the scroll velocity | Render 4-8 rows beyond the viewport |
| Scrollbar jumps at the bottom | Spacer height not recalculated after filter | Recompute the spacer from the filtered row count |
| Filter still freezes the tab | Filtering and sorting on the main thread per keystroke | Debounce and move the work to a worker or the server |
| Selection lost after scrolling | Selection stored in row-local state | Keep a `Set` of ids in the parent |
| Rows re-render on every scroll frame | Inline object and arrow props on the row | Memoise the row and pass primitives |
| Table fast on desktop, slow on phone | Profile done on a fast machine | Re-measure on a mid-range Android device |

## Copy-ready agent prompt

> Read the skill at the URL above and make my data table fast. Ask me for the row and column counts, the framework and the current interaction - scroll, sort, filter, edit - then record the five baseline metrics before changing anything. Recommend windowing, pagination or server paging with a reason, give me the windowing implementation with fixed row height and overscan, move sort and filter off the render path, and show the memoisation changes for rows. Finish by re-profiling against the baseline and adding the CI tests that guard the DOM node count. Do not add a table library unless you can justify it against the row count.
