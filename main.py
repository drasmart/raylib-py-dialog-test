"""Raylib input dialog. Prints a single JSON object to stdout.

Usage: python main.py --prompt "Header text" [--default "initial text"]

Output:  {"status": "ok" | "cancel", "text": "<input>" | null, "prompt": "<header>"}
Exit code is 0 for ok, 1 for cancel, 2 for errors (error JSON still printed).
"""
import argparse
import json
import sys

import pyray as rl

WIDTH, HEIGHT = 520, 240
PAD = 20
FONT = 20


def wrap(text: str, max_width: int) -> list[str]:
    lines: list[str] = []
    for para in text.splitlines() or [""]:
        cur = ""
        for word in para.split(" "):
            trial = f"{cur} {word}".strip()
            if cur and rl.measure_text(trial, FONT) > max_width:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        lines.append(cur)
    return lines


def button(rect: rl.Rectangle, label: str) -> bool:
    hover = rl.check_collision_point_rec(rl.get_mouse_position(), rect)
    rl.draw_rectangle_rec(rect, rl.LIGHTGRAY if hover else rl.RAYWHITE)
    rl.draw_rectangle_lines_ex(rect, 1, rl.DARKGRAY)
    w = rl.measure_text(label, FONT)
    rl.draw_text(label, int(rect.x + (rect.width - w) / 2), int(rect.y + 10), FONT, rl.BLACK)
    return hover and rl.is_mouse_button_released(rl.MOUSE_BUTTON_LEFT)


def run_dialog(prompt: str, default: str) -> dict:
    rl.set_trace_log_level(rl.TraceLogLevel.LOG_NONE)  # raylib logs to stdout
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_TOPMOST)
    rl.init_window(WIDTH, HEIGHT, "Input")
    rl.set_exit_key(rl.KeyboardKey.KEY_NULL)  # we handle ESC ourselves
    rl.set_target_fps(60)

    text = default
    header = wrap(prompt, WIDTH - 2 * PAD)
    input_rect = rl.Rectangle(PAD, HEIGHT - 120, WIDTH - 2 * PAD, 36)
    ok_rect = rl.Rectangle(WIDTH - PAD - 220, HEIGHT - 60, 100, 38)
    cancel_rect = rl.Rectangle(WIDTH - PAD - 100, HEIGHT - 60, 100, 38)
    result = None

    while result is None and not rl.window_should_close():
        # --- input ---
        while (ch := rl.get_char_pressed()) != 0:
            if ch >= 32:
                text += chr(ch)
        if rl.is_key_pressed(rl.KeyboardKey.KEY_BACKSPACE) or rl.is_key_pressed_repeat(
            rl.KeyboardKey.KEY_BACKSPACE
        ):
            text = text[:-1]
        ctrl = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_CONTROL) or rl.is_key_down(
            rl.KeyboardKey.KEY_RIGHT_CONTROL
        )
        if ctrl and rl.is_key_pressed(rl.KeyboardKey.KEY_V):
            clip = rl.get_clipboard_text()
            if clip:
                text += clip.replace("\r", "").replace("\n", " ")

        # --- draw ---
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        for i, line in enumerate(header):
            rl.draw_text(line, PAD, PAD + i * (FONT + 4), FONT, rl.BLACK)

        rl.draw_rectangle_rec(input_rect, rl.WHITE)
        rl.draw_rectangle_lines_ex(input_rect, 2, rl.BLUE)
        max_w = int(input_rect.width) - 16
        shown = text
        while shown and rl.measure_text(shown, FONT) > max_w:
            shown = shown[1:]  # keep the tail visible while typing
        rl.draw_text(shown, int(input_rect.x) + 8, int(input_rect.y) + 8, FONT, rl.BLACK)
        if int(rl.get_time() * 2) % 2 == 0:
            cx = int(input_rect.x) + 8 + rl.measure_text(shown, FONT) + 1
            rl.draw_rectangle(cx, int(input_rect.y) + 6, 2, FONT + 2, rl.BLACK)

        ok_clicked = button(ok_rect, "OK")
        cancel_clicked = button(cancel_rect, "Cancel")
        rl.end_drawing()

        if ok_clicked or rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER) or rl.is_key_pressed(
            rl.KeyboardKey.KEY_KP_ENTER
        ):
            result = {"status": "ok", "text": text}
        elif cancel_clicked or rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
            result = {"status": "cancel", "text": None}

    rl.close_window()
    return result or {"status": "cancel", "text": None}  # window closed via X


def main() -> int:
    parser = argparse.ArgumentParser(description="Raylib input dialog returning JSON.")
    parser.add_argument("--prompt", default="Enter a value:", help="Header text")
    parser.add_argument("--default", default="", help="Initial input text")
    args = parser.parse_args()

    try:
        result = run_dialog(args.prompt, args.default)
    except Exception as exc:  # noqa: BLE001 - report any failure as JSON
        print(json.dumps({"status": "error", "error": str(exc), "prompt": args.prompt}))
        return 2

    result["prompt"] = args.prompt
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
