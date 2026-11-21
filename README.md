# Metaphorical Logo

A Codex skill for engraved app icons. It pairs **one animal with one physical object** to express what the app does, then draws the pair in black ink and ivory on a vivid, rounded tile.

## Reference designs

<table>
  <thead>
    <tr>
      <th scope="col" align="center">Demet</th>
      <th scope="col" align="center">Blazon</th>
      <th scope="col" align="center">Zihin</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><img src="docs/reference-logos/demet.png" width="210" alt="Engraved monkey holding a bouquet on an amber tile"></td>
      <td align="center"><img src="docs/reference-logos/blazon.png" width="210" alt="Engraved chameleon gripping a folder on a coral tile"></td>
      <td align="center"><img src="docs/reference-logos/zihin.png" width="210" alt="Engraved squirrel holding a sheet of paper on a violet tile"></td>
    </tr>
    <tr>
      <td valign="top">A monkey gathers flowers into one bouquet.</td>
      <td valign="top">A chameleon holds a folder, evoking a change in its appearance.</td>
      <td valign="top">A squirrel saves a sheet of paper the way it stores something for later.</td>
    </tr>
  </tbody>
</table>

## How it works

1. **Compare three concepts.** Describe the app's main action. Codex explores different animal-and-object pairings and presents three original illustrations on a single A/B/C board, with 64, 32, and 16 px previews.
2. **Try backgrounds live.** Each concept opens with its own default color. Use suggested swatches, the color picker, or a HEX value to change each tile independently. Reset a concept to its default at any time. The panel runs locally and remembers the selected colors for that round.
3. **Choose and export.** Pick a concept in chat and approve the final design. The selected color carries through to the PNG sizes, Windows ICO, macOS ICNS when supported, and web favicon and PWA assets.

## Install in Codex

```sh
git clone https://github.com/bilikenes/metaphorical-logo-design-skill.git
```

Copy the repository's [`metaphorical-logo` folder](metaphorical-logo/) into your Codex skills directory, typically `~/.codex/skills/`. Invoke it with **`$metaphorical-logo`** and tell Codex what your app helps people do.

> Use `$metaphorical-logo` to design an icon for Trailmark. It records a hiker's route and helps them retrace it. Show three engraved concepts and open the background color panel.

Illustration requires an available image generator with transparency support. For the local panel, install Pillow with `python -m pip install "Pillow>=10"`. The [skill instructions](metaphorical-logo/SKILL.md) describe how to use the companion `engraved-logo-design` skill for the static board and production exports.

## Open an existing color round

Once a design round has a `round.json` and three transparent engraving layers, run this from the repository root and open the local URL printed by the script.

```sh
python metaphorical-logo/scripts/palette_panel.py serve --round path/to/round.json
```

See the [round manifest example](metaphorical-logo/SKILL.md#open-the-color-panel) and the [animal-and-object prompt template](metaphorical-logo/references/animal-object-concepts.md#image-prompt-template) for the input format.
