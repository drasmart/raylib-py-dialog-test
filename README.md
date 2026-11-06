# raylib-py-dialog-test

Raylib input dialog (text field, OK, Cancel) that returns structured JSON.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Use

```powershell
.\ask-user.ps1 "What is your name?"
```

Output (stdout, one line):

```json
{"status": "ok", "text": "Ada", "prompt": "What is your name?"}
```

`status` is `ok`, `cancel` (text is `null`), or `error` (with `error` message).
Exit code: 0 ok, 1 cancel, 2 error. Enter = OK, Esc = Cancel.
