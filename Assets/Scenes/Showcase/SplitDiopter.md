# Office doorway split diopter

Open `Assets/Scenes/Showcase/SplitDiopter.lvl` and press Play. A Synty Office Pack
employee stands just outside the doorway in the left foreground. The camera looks
diagonally into the office from the corridor, past the open door to his boss behind
the desk on the right. The doorway and matching hinged door use their original
single-width proportions. The characters have posed arms;
all models use explicit Office Pack materials instead of the FBXs' missing PSD paths.

The main camera looks 28° left into the room with a 28° vertical field of view,
36 mm sensor height and f/0.8. The employee is framed as a close foreground portrait.
The left focus depth is 1.83 m, the right is 8.36 m, measured along camera-forward
to the faces. The boundary sits at 47% of the image width between the characters,
with a 1.8% full transition width. The receding door and frame, background blinds,
and near corridor wall reveal the opposing defocus.

Select **Main Camera → PostProcess → Depth of Field** to compare:

- **Split Diopter** enabled: both faces stay sharp.
- Split disabled, **Focus Distance** 1.83 m: the employee stays sharp; the boss blurs.
- Split disabled, focus 8.36 m: the boss stays sharp; the employee blurs.
- **Depth of Field** disabled: everything stays sharp.
- **Visualize Circle of Confusion**: black indicates focus; red and green indicate
  depth before and behind each lens's focus plane. The feather blends these debug
  colours just as it blends the two lens images.

`python3 Tools/BuildSplitDiopter.py` rebuilds the scene from the installed Office
Pack and `Tools/SplitDiopterOfficeParts.json`. The manifest records imported mesh
paths and posed skeleton-node overrides. The builder converts Unity YAML sidecars
for the two used Office textures into engine JSON, preserving their originals in
`.tmp/SplitDiopterImport/`. Model import settings are unchanged.

Validation, from the project root inside the development environment:

```bash
python3 Tools/TestDepthOfField.py
python3 Tools/TestDepthOfFieldBlur.py
python3 Engine/Tools/RunEditorFlows.py --editor .build/Editor_Debug/Havana \
  --wrapper Engine/Tools/Headless.sh --only SplitDiopter
```

The image tests compare each side against separately rendered ordinary lenses,
including a hard split, edge positions, matching focus distances, a wide feather,
TAA and odd output sizes. The editor flow checks undo, save/load, lens toggles,
CoC debug, resize with TAA, and bypasses. Captures land in `.tmp/DepthOfFieldImages/`
and `.tmp/SplitDiopterFlows/`. The blur-quality test checks uniform circular bokeh
at radii up to 64 pixels and writes `.tmp/DepthOfFieldBlur/`; it catches repeated
edge outlines and sparse point patterns that basic focus checks miss.
