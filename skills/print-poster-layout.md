---
name: print-poster-layout
description: Lay out a print poster that survives the press - correct bleed, a real grid, CMYK-safe colours and a proof you check at actual size before it goes to the printer.
version: 1.0.0
license: MIT
tags: [design, print, poster, layout, cmyk]
---

# Print Poster Layout

A screen file sent to a printer comes back with white edges, shifted trim, and a brand colour that reads dull because it was designed in RGB. Print has different failure modes than screens, and none of them are visible on a monitor at 40% zoom.

This skill sets the document up correctly first - size, bleed, margins, safe area - then builds a grid that survives trimming, converts colour with a proof, and checks type sizes at actual size. You end with a press-ready PDF, a checklist for the printer, and a proof you signed off at 100%.

## When to use this skill

- A poster, flyer or standee is going to a printer in the next 2 weeks.
- Your last print came back with a cropped headline or a white 3 mm edge.
- The brand orange looked brown in print and nobody knows why.
- You are designing in RGB and the printer asked for CMYK with bleed.

Do NOT use for: screen-only graphics, packaging die-lines, or large-format signage at 10 m viewing distance (different resolution and colour rules). It also does not replace the printer's own preflight report.

## Stage 1 - Set the document up before anything is drawn

1.1 Size: A3 is 297x420 mm, A2 is 420x594 mm, A1 is 594x841 mm. Choose the finished size, then add bleed - never the reverse.

1.2 Bleed: 3 mm on every side for standard offset, 5 mm for large format. Background art must extend into the bleed, not stop at the trim.

1.3 Safe area: keep all text and logos at least 5 mm inside the trim. A guillotine is accurate to about 1-2 mm, and nobody wants to bet a headline on it.

1.4 Colour mode: CMYK from the start. Converting an RGB document at the end shifts every saturated colour, and the shift is not reversible.

1.5 Resolution: 300 ppi at final size for images. A 200 ppi image is acceptable for a poster viewed at 1 m; 72 ppi is a web image and will look soft.

| Format | Trim (mm) | With 3 mm bleed | Safe margin |
|---|---|---|---|
| A3 | 297x420 | 303x426 | 5 mm |
| A2 | 420x594 | 426x600 | 5 mm |
| A1 | 594x841 | 600x847 | 5 mm |
| A4 flyer | 210x297 | 216x303 | 5 mm |

Gate: the document is the trim size plus bleed, in CMYK, with guides for trim and safe area visible.

## Stage 2 - Build a grid that can survive trimming

2.1 Choose 4, 6 or 12 columns. A 12-column grid divides into 2, 3, 4 and 6 without fractions, which is why it survives every layout change.

2.2 Set a gutter of 4-6 mm at A3 and scale it with the format. A 2 mm gutter disappears at 2 m viewing distance.

2.3 Set a baseline grid at 4 mm (roughly 11.3 pt) and align body text to it. Text that ignores the baseline reads as untidy without the viewer knowing why.

2.4 Keep a 5 mm inner margin on top of the safe area for the poster's own breathing room.

2.5 Place the headline first, at its final size, before any other element. Layout decisions made around a headline that later grows are the ones that break.

```text
A3 poster, 303x426 mm with bleed
  trim          297 x 420
  safe area     inset 5 mm  -> 287 x 410
  columns       12, gutter 5 mm, margin 10 mm
  baseline      4 mm
  headline      spans 8 of 12 columns
```

Gate: the grid is visible, and every element snaps to a column and to the baseline.

## Stage 3 - Set type sizes for viewing distance

3.1 Headline: 1 mm of cap height per 250 mm of viewing distance as a starting point, then adjust. A poster read at 2 m needs a cap height of about 8 mm, roughly 32 pt.

3.2 Body copy: 9-11 pt for a poster held in hand, 14-18 pt for one read at 2-3 m. Below 9 pt on a poster is decoration, not reading.

3.3 Minimum type on print is 6 pt, and never reverse out below 8 pt: thin white strokes on a dark field fill in on press.

3.4 Line length: 45-75 characters for body, and no more than 3 lines for a headline before it becomes a paragraph.

3.5 Convert all type to outlines only in the final PDF, and keep an editable copy with live text.

| Element | Hand-held (pt) | 2 m (pt) | 5 m (pt) |
|---|---|---|---|
| Headline | 24-36 | 40-72 | 96-160 |
| Sub-head | 14-18 | 22-30 | 40-60 |
| Body | 9-11 | 14-18 | 24-30 |
| Caption | 7-8 | 10-12 | 16-20 |

Gate: every text block passes the 6 pt minimum and the reverse-out rule.

## Stage 4 - Convert colour with a proof, not with hope

4.1 Ask the printer for their ICC profile or their standard (often FOGRA39 for coated stock in India). Convert to that profile, not to a generic CMYK.

4.2 Rich black for large areas: C40 M30 Y30 K100. Plain 100K black looks washed out on a large solid.

4.3 Body text in 100K only. Rich black on small type causes registration fringing.

4.4 Total ink coverage under 300-320% depending on stock. Above that, the sheet does not dry and the poster scuffs.

4.5 Any colour with a brand requirement needs a spot colour or a Pantone reference. CMYK will not match a screen brand colour, and pretending it will is how a rebrand argument starts.

| Colour use | Recipe | Note |
|---|---|---|
| large black area | C40 M30 Y30 K100 | rich black, 200% ink |
| body text | K100 only | avoids fringing |
| brand accent | spot or Pantone | CMYK will drift |
| pale background tint | 5-10% of one channel | below 5% may not print |

Gate: total ink coverage checked on the darkest area, and every brand colour has a defined reference.

## Stage 5 - Place images and logos correctly

5.1 Images at 300 ppi at placed size, linked, not embedded, so the printer can see them.

5.2 Logo as a vector, never as a PNG. A raster logo on a poster is visible at 1 m.

5.3 Logos sit inside the safe area with clear space of at least the height of the mark's counter.

5.4 Any full-bleed image extends 3 mm past the trim on every edge. A photo that stops at the trim shows a white hairline after cutting.

5.5 Keep the working file with linked images in one folder per job, so a re-export a year later does not fail on a missing asset.

Gate: no image below 200 ppi, no raster logo, no full-bleed element stopping at the trim.

## Stage 6 - Export the PDF the printer actually wants

6.1 Export PDF/X-4 when the printer accepts it: it carries the output intent and keeps transparency live. PDF/X-1a is the fallback for older workflows and flattens transparency.

6.2 Include 3 mm bleed in the export and enable crop marks and registration marks.

6.3 Embed or outline all fonts. A missing font substitutes silently and ruins the layout.

6.4 Downsample images to 300 ppi, not 72 and not 1200. Over-resolution makes a 400 MB file that the printer's RIP will reject.

6.5 Name the file with size, job and version: `poster-a3-autumn-v3-print.pdf`.

```bash
# preflight a PDF from the command line
gs -q -o /dev/null -sDEVICE=nullpage poster-a3-autumn-v3-print.pdf
pdfinfo poster-a3-autumn-v3-print.pdf | grep -E "Page size|File size"
pdffonts poster-a3-autumn-v3-print.pdf | awk 'NR>2 && $4=="no"{print "NOT EMBEDDED:", $1}'
```

Gate: the PDF reports the correct page size including bleed, all fonts embedded, and a file size under 100 MB.

## Stage 7 - Preflight before you send anything

7.1 Run the printer's preflight profile if they provide one; otherwise check the 8 items in the table below by hand.

7.2 Look at the file at 100% zoom, in four quadrants. Errors at 40% zoom are invisible.

7.3 Check the darkest and lightest areas on a printed proof, not on screen. A monitor cannot show 100K black or a 5% tint.

7.4 Ask for a hard-copy proof for any run over 100 pieces, or a digital proof at minimum for smaller runs.

| Check | Pass condition |
|---|---|
| page size | trim plus bleed exactly |
| bleed | art extends 3 mm past trim on all sides |
| resolution | 300 ppi at placed size |
| colour mode | CMYK with the correct output intent |
| ink coverage | under 320% total |
| fonts | all embedded or outlined |
| safe area | no text or logo within 5 mm of trim |
| marks | crop and registration marks present |

Gate: all 8 pass, and the printer's preflight reports no errors.

## Stage 8 - Handle the proof round in writing

8.1 Send the PDF with a one-line summary: size, stock, quantity, finish, and the date you need it.

8.2 Ask for their preflight report back in writing, before the plates are made.

8.3 On the proof, check: trim, colour of the brand element, small text legibility, and image sharpness in one 100% crop.

8.4 Approve in writing with the version name. "Looks fine" in a chat is not an approval and will not settle a dispute.

Gate: written preflight report and a written approval naming the file version.

## Stage 9 - Learn from what came back

9.1 Photograph the delivered poster next to the proof under the same light and compare.

9.2 Log the two differences that matter: colour drift and any trim shift.

9.3 Adjust the ink coverage and the tint floor for the next run on the same stock.

9.4 Keep the approved PDF and the printer's report in one folder per job. The next job on the same press starts from a known baseline.

9.5 Record the stock and the press in the note. The same file on a different stock is a different colour result, and the note only helps if it names both.

9.6 Keep a second copy of the approved PDF off the design machine, in the job folder your printer can also reach.

Gate: one photo comparison and a 3-line note per print job, kept with the artwork.

## Worked example

An A2 event poster, 500 copies, on 170 gsm matte.

| Item | First run | Second run |
|---|---|---|
| Document | A2 RGB, no bleed | A2 CMYK, 3 mm bleed |
| Trim result | 3 white edges | clean |
| Brand orange | dull brown | Pantone reference |
| Headline at 2 m | legible | legible, 8 mm cap height |
| Full-bleed photo | stopped at trim | extended 3 mm |
| Ink coverage | 340% in the dark band | 285% |
| Fonts | 1 substituted | all embedded |
| Proof | screen only | hard copy signed |

The white edges and the brown orange were both caused by the setup, not the design: no bleed and an RGB conversion done at export time.

## Quality checklist

- [ ] Document is trim size plus 3 mm bleed, in CMYK
- [ ] Safe area guides at 5 mm inside trim
- [ ] 12-column grid with a gutter scaled to the format
- [ ] Baseline grid set and body text aligned to it
- [ ] Headline placed at final size before anything else
- [ ] Type sizes chosen from viewing distance, 6 pt minimum
- [ ] No reverse-out type below 8 pt
- [ ] Correct ICC profile from the printer applied
- [ ] Rich black only on large areas, 100K on text
- [ ] Total ink coverage under 320%
- [ ] Brand colours defined as spot or Pantone
- [ ] Images at 300 ppi, linked, none below 200 ppi
- [ ] Logo is vector, inside the safe area
- [ ] Full-bleed elements extend past the trim
- [ ] PDF/X-4 with bleed, crop and registration marks
- [ ] All fonts embedded or outlined

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| White edge after trimming | Art stopped at the trim line | Extend background 3 mm into the bleed |
| Headline cropped | Text inside the trim, not the safe area | Keep text 5 mm inside trim |
| Brand colour looks brown | RGB converted to CMYK at export | Convert early with the printer's profile, use a Pantone |
| Large black area looks grey | 100K black used for a solid | Rich black C40 M30 Y30 K100 |
| Small text looks fuzzy | Rich black on thin type, registration shift | 100K only for text |
| Poster scuffs after handling | Ink coverage over 320% | Reduce total ink, check the darkest area |
| Font changed on press | Fonts not embedded | Embed or outline before export |
| Printer rejects the file | 1200 ppi images, 400 MB file | Downsample to 300 ppi at placed size |
| Tint disappears | Tint below 5% | Raise to 8-10% or use a different treatment |
| Proof approved verbally, then disputed | No written approval with a version | Written approval naming the file |
| Second run looks different from the first | Stock or press changed, note never recorded | Record stock and press per job |
| Print shop cannot find the file | Approved PDF only on a laptop | Store it in the shared job folder |

## Copy-ready agent prompt

> Read the skill at the URL above and set up a print-ready poster. Ask me: the finished size, the viewing distance, the printer's stock and ICC profile, the brand colours, and whether a spot colour is possible. Then give me the document setup with trim, 3 mm bleed and 5 mm safe area, a 12-column grid with gutter and baseline values for my format, a type scale for the viewing distance, the colour rules with rich black and ink coverage limits, the image and logo requirements, the exact PDF export settings including PDF/X-4 and marks, the 8-item preflight table, and the written proof-approval message. Tell me which of my current elements are outside the safe area or under 200 ppi.
