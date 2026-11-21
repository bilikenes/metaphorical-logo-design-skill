"""Serve an icon comparison round locally and render a chosen background."""

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from threading import Lock

from PIL import Image, ImageDraw


LETTERS = ("A", "B", "C")
CORNER_RADIUS = 0.225
PAGE = Path(__file__).resolve().parents[1] / "assets" / "palette-panel.html"


def normalize_color(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("Expected a color in #RRGGBB format.")
    return value.upper()


def load_art(path):
    with Image.open(path) as source:
        if source.format != "PNG" or source.width != source.height:
            raise ValueError(f"{path.name} must be a square PNG.")
        art = source.convert("RGBA")
    alpha_min, alpha_max = art.getchannel("A").getextrema()
    corners = [(0, 0), (art.width - 1, 0), (0, art.height - 1), (art.width - 1, art.height - 1)]
    if alpha_min != 0 or alpha_max == 0 or any(art.getpixel(point)[3] != 0 for point in corners):
        raise ValueError(f"{path.name} needs a visible engraving on a transparent background.")
    return art


def render_master(art, color):
    tile = Image.new("RGBA", art.size, normalize_color(color))
    tile.alpha_composite(art)
    width = art.width * 4
    mask = Image.new("L", (width, width), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, width - 1, width - 1), radius=round(width * CORNER_RADIUS), fill=255
    )
    tile.putalpha(mask.resize(art.size, Image.Resampling.LANCZOS))
    return tile


class Round:
    def __init__(self, manifest_path):
        self.directory = manifest_path.resolve().parent
        self.state_path = self.directory / "palette-state.json"
        self.lock = Lock()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.title = manifest["title"]
        self.subtitle = manifest.get("subtitle", "")
        self.locale = manifest.get("locale", "en")
        self.recommend = manifest.get("recommend")
        concepts = manifest["concepts"]
        if set(concepts) != set(LETTERS):
            raise ValueError("List exactly three concepts named A, B and C.")
        self.concepts = {letter: concepts[letter] for letter in LETTERS}
        if self.recommend is not None and self.recommend not in LETTERS:
            raise ValueError("The recommendation must be A, B or C.")
        for letter, concept in self.concepts.items():
            concept["default"] = normalize_color(concept["default"])
            concept["swatches"] = list(dict.fromkeys(
                [concept["default"], *(normalize_color(color) for color in concept["swatches"])]
            ))
            if not all(isinstance(concept[key], str) for key in ("name", "note")):
                raise ValueError(f"Concept {letter} needs a name and note.")

    def art_path(self, letter):
        return self.directory / f"{letter.lower()}-art.png"

    def colors(self):
        try:
            saved = json.loads(self.state_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            saved = {}
        return {
            letter: normalize_color(saved.get(letter, concept["default"]))
            for letter, concept in self.concepts.items()
        }

    def set_color(self, letter, color):
        chosen = normalize_color(color)
        with self.lock:
            colors = self.colors()
            colors[letter] = chosen
            temporary = NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.directory, delete=False
            )
            pending = Path(temporary.name)
            try:
                with temporary:
                    json.dump(colors, temporary, indent=2)
                    temporary.write("\n")
                os.replace(pending, self.state_path)
            finally:
                pending.unlink(missing_ok=True)
        return chosen

    def page_data(self):
        with self.lock:
            colors = self.colors()
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "locale": self.locale,
            "recommend": self.recommend,
            "cornerRadius": CORNER_RADIUS,
            "concepts": self.concepts,
            "colors": colors,
        }


def serve(round_data, port):
    for letter in LETTERS:
        load_art(round_data.art_path(letter))
    page = PAGE.read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def reply(self, body, content_type, status=200):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, data, status=200):
            self.reply(json.dumps(data, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8", status)

        def valid_host(self):
            if self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}":
                return True
            self.send_error(403)
            return False

        def do_GET(self):
            if not self.valid_host():
                return
            if self.path == "/":
                self.reply(page, "text/html; charset=utf-8")
            elif self.path == "/round":
                self.send_json(round_data.page_data())
            elif self.path in {f"/art/{letter}" for letter in LETTERS}:
                self.reply(round_data.art_path(self.path[-1]).read_bytes(), "image/png")
            else:
                self.send_error(404)

        def do_POST(self):
            if not self.valid_host():
                return
            if self.path != "/colors":
                self.send_error(404)
                return
            expected_origin = f"http://127.0.0.1:{self.server.server_port}"
            if (self.headers.get("Origin") != expected_origin
                    or self.headers.get_content_type() != "application/json"):
                self.send_error(403)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 256:
                    raise ValueError("Invalid selection payload.")
                data = json.loads(self.rfile.read(length))
                letter = data["concept"]
                if letter not in LETTERS:
                    raise ValueError("Invalid concept.")
                color = round_data.set_color(letter, data["color"])
            except (KeyError, TypeError, ValueError) as error:
                self.send_json({"error": str(error)}, 400)
                return
            except OSError:
                self.send_json({"error": "Could not save the palette."}, 500)
                return
            self.send_json({"color": color})

    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        print(f"http://127.0.0.1:{server.server_port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preview = commands.add_parser("serve")
    preview.add_argument("--round", type=Path, required=True)
    preview.add_argument("--port", type=int, default=0)
    render = commands.add_parser("render")
    render.add_argument("--round", type=Path, required=True)
    render.add_argument("--concept", choices=LETTERS, required=True)
    render.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        round_data = Round(args.round)
        if args.command == "serve":
            serve(round_data, args.port)
            return
        inputs = [args.round, round_data.state_path, *(round_data.art_path(letter) for letter in LETTERS)]
        if args.out.resolve() in {path.resolve() for path in inputs}:
            raise ValueError("Choose an output file separate from the round inputs.")
        art = load_art(round_data.art_path(args.concept))
        chosen = round_data.colors()[args.concept]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        render_master(art, chosen).save(args.out, format="PNG")
        print(chosen)
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
