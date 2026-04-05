from dataclasses import dataclass
from pathlib import Path
from pygame import Vector2
from App.ui import UIScene, UIButton, UITextureButton, UILabel, UITexture
from App.asset_manager import AssetManager

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# Create Scene related Classes
@dataclass
class SceneLibrary:
    scenes: dict[str, UIScene]


# Set UI Data Path
DATA_ROOT = Path(__file__).resolve().parent.parent.joinpath("Data/UI")


def _parse_color(value, default=(255, 255, 255, 255)):
    if value is None:
        return default
    return tuple(value)


# Scenes Loader
def load_scenes(asset_manager: AssetManager) -> SceneLibrary:
    scene_library = SceneLibrary(scenes={})

    for file in DATA_ROOT.rglob("*.toml"):
        # Open the file
        with file.open("rb") as f:
            data = tomllib.load(f)

        # Extract Sections
        name_data = data.get("name")
        if name_data is None:  # Skip invalid names
            continue
        elements_data = data.get("elements", [])

        # Build UIScene
        scene = UIScene(name=name_data)

        # Loop through all the elements
        for e in elements_data:
            element_type = e.get("type")
            built_element = None

            if element_type == "button":
                font_key = e.get("text_font")
                font_path = asset_manager.get("fonts", font_key) if font_key else None

                built_element = UIButton(
                    rect=tuple(e["rect"]),
                    text=e.get("text", "Text Template"),
                    text_size=e.get("text_size", 24),
                    text_font=font_path,
                )
                built_element.text.color = _parse_color(e.get("text_color"))
                built_element.visible = e.get("visible", True)
                built_element.enabled = e.get("enabled", True)

            elif element_type == "texture_button":
                texture_key = e.get("texture")
                texture = asset_manager.get("textures", texture_key) if texture_key else None

                built_element = UITextureButton(
                    rect=tuple(e["rect"]),
                    texture=texture,
                    draw_background=e.get("draw_background", False),
                )
                built_element.visible = e.get("visible", True)
                built_element.enabled = e.get("enabled", True)

            elif element_type == "label":
                font_key = e.get("text_font")
                font_path = asset_manager.get("fonts", font_key) if font_key else None

                built_element = UILabel(
                    position=tuple(e.get("position", (0, 0))),
                    text=e.get("text", ""),
                    text_size=e.get("text_size", 24),
                    text_font=font_path,
                    draw_background=e.get("draw_background", False),
                )
                built_element.text.color = _parse_color(e.get("text_color"))
                built_element.visible = e.get("visible", True)
                built_element.enabled = e.get("enabled", True)

            elif element_type == "texture":
                texture_key = e.get("texture")
                texture = asset_manager.get("textures", texture_key) if texture_key else None

                built_element = UITexture(
                    texture=texture,
                    position=Vector2(e.get("position", (0, 0))),
                    anchor=e.get("anchor", "topleft"),
                )
                built_element.visible = e.get("visible", True)
                built_element.enabled = e.get("enabled", True)

            if built_element is not None:
                built_element.id = e.get("id")
                scene.elements.append(built_element)

        scene_library.scenes[name_data] = scene

    return scene_library