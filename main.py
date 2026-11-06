"""Raylib/raygui input dialog. Prints a single JSON object to stdout.

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
TEXT_CAPACITY = 1024  # bytes, including the NUL terminator


def style_gui() -> None:
    default = rl.GuiControl.DEFAULT
    rl.gui_set_style(default, rl.GuiDefaultProperty.TEXT_SIZE, FONT)
    rl.gui_set_style(default, rl.GuiDefaultProperty.TEXT_SPACING, 2)
    rl.gui_set_style(default, rl.GuiDefaultProperty.TEXT_LINE_SPACING, 4)  # added to TEXT_SIZE
    rl.gui_set_style(default, rl.GuiDefaultProperty.TEXT_ALIGNMENT_VERTICAL, rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP)


def run_dialog(prompt: str, default: str) -> dict:
    rl.set_trace_log_level(rl.TraceLogLevel.LOG_NONE)  # raylib logs to stdout
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_TOPMOST)
    rl.init_window(WIDTH, HEIGHT, "Input")
    rl.set_exit_key(rl.KeyboardKey.KEY_NULL)  # we handle ESC ourselves
    rl.set_target_fps(60)
    style_gui()

    buf = rl.ffi.new("char[]", TEXT_CAPACITY)
    init = default.encode("utf-8")[: TEXT_CAPACITY - 1]
    rl.ffi.memmove(buf, init, len(init))

    label_rect = rl.Rectangle(PAD, PAD, WIDTH - 2 * PAD, HEIGHT - 120 - 2 * PAD)
    input_rect = rl.Rectangle(PAD, HEIGHT - 120, WIDTH - 2 * PAD, 36)
    ok_rect = rl.Rectangle(WIDTH - PAD - 220, HEIGHT - 60, 100, 38)
    cancel_rect = rl.Rectangle(WIDTH - PAD - 100, HEIGHT - 60, 100, 38)
    bg_style = rl.gui_get_style(rl.GuiControl.DEFAULT, rl.GuiDefaultProperty.BACKGROUND_COLOR)
    bg = rl.get_color(bg_style & 0xFFFFFFFF)  # style ints are signed
    edit_mode = True
    result = None

    while result is None and not rl.window_should_close():
        enter = rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER) or rl.is_key_pressed(rl.KeyboardKey.KEY_KP_ENTER)
        escape = rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE)

        rl.begin_drawing()
        rl.clear_background(bg)
        # Word wrap only for the label: wrapping on the text box breaks typing.
        rl.gui_set_style(rl.GuiControl.DEFAULT, rl.GuiDefaultProperty.TEXT_WRAP_MODE, rl.GuiTextWrapMode.TEXT_WRAP_WORD)
        rl.gui_label(label_rect, prompt)
        rl.gui_set_style(rl.GuiControl.DEFAULT, rl.GuiDefaultProperty.TEXT_WRAP_MODE, rl.GuiTextWrapMode.TEXT_WRAP_NONE)
        # Returns 1 when edit mode should toggle (Enter, or click inside/outside).
        if rl.gui_text_box(input_rect, buf, TEXT_CAPACITY, edit_mode) and not enter:
            edit_mode = not edit_mode
        ok_clicked = rl.gui_button(ok_rect, "OK")
        cancel_clicked = rl.gui_button(cancel_rect, "Cancel")
        rl.end_drawing()

        if ok_clicked or enter:
            result = {"status": "ok", "text": rl.ffi.string(buf).decode("utf-8", "replace")}
        elif cancel_clicked or escape:
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
