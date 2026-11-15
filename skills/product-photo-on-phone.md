---
name: product-photo-on-phone
description: Shoot marketplace-ready product photos on a phone with a window, a sheet and two lamps, then cut, correct and export to each platform's exact image spec.
version: 1.0.0
license: MIT
tags: [photography, ecommerce, product, mobile, india]
---

# Product Photo On Phone

Marketplace listings live or die on the first image, and the first image is decided in about 0.3 seconds of scrolling. Sellers lose that second to grey photos shot at night under a ceiling bulb, with a shadow across the label and a 4:3 crop that the platform then letterboxes.

This skill builds a repeatable shoot with what a seller already owns - a phone, a window, a white sheet and two lamps - then cuts, corrects and exports to each platform's exact spec. The result is a consistent set where every product looks like it belongs to the same catalogue, which is what makes a small seller look established.

The rule that decides most of the quality: light the product, not the room. Everything else in this skill is downstream of that.

## When to use this skill

- You are listing 10-100 SKUs and cannot afford a studio per product.
- The marketplace rejected or suppressed images for background, size or text.
- Photos look different for every product, so the catalogue looks improvised.
- You need a lifestyle image and a clean white image from one session.
- **Do NOT use for:** shooting people or models, video, or copying a competitor's product photography wholesale - this ends at an exported image set per platform.

## Stage 1 - Set the light before you touch the product

One window on an overcast day is a better light source than any phone flash. Position the product so the light comes from the side, and put something white opposite to bounce it back.

1.1 Choose a window that gets indirect daylight - north-facing in the northern hemisphere - and shoot between 10 am and 4 pm.

1.2 Never use the phone flash. It flattens texture, creates a hard shadow and turns gloss into a white blob.

1.3 Put a white sheet or foam board opposite the window as a bounce, about 40-60 cm from the product, to fill the shadow side.

1.4 Diffuse direct sun with a white curtain or a sheet of tracing paper taped to the frame.

1.5 Kill mixed colour temperature: turn off ceiling lights and any lamp that is not the same colour as the daylight.

1.6 Test with one shot and check the shadow edge on the product's label - a hard edge means the light is too direct.

1.7 Lock exposure and white balance on the phone before shooting the set, so every frame in the batch matches.

Gate: one test frame has a soft shadow, a visible label and no colour cast, with exposure and white balance locked.

## Stage 2 - Build the table and the background

The background is a decision, not an accident. A sheet taped to a wall and swept onto a table gives an unbroken white with no horizon line, which is what marketplaces want.

2.1 Tape a white sheet to the wall and let it curve onto the table with no crease; the curve removes the horizon.

2.2 Iron or steam the sheet. A crease reads as a grey line in every frame and cannot be fixed cleanly later.

2.3 Keep 30 cm of empty background around the product on all sides so the crop has room.

2.4 Mark the product position with tape on the table so each SKU sits in the same spot.

2.5 Keep a spray bottle and a lint roller beside the table; dust on a black product is the most common reject reason after background.

2.6 Tape the phone to a stand or a stack of books at product height. Handheld at an angle is the second most common cause of distortion.

2.7 Put the table beside the window, not in front of it. Facing the window puts the light behind the product and turns the hero into a silhouette.

Gate: background is unbroken, crease-free and clean, and the phone is fixed at product height.

## Stage 3 - Compose the five frames every listing needs

A listing needs a set, not a photo. Five frames cover almost every marketplace requirement and every buyer question.

3.1 Hero frame: product centred, filling 80-85% of the frame, shot straight on at product height.

3.2 Second angle: 45 degrees from the front, showing depth and the top surface.

3.3 Detail frame: the label, the texture, the stitching or the port - whatever a buyer would want to touch.

3.4 Scale frame: the product beside a familiar object, or in a hand, so size is unambiguous.

3.5 In-use frame: the product doing its job, on a surface that belongs in the buyer's life.

3.6 Leave 10% of the frame as margin on the hero so a square crop does not clip the product.

3.7 Shoot each frame three times and keep all three until the edit; the sharpest frame is rarely the first.

| Frame | Purpose | Crop | Common mistake |
|---|---|---|---|
| Hero | Thumbnail and search result | 1:1 | Product touching the edges |
| 45 degree | Depth and form | 1:1 | Camera above the product looking down |
| Detail | Material and label | 1:1 or 4:5 | Out of focus at the edges |
| Scale | Size expectation | 1:1 | Object of unknown size |
| In use | Context | 4:5 | Cluttered background |

Gate: five frames per SKU, each with three takes, all at the same locked exposure.

## Stage 4 - Select and cut without destroying the product

Editing starts with selection, and the cut decides whether the product looks like an object or a sticker.

4.1 Cull to the sharpest frame per shot at 100% zoom, checking the label edge rather than the middle.

4.2 Crop to the platform's aspect ratio first, then correct the perspective so verticals are vertical.

4.3 Remove the background only when the platform requires pure white; a soft natural shadow under the product makes it sit rather than float.

4.4 Keep a 2-3% soft shadow under the product. A product with no shadow at all reads as pasted.

4.5 Clean dust and scratches with a clone tool at 100% zoom, working in small strokes.

4.6 Do not smooth texture. Buyers use texture to judge material quality and a smoothed product reads as plastic.

4.7 Save a layered master per SKU before any export, so a spec change does not mean a re-shoot.

Gate: five finished frames per SKU, sharp at 100%, with a natural shadow and no visible dust.

## Stage 5 - Correct colour against a known reference

Colour correction is a comparison, not a taste. Put something neutral in the frame and match it, or the red shirt will be orange on one platform and crimson on another.

5.1 Include a white card or a sheet of white paper in the first frame of each set, lit the same way as the product.

5.2 Use the white card to set white balance in the editor, then apply the same correction to the rest of the set.

5.3 Correct exposure so the white background reads about 245-250 in RGB, not 255 - pure 255 clips and hides texture.

5.4 Keep the product's own colour honest. A saturated boost makes the image pop in a grid and returns the item.

5.5 Check the shadow is neutral grey, not blue or yellow; a tinted shadow is the giveaway of a bad white balance.

5.6 Compare the edited frame with the physical product under daylight before exporting.

```bash
# batch white-balance and exposure check with ImageMagick
for f in shots/*.jpg; do
  convert "$f" -format "%f mean=%[fx:mean] max=%[fx:maxima]\n" info:
done
```

Gate: background reads 245-250, shadow is neutral, and the product colour matches the physical item under daylight.

## Stage 6 - Export to each platform's spec

Every platform has a size, ratio, format and file-size rule, and most reject or recompress anything outside it. Export per platform rather than uploading one file everywhere.

6.1 Export the hero at a minimum of 1600 px on the long edge; most marketplaces zoom only above that.

6.2 Use sRGB colour, JPEG at quality 85-90, and keep the file under 2 MB for fast loading.

6.3 Match the ratio the platform displays - square for grid-first marketplaces, 4:5 for feeds that crop vertically.

6.4 Strip EXIF location data before upload; a photo taken at home should not publish your address.

6.5 Name files `sku-frame.ext`, so a bulk upload maps to the right product without manual sorting.

6.6 Keep the layered master and the exported file in separate folders, so a re-export never overwrites the master.

6.7 Export a second, smaller thumbnail at 400 px for the catalogue grid. Platforms downscale badly, and a sharp 400 px file makes the grid look consistent.

```bash
mkdir -p export
for f in edited/*.jpg; do
  convert "$f" -resize 1600x1600^ -gravity center -extent 1600x1600 \
    -colorspace sRGB -strip -quality 88 "export/$(basename "$f")"
done
du -sh export
```

Gate: every exported file is at least 1600 px on the long edge, under 2 MB, sRGB and stripped of metadata.

## Stage 7 - Check the set as a grid, not as images

Buyers see the grid, not the individual photo. The grid is where inconsistency becomes visible.

7.1 Put all hero images in one folder and view them as thumbnails at 200 px.

7.2 Check that the product occupies a similar share of the frame in every image.

7.3 Check that the background white matches across the set; a grey one beside a white one looks like a different seller.

7.4 Check that no image has text, borders, watermarks or badges - most marketplaces prohibit them on the main image.

7.5 Fix the outliers by re-exporting that SKU, not by adjusting the whole set.

7.6 Check one image on a phone at 100% brightness and one on a laptop; the grid is judged on both.

Gate: the grid shows consistent framing, matching white and no prohibited overlays on any main image.

## Stage 8 - Publish, then measure which frame sells

The photo is a hypothesis until the listing has data. Measure it and iterate on the one that matters.

8.1 Publish the set and note the date of the change.

8.2 After 14 days, compare click-through rate on the new hero against the old one, if the platform reports it.

8.3 If clicks are flat, change the hero angle rather than the whole set - one variable at a time.

8.4 If clicks are good and conversion is poor, the problem is the detail, scale or in-use frame, not the hero.

8.5 Keep the previous set in an archive folder so a change can be reversed.

8.6 Record which frame was changed and what happened, in one line per SKU, so the pattern becomes visible.

Gate: every changed listing has a date, a metric and a recorded outcome after 14 days.

## Stage 9 - Make the process repeatable for the next 50 SKUs

The value of this skill is the second batch, shot in half the time with the same look.

9.1 Write a one-page shoot sheet: window, sheet, bounce position, phone height, exposure lock, five frames.

9.2 Batch SKUs by size and colour, and shoot in groups so the light and the settings never change mid-batch.

9.3 Keep a fixed naming and folder structure per batch: `raw/`, `edited/`, `export/`, `archive/`.

9.4 Time the first batch and write the minutes per SKU; use it to price your own listing work honestly.

9.5 Re-shoot only when the product changes materially - a new label or a new colour - not when the season changes.

9.6 Store the shoot sheet beside the images so anyone can reproduce the look without asking you.

Gate: a one-page shoot sheet exists, a batch folder structure is in use, and minutes per SKU are recorded.

## Quality checklist

- [ ] Every frame was shot in indirect daylight with the flash off.
- [ ] A bounce fills the shadow side in every frame.
- [ ] Exposure and white balance were locked before the set.
- [ ] The background is unbroken, crease-free and dust-free.
- [ ] The phone was fixed at product height, not handheld.
- [ ] Five frames exist per SKU: hero, 45 degree, detail, scale, in use.
- [ ] Three takes exist per frame before culling.
- [ ] The hero fills 80-85% of the frame with 10% margin.
- [ ] A soft shadow under the product is preserved.
- [ ] Background white reads 245-250, not 255.
- [ ] The product colour matches the physical item under daylight.
- [ ] Exports are at least 1600 px on the long edge and under 2 MB.
- [ ] EXIF metadata is stripped from every export.
- [ ] The grid view shows consistent framing and matching white.
- [ ] No main image carries text, borders or watermarks.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Product looks flat and plasticky | Phone flash used, killing texture and shadow | Turn the flash off and shoot with window light plus a bounce |
| Grey line across the background | A crease in the sheet, lit at a grazing angle | Iron the sheet and re-sweep the curve onto the table |
| Product looks pasted on white | Background removed with no shadow retained | Keep a 2-3% soft shadow and a slightly off-white background |
| Colour rejected by buyer as "not as shown" | Saturation boosted for the grid | Correct to the white card and compare with the item under daylight |
| Upload rejected for size | Exported at the phone's native crop, under 1600 px | Re-export at 1600 px long edge with a square extent |
| Grid looks like several sellers | Each SKU shot at a different distance and white balance | Lock settings, mark the floor position and batch by size |

## Copy-ready agent prompt

> Read the skill at the URL above and set up my product photo process. Ask me for the product type, the platforms I sell on and their current image specs, then give me the lighting and table setup, the five frames to shoot per SKU with the crop for each, the export commands for every platform, and a grid check I can run before uploading. Finish with the one-page shoot sheet and the batch folder structure. Do not suggest equipment I have to buy; work with a phone, a window, a sheet and two lamps.
