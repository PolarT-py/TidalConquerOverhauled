from dataclasses import dataclass
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# Create Classes

@dataclass
class MainSettings:
    window_size: tuple[int, int]
    window_title: str
    window_bg_color: tuple[int, int, int]
    fps: int

@dataclass
class AudioSettings:
    master: float

@dataclass
class Settings:
    main: MainSettings
    audio: AudioSettings


# Set Paths

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILE = PROJECT_ROOT / "settings.toml"


# Settings Loader
def load_settings() -> Settings:
    # Check if the file exists
    if not SETTINGS_FILE.exists():
        raise FileNotFoundError(f"Settings file not found: {SETTINGS_FILE}")
        # Future: Add auto create settings if not found (Copy a file)

    # Open settings file
    with SETTINGS_FILE.open("rb") as f:
        data = tomllib.load(f)

    # Extract Sections
    main_data = data.get("main", {})
    audio_data = data.get("audio", {})

    # Build dataclasses
    main = MainSettings(
        window_size=main_data["window_size"],
        window_title=main_data["window_title"],
        window_bg_color=main_data["window_bg_color"],
        fps=main_data["fps"],
    )
    audio = AudioSettings(
        master=audio_data["master"]
    )

    return Settings(main=main, audio=audio)


# Settings Saver
def save_settings(settings: Settings) -> None:
    # Make structure
    data = {
        "main": {
            "window_size": list(settings.main.window_size),
            "window_title": settings.main.window_title,
            "window_bg_color": list(settings.main.window_bg_color),
            "fps": settings.main.fps,
        },
        "audio": {
            "master": settings.audio.master,
        },
    }
    lines = []

    # Add [main]
    lines.append("[main]")
    lines.append(f"window_size = {data['main']['window_size']}")
    lines.append(f'window_title = "{data["main"]["window_title"]}"')
    lines.append(f'window_bg_color = {data["main"]["window_bg_color"]}')
    lines.append(f"fps = {data['main']['fps']}")
    lines.append("")

    # Add [audio]
    lines.append("[audio]")
    lines.append(f"master = {data['audio']['master']}")
    lines.append("")

    SETTINGS_FILE.write_text("\n".join(lines), encoding="utf-8")
