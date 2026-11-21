---
name: metaphorical-logo
description: Design engraved app logos and icons that pair exactly one animal with one physical object to express the application's function. Use for animal-and-object logo briefs, including requests for a gravür tarzında hayvan ve eşya logosu and interactive background-color previews.
---

# Metaphorical Logo

Speak the user's language. Deliver original illustrated app icons. Each icon contains exactly one recognizable animal and one identifiable physical object. Treat a bouquet or another naturally unified item as one object. The animal's characteristic behavior or ability and its physical interaction with the object together express the app's core action or benefit.

## Visual identity

- Use a square tile with generous rounded corners and one vivid, flat background color.
- Engrave both figures in black ink and ivory, with anatomically credible forms, fine directional hatching, and highlights shaped by the form. Keep all color in the tile.
- Build one readable silhouette with plausible contact and overlap. Keep the animal, the object, and their interaction recognizable when reduced to app-icon size.
- Keep the foreground to the pair. Exclude extra props, companions, scenery, text, and graphics. Use natural-history copperplate engraving with clean edges and avoid cartoon and 3D treatments.

For the shared visual reference and scripts, locate the installed `engraved-logo-design` skill by its `SKILL.md`, typically in the neighboring folder. Resolve its resource paths from that folder and keep project outputs in the user's workspace. Read its `references/visual-dna.md` for style. If the shared resources are unavailable, retain the workflow and use available equivalents for layout and export. Verify any replacement outputs and report any missing formats.

## Design

1. Identify the app's main action or benefit from the brief and any supplied materials. Read [the pairing examples and generation template](references/animal-object-concepts.md). Ask for a short description of the app's main task only when the available context does not establish it.
2. Explore at least nine pairings privately. For each one, map an app action to an animal trait, a physical object the user can connect to the app, and a visible interaction that makes the metaphor readable in one sentence. Select exactly three concepts with different silhouettes and interactions. Vary species and object by default. If the brief fixes one subject, vary the other subject and the composition. Exclude concepts whose animal could be swapped for any other animal without changing the idea.
3. Use an available image generator in transparent-background mode and the template to produce three separate square PNG engraving layers, preferably at least 1024 × 1024. Save them as `a-art.png`, `b-art.png`, and `c-art.png` in a fresh directory for this round. If image references are supported, use the shared skill's `references/approved-chameleon-folder.png` for engraving and tonal treatment. Give each pair distinct subject and composition instructions and include comfortable margins. Check true alpha and revise layers with baked backgrounds or missing ivory details. If illustration is unavailable, report the limitation and keep any written concepts clearly labeled as such.
4. Pick three visibly different default tile colors unless the brief specifies a shared brand color. Add several curated suggestions per concept and create the round manifest below. Render `a.png`, `b.png`, and `c.png` with the defaults. Inspect the masters at full size and at actual 64, 32, and 16 px. Revise and recheck anatomy, object count, contact, legibility, palette, and corner geometry. At 32 px the central pairing should read. At 16 px prioritize its signature silhouette.
5. Read the shared skill's `references/presentation-and-checkpoint.md` and create `concepts.png` with its board script. Launch the companion panel for the same three concepts so the user can edit each background.

   ```text
   python SCRIPT_PATH/concept_board.py a.png b.png c.png --names "Concept A" "Concept B" "Concept C" --notes "Rationale A" "Rationale B" "Rationale C" --title "Product icon concepts" --subtitle "Choose a direction to refine" --recommend 2 --corner-radius 0 --out concepts.png
   ```

6. Inspect and show exactly one static A/B/C board and share the verified local panel URL. Explain each pairing in one sentence, recommend one, and ask which to develop. Pause for the choice. Keep the panel available while the user reviews the options. Proceed straight to the kit only if the user explicitly asks to skip the checkpoint and deliver the full kit.

### Open the color panel

Save a UTF-8 `round.json` next to the three engraving layers. Localize the title, subtitle, names, and notes. The panel controls support Turkish (`tr`) and English (`en`). `recommend` is optional.

```json
{
  "title": "Product icon concepts",
  "subtitle": "Compare the three directions and try different tile colors.",
  "locale": "en",
  "recommend": "B",
  "concepts": {
    "A": {"name": "Concept A", "note": "Pairing rationale A.", "default": "#F49F20", "swatches": ["#E76F55", "#29B6A2", "#3298DB"]},
    "B": {"name": "Concept B", "note": "Pairing rationale B.", "default": "#29B6A2", "swatches": ["#347EC8", "#9875F6", "#F5AF35"]},
    "C": {"name": "Concept C", "note": "Pairing rationale C.", "default": "#9875F6", "swatches": ["#EA6F58", "#2AB7A9", "#E4A228"]}
  }
}
```

From the round directory, resolve `PANEL_SCRIPT` to this skill's `scripts/palette_panel.py`. It uses Python and Pillow, the same runtime as the board exporter. Render all three masters, replacing the letter and output name for B and C. Start the server in a retained background process, capture its printed loopback URL, and confirm the page serves before sharing it.

```text
python PANEL_SCRIPT render --round round.json --concept A --out a.png
python PANEL_SCRIPT serve --round round.json
```

The panel shows the same three concepts and size previews as the static board. Each column offers suggested swatches, a native color picker, an editable HEX value, and a reset to its own default. Changes save to `palette-state.json` in this round's directory. If a color is requested in chat, update that concept in the same state file and use the new color in the rendered preview. Reload an open panel to show a change made in chat. If the local server cannot run, keep the static board available and handle palette requests in chat.

## Refine and export

For a round with a color panel, start from the chosen transparent engraving layer and read its current saved color from `palette-state.json`, or its manifest default if no color was saved. Re-render the chosen letter to a new master at the selected color. The render command prints the exact HEX value to pass to the exporter. When asked to refine the drawing, preserve the chosen background and edit the transparent layer. Keep the agreed pairing and composition, and present material changes for approval before exporting. For a re-export, start with the existing approved master.

Read the shared skill's `references/export-guidelines.md`. Export from the highest-resolution approved master with the correct tile hex color. Use `--corner-mode keep` for a panel-rendered master, which already includes a rounded alpha mask. Choose the corner mode for other sources after inspecting their alpha. Use an approved micro-master only if needed to keep the same pairing readable at small sizes.

```text
python PANEL_SCRIPT render --round round.json --concept A --out approved.png
python SCRIPT_PATH/export_kit.py approved.png --name example-app --bg "#F49F20" --out-dir icon-kit --corner-mode keep --icns
python SCRIPT_PATH/verify_kit.py icon-kit
```

Check the PNG size ladder, Windows ICO, macOS ICNS when supported, and web favicon and PWA assets. Inspect the corner transparency and 16/32 px previews. Report unavailable formats or upscaling. Deliver links to the production files and describe generated raster assets as raster.
