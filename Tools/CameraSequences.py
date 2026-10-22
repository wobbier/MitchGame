"""Reusable authored camera sequence data for the primitive demo and Lost Temple generator."""
import math
import json


def as_asset(sequence, asset_path, target_names):
    """Split clip data from scene-specific binding identities and playback settings."""
    slots = {}
    used = set()
    camera = next(t["Target"] for t in sequence["Tracks"] if t["Component"] == "Camera")
    tracks = []
    for source in sequence["Tracks"]:
        target = source["Target"]
        if target not in slots:
            base = "Camera" if target == camera else target_names.get(target, "Target")
            slot, suffix = base, 2
            while slot in used:
                slot, suffix = f"{base} {suffix}", suffix + 1
            used.add(slot)
            slots[target] = slot
        track = {k: v for k, v in source.items() if k != "Target"}
        track["Binding"] = slots[target]
        tracks.append(track)
    asset = {"Version": 1, "Name": sequence["Name"], "FrameRate": sequence["FrameRate"],
             "DurationFrames": sequence["DurationFrames"], "Tracks": tracks}
    player = {"Type": "Sequence", "Clip": asset_path,
              "Clips": [{"Name": "DollyZoom", "Clip": asset_path}],
              "Bindings": [{"Slot": slot, "Target": target} for target, slot in slots.items()],
              **{k: sequence[k] for k in ("PlayOnStart", "Loop", "Speed")}}
    return asset, player


def asset_references(asset_paths, root):
    """Keep generated clip references compatible with the engine's GUID-based asset moves."""
    references = {}
    for path in asset_paths:
        meta = root / (path + ".meta")
        if meta.exists():
            guid = json.loads(meta.read_text()).get("GUID")
            if guid:
                references[guid] = path
    return references


def push_pull(target, position, rotation, forward, *, subject_distance, distance=6.0, fov=52.0,
              autoplay=True, focus=False):
    """Dolly zoom holding a stationary subject plane's projected size across the entire loop.

    Positive distance pushes towards the subject; negative distance pulls away. Match position's
    SmoothStep easing with SmoothFocalLength on FOV so compensation holds between keys as well.
    """
    end_depth = subject_distance - distance
    if not (math.isfinite(subject_distance) and math.isfinite(distance) and
            subject_distance > 0 and end_depth > 0 and 1 <= fov <= 179):
        raise ValueError("Dolly zoom needs positive subject depths and a valid perspective FOV")
    length = math.sqrt(sum(v * v for v in forward))
    if not math.isfinite(length) or length <= 0:
        raise ValueError("Dolly zoom needs a finite camera forward direction")
    forward = [v / length for v in forward]
    end_fov = math.degrees(2 * math.atan(subject_distance / end_depth * math.tan(math.radians(fov) / 2)))
    if not 1 <= end_fov <= 179:
        raise ValueError("Dolly zoom exceeds the camera's supported FOV range")
    def value(items):
        if not isinstance(items, (list, tuple)):
            items = [items]
        return list(items) + [0.0] * (4 - len(items))

    def track(component, property_name, start, end, interpolation="SmoothStep"):
        return {"Target": target, "Component": component, "Property": property_name, "Enabled": True,
                "Keys": [{"Frame": frame, "Value": value(sample), "Interpolation": interpolation}
                         for frame, sample in [(0, start), (90, end), (120, end), (210, start), (240, start)]]}

    end = [p + d * distance for p, d in zip(position, forward)]
    tracks = [track("Transform", "Position", position, end),
              track("Transform", "Rotation", rotation, rotation),
              track("Camera", "FieldOfView", fov, end_fov, "SmoothFocalLength")]
    if focus:
        tracks.append(track("PostProcess", "DoFFocusDistance", subject_distance, end_depth))
    return {"Type": "Sequence", "Name": "Camera Dolly Zoom", "FrameRate": 30, "DurationFrames": 240,
            "PlayOnStart": autoplay, "Loop": True, "Speed": 1.0,
            "Tracks": tracks}
