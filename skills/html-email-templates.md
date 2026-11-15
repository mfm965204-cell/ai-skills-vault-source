---
name: html-email-templates
description: Build one table-based email template that survives Outlook, Gmail and Apple Mail, with dark-mode rules, a plain-text part and an inbox test that catches the 6 failures that matter.
version: 1.0.0
license: MIT
tags: [frontend, email, html, templates, outlook, accessibility]
---

# HTML Email Templates

Web HTML and email HTML are different languages with the same syntax. Flexbox, grid, and external stylesheets are ignored by Outlook's Word rendering engine, and Gmail strips `<style>` from some clients entirely - so a template that looks perfect in a browser can arrive as an unstyled column of text.

This skill builds one email template that renders within 2-3 px across the 6 clients that matter, degrades to readable text without images, and has a plain-text part. You end with a 600 px table-based layout, inline styles, a dark-mode block and a test matrix.

## When to use this skill

- Your email looks fine in Gmail and broken in Outlook, or the reverse.
- Images are off and the email is a blank rectangle.
- Text is clipped at 60% on a phone because the layout was fixed at 700 px.
- A client asks for a template that their CRM can send without a designer.

Do NOT use for: sending infrastructure, deliverability and SPF/DKIM setup (a separate concern), or designing the campaign copy. This is the markup and its rendering behaviour.

## Stage 1 - Fix the layout constraints before writing markup

1.1 Design at 600 px wide. That is the safe content width across the major desktop clients and inside Outlook's reading pane.

1.2 Build on `<table>` with `role="presentation"`, `cellpadding="0"`, `cellspacing="0"` and `border="0"`. Tables are the only layout primitive that every client honours.

1.3 Use one column for anything that must not break, and nest a second table for the two-column rows. Nested tables beat `float` and beat `inline-block`.

1.4 Set `max-width: 600px` on the wrapper table and `width: 100%` so a phone scales down instead of scrolling.

| Constraint | Value | Why |
|---|---|---|
| content width | 600 px | Outlook pane and mobile scaling |
| body font size | 16 px minimum | iOS auto-zooms below 16 |
| line height | 1.5 | readability at 320 px |
| image max width | 600 px, `display:block` | avoids the 3 px inline gap |
| tap target | 44x44 px minimum | thumb accuracy |

Gate: the template has a 600 px wrapper, one column for critical content, and no `float` or `flex` anywhere.

## Stage 2 - Write markup that survives Word's renderer

2.1 Outlook 2007-2019 uses Microsoft Word's HTML engine: no flexbox, no grid, no `border-radius`, no `max-width` on divs, and unreliable padding on `<p>`.

2.2 Use `mso-` conditional comments only for the Outlook-specific fix, never for content. Content hidden in a conditional is invisible everywhere else.

2.3 Spacing goes on `<td>` padding, not on margin. Margin on a `<p>` collapses in Outlook and disappears in some Android clients.

2.4 Set `mso-line-height-rule: exactly` where line height must not be adjusted by Word.

```html
<!--[if mso]>
<table role="presentation" width="600" align="center"><tr><td>
<![endif]-->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="max-width:600px;margin:0 auto;background:#ffffff;">
  <tr>
    <td style="padding:24px 20px;font-family:Arial,Helvetica,sans-serif;
               font-size:16px;line-height:1.5;color:#1f2937;">
      Content goes here.
    </td>
  </tr>
</table>
<!--[if mso]>
</td></tr></table>
<![endif]-->
```

Gate: the template has zero flex, grid or float declarations, and every gap is a `td` padding.

## Stage 3 - Decide the CSS delivery strategy

3.1 Inline every visual style on the element. Gmail strips `<style>` in several contexts and the promotional tab behaves differently from the primary tab.

3.2 Keep a `<style>` block only for things that cannot be inlined: media queries, `:hover`, and dark-mode overrides.

3.3 Use a premailer or a build step (inline-css, juice) so authors write classes and the build inlines them. Hand-inlining 200 declarations is where typos live.

3.4 Keep total HTML under 100 KB. Gmail clips messages over 102 KB and the clip is silent.

| Style type | Where | Example |
|---|---|---|
| layout and colour | inline `style` | `padding`, `color`, `background` |
| responsive | `<style>` media query | `@media (max-width:600px)` |
| hover | `<style>` | button colour on hover |
| dark mode | `<style>` with media query | colour overrides |

Gate: the rendered HTML has zero external stylesheet links and every colour is present inline.

## Stage 4 - Make the mobile view a real view

4.1 One media query at `max-width: 600px` is enough. Stack the two-column rows, drop side padding to 16 px, and raise the font size to 17-18 px.

4.2 Buttons must be full width on mobile and at least 44 px tall. A 120 px wide text link is not a tap target.

4.3 Images at `width="100%"` with `height:auto` and `display:block`; never a fixed pixel width that overflows 320 px.

4.4 Test at 320 px, not 375 px. The narrowest common device is the one that breaks layouts.

```css
@media (max-width: 600px) {
  .stack { display: block !important; width: 100% !important; }
  .pad { padding-left: 16px !important; padding-right: 16px !important; }
  .btn a { display: block !important; width: 100% !important; padding: 16px 0 !important; }
  h1 { font-size: 22px !important; line-height: 1.3 !important; }
}
```

Gate: at 320 px there is no horizontal scroll and no text smaller than 14 px.

## Stage 5 - Handle dark mode without breaking light mode

5.1 Add `<meta name="color-scheme" content="light dark">` and `<meta name="supported-color-schemes" content="light dark">`.

5.2 Use `@media (prefers-color-scheme: dark)` to override the background, text and border colours. Clients that ignore it keep the light version, which is the safe default.

5.3 Avoid pure white text on pure black: use `#f3f4f6` on `#111827`. Pure contrast vibrates and looks broken on OLED.

5.4 Never invert images with CSS filters; supply a dark-safe asset or a transparent PNG with a light stroke.

5.5 Test the dark version with images blocked. That combination is where 80% of dark-mode bugs live.

Gate: the email is readable in light and dark, with images on and off.

## Stage 6 - Write the plain-text part

6.1 Every multipart email gets a `text/plain` alternative. Filters score a missing text part as a spam signal.

6.2 The text part carries the same information, the same links as bare URLs, and no image placeholders.

6.3 Keep lines under 78 characters and use a real blank line between paragraphs.

6.4 Do not send the HTML with tags stripped as the text part. That produces broken links and stray ` `.

```text
Hi Priya,

Your invoice INV-2026-1041 for Rs 24,500 is due on 30 Nov 2026.

Pay online: https://example.org/pay/1041
Questions: reply to this email.

Regards,
Accounts, Studio Nine
```

Gate: the text part is readable on its own, with every link present as a URL.

## Stage 7 - Make it work with images blocked

7.1 Set `alt` text on every image, and make the alt carry the message: `alt="Invoice total: Rs 24,500"`, not `alt="banner"`.

7.2 Give images explicit `width` and `height` attributes so the layout does not collapse when the image is blocked.

7.3 Never put essential copy inside an image. A text-as-image header fails for screen readers, blocked images and dark mode.

7.4 Style the `alt` text: colour and font-size on the `<img>` element so the fallback is legible.

Gate: with images blocked the email still communicates the offer, the price and the action.

## Stage 8 - Run the test matrix that matters

8.1 Six clients cover most of the failures: Outlook Windows, Outlook web, Gmail app on Android, Apple Mail on iOS, Gmail web, and one Android default client.

8.2 Check four things per client: layout at 600 px, stacking at 320 px, dark mode, images off.

8.3 Add the spam-score check: a seed-list test through a service, or at minimum a check of link count, image-to-text ratio and the presence of a text part.

8.4 Keep a screenshot of each client in the repo, dated. Regressions are visible in a diff, not in memory.

| Client | Known failure | Check |
|---|---|---|
| Outlook Windows | no radius, no flex, margin collapse | table padding, mso comments |
| Outlook web | strips some CSS | inline styles only |
| Gmail Android | strips `<style>` sometimes | critical styles inline |
| Apple Mail iOS | auto-links dates and addresses | wrap in a span if unwanted |
| Gmail web | clips over 102 KB | size check in CI |

Gate: 6 clients, 4 checks each, with dated screenshots stored.

## Stage 9 - Ship it with a build and a guard

9.1 Template source in one file with classes; build step inlines the CSS and emits the final HTML.

9.2 CI fails when the output exceeds 100 KB, when a `flex` or `grid` declaration appears, or when an `<img>` has no `alt`.

9.3 Version the template and keep the changelog short: what changed, which client it affected.

9.4 Give the sender a `{{variables}}` list with example values, so the copywriter never edits markup.

```bash
npx juice --preserveMediaQueries template.html dist/email.html
python3 - <<'PY'
import re, sys
h = open("dist/email.html").read()
assert len(h) < 100_000, f"too large: {len(h)} bytes"
assert not re.search(r"display:\s*(flex|grid)", h), "flex or grid in email"
assert len(re.findall(r"<img(?![^>]*\balt=)", h)) == 0, "image without alt"
print("email guards ok")
PY
```

Gate: all three guards pass and the built file is under 100 KB.

## Worked example

A monthly invoice email for a design studio, before and after.

| Item | Before | After |
|---|---|---|
| Layout | 720 px divs with flex | 600 px tables, nested |
| Outlook Windows | two columns collapsed | one column, stacked |
| Mobile 320 px | horizontal scroll | no scroll, 17 px text |
| Images blocked | blank rectangle | alt text carries the amount |
| Dark mode | white box on dark | overridden surfaces |
| Plain-text part | none | 6 lines with links |
| HTML size | 148 KB | 62 KB |
| Gmail clipping | clipped | not clipped |
| Client tests | Gmail web only | 6 clients, 4 checks |

The clip was the invisible one: at 148 KB Gmail cut the message at the footer and the unsubscribe link vanished, which is both a deliverability and a compliance problem.

## Quality checklist

- [ ] 600 px wrapper with `max-width` and `width: 100%`
- [ ] Tables with `role="presentation"`, zero border and zero cell spacing
- [ ] No flex, grid or float anywhere in the output
- [ ] All spacing on `td` padding, no margin on paragraphs
- [ ] Every visual style inlined, `<style>` only for media queries and hover
- [ ] No external stylesheet link
- [ ] Media query at 600 px stacks columns and drops padding to 16 px
- [ ] Buttons full width on mobile, at least 44 px tall
- [ ] Images `display:block`, `width:100%`, `height:auto`
- [ ] Dark-mode meta tags present and surfaces overridden
- [ ] Dark colours tested with images blocked
- [ ] Plain-text alternative with every link as a URL
- [ ] Alt text carries the message on every image
- [ ] Explicit width and height on images
- [ ] HTML under 100 KB, checked in CI
- [ ] 6 clients tested with dated screenshots

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Two columns collapse in Outlook | Flex or float used for layout | Nested tables, one column on narrow |
| Email unstyled in Gmail app | `<style>` stripped, styles not inline | Inline every visual declaration |
| Text clipped on a phone | Fixed width over 600 px, no viewport meta | 600 px max, media query at 600 |
| Gmail cuts the message | HTML over 102 KB | Trim markup, compress inlining, check in CI |
| Blank box when images are off | No alt text, fixed height | Alt text with the message, explicit sizes |
| White card on a dark background | No dark-mode overrides | `prefers-color-scheme` block plus meta tags |
| Spam score high | No text/plain part, image-heavy | Add the text part, raise text ratio |
| Padding disappears in Outlook | Margin on `<p>` | Move spacing to `td` padding |
| Rounded buttons square in Outlook | `border-radius` unsupported | Accept it, or use a VML roundrect |
| Links broken in the text part | Tags stripped to make the text version | Author the text part by hand |
| Dates auto-linked on iOS | Apple data detectors | Wrap in a styled span if unwanted |
| Template breaks after a copy edit | Markup edited by a copywriter | Variables list, markup owned by the build |

## Copy-ready agent prompt

> Read the skill at the URL above and build me one email template. Ask me: what the email is for, the brand colours, whether dark mode matters, and which clients my list actually uses. Then give me the full 600 px table-based HTML with `role="presentation"` tables, inline styles, the mso conditional wrapper, the 600 px media query that stacks columns and sets 44 px buttons, the dark-mode meta tags and override block, alt text that carries the message on every image, and a hand-written plain-text part with bare URLs. Finish with the build command that inlines CSS and the three CI guards for size, flex and missing alt, plus the 6-client, 4-check test matrix. Tell me the built file size and anything that will break in Outlook.
