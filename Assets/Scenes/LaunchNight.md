# Launch Night

It's 3:47 AM at Moonshot Games, thirteen minutes before the gold master is due. The build server is
on fire.

The scene has 2,161 entities and 182 distinct Synty Office Pack models, with 28 particle systems,
37 lights, 21 shader graphs, 12 looping animation sequences and 16 ambient sound loops. Nobody explains what happened; the office tells it:

| Where | What happened |
| --- | --- |
| The dev pit | One developer is still typing at a triple monitor, headset on, behind a pyramid of ten energy drinks and a carpet of crumpled paper. His ceiling panel is failing. Across the pod, a colleague has fallen asleep face-down on her keyboard; her screensaver bounces "ZZZ..." round the screen. A hanging LED board counts down to the gold master; on its back, the CI dashboard says build #4471 FAILED, 847 tests failing, build agent ON FIRE, days since last fire: 0. |
| The rage quit | An empty chair still turning slowly. A monitor face-up on the carpet showing a crash screen ("STOP CODE: SHIP_IT_ANYWAY"), the keyboard thrown under the next desk, letters on the floor, and a box packed with a plant, a photo and a mug. Paper planes glide round the pit. |
| The whiteboard | "SHIP IT!!!", "BUGS: 847", 47 tally marks of crunch and, in green, "DO NOT TOUCH THE BUILD SERVER (IT'S FINE)". |
| QA | Sticky notes all over the monitor, toy guns on the desk and foam darts across the aisle from the 1 AM nerf war. |
| The server room | Rack BUILD-01 is scorched and burning: flames, sparks, smoke rolling out under the door frame. The sprinklers are going and the floor is flooded out into the corridor. Red beacons sweep, the racks' LEDs strobe red near the fire, and an empty extinguisher lies in a puddle of foam. |
| The corridor | The cleaner is mopping the flood with her back to the fire. The photocopier, marked OUT OF ORDER, is spitting paper across the floor. A ceiling panel has come down, and the cable it brought with it is sparking. |
| The kitchen | The launch party nobody came to: a cake with its candles still burning, balloons tied to the chairs, party hats, bunting and an air horn. Six empty donut boxes with one donut left. The espresso machine is pouring with no cup under it: over its drip tray, across the counter and off the edge onto the floor, and someone's 2 AM popcorn is smoking in the microwave. The milk is labelled. |
| The lounge | A developer asleep in a beanbag with the laptop on his stomach still compiling shaders: 47391 / 47392, 99%, "ETA: 3 MINUTES". The arcade cabinet runs its attract mode, the neon cactus buzzes and three fish swim laps. |
| The conference room | The projector was left on, showing the Q4 roadmap: 1. SHIP MOONSHOT, 2. ???, 3. PROFIT, 4. SLEEP. A hockey-stick chart marked "WE ARE HERE" at the bottom. Chairs pushed back at odd angles. |
| The lobby | The security guard asleep, head back, nodding off and jerking awake. His centre CCTV monitor shows the server room on fire with "! MOTION !" flashing. The lift is out of order. Security cameras pan. |
| The boss's office | Glass walls with the blinds down, putting green, champagne and four flutes on ice. The boss stands at the window on the phone, back to the floor, while his monitor shows the same burning server room. |
| Outside | A thunderstorm over the city, 30 floors down. Rain runs down the glass, lightning forks over the towers and lights up the office. |

## Running it

Open **Assets/Scenes/LaunchNight.lvl** in Havana and press Play, or on Linux from the repository
root:

```bash
nix develop --command .build/Game_linux_Debug/Game_EntryPoint_x64 --scene Assets/Scenes/LaunchNight.lvl --no-debug-overlay
```

The **Camera Tour** sequence drives the Main Camera through 14 shots (108 s, looping): through the
storm glass, the last developer, the countdown, the sleeper, the rage quit, the fire, the cleaner,
the paper jam, the roadmap, security, the party, the beanbag, the boss, and a wide shot at 3:47 AM.
Each shot is a slow move with cuts between; FOV and depth-of-field focus are keyed per shot.

## Sequences

Everything that moves is a looping **Sequence** (Assets/Animations/LaunchNight/*.sequence), played
by an entity under **Sequences** in the hierarchy. Select one and open **View > Sequencer** to scrub
or edit it.

| Clip | Length | Animates |
| --- | --- | --- |
| Camera Tour | 108 s | Main Camera position, rotation, FieldOfView, DoFFocusDistance |
| Storm | 23 s | Lightning flash (spot light intensity), camera exposure, the three bolts (scale toggled with Hold keys) |
| Server Room Alarm | 5 s | Both beacon rotors, the fire light's flicker |
| Office Life | 12 s | The spinning chair, the failing panels, sparks, candles, microwave, balloons, fish, security cameras |
| Paper Planes | 14 s | Three planes banking round the pit |
| Ceiling Fan | 2 s | The boss's fan |
| Typing | 2 s | The developer's arm, hand and head bones |
| Breathing / Beanbag Breathing | 4.5 / 5.2 s | Spine bones of the two sleepers |
| Guard Dozing | 11 s | Breathing, then a nod and a jerk awake |
| Boss On The Phone | 9 s | The boss's spine: turning as he talks |
| Mopping | 2.4 s | The cleaner's spine and arms (the mop is parented to her hand) |

Characters are expanded skeletons written into the scene, so sequences can animate their bones
directly. The poses come from a small IK solver in the builder (`solve_pose`): hands are placed on
the keyboard, the phone, the mop handle and the laptop.

## Shader graphs

All in `Assets/ShaderGraphs/LaunchNight/`, generated sources in `<Name>.sg/`. Signs and screens print
their text with a 5x7 pixel font compiled into Custom Function code (`Tools/PixelFont.py`), so the
words are part of the graph. Screen graphs share **UV Rect** and **Flip** properties to fit any
monitor's UVs.

| Graph | Target | Used for |
| --- | --- | --- |
| `CodeScreen` | Lit | Scrolling, syntax-coloured code with line numbers and a cursor (Seed and Scroll Speed per monitor) |
| `Countdown` | Lit | LED matrix "GOLD MASTER IN hh:mm:ss", counting down live from Start Seconds |
| `BuildStatus` | Lit | The CI dashboard, flashing FAILED, with status bars |
| `BlueScreen` | Lit | The crash screen on the thrown monitor |
| `Screensaver` | Lit | "ZZZ..." bouncing and changing colour at each wall |
| `Compiling` | Lit | The beanbag laptop's stuck progress bar |
| `CCTVServerRoom` / `CCTVLobby` | Lit | Grainy feeds with a rolling bar, camera name, live clock, REC, and the fire with a MOTION alarm |
| `RoadmapSlide` | Lit | The projected Q4 roadmap and chart |
| `ArcadeScreen` | Lit | The Synty arcade screen, scrolling, with scanlines |
| `ServerLEDs` | Lit | Rack status LEDs; Alarm turns them red and strobing |
| `RainGlass` | Lit, transparent | Beading drops and drops running down with broken trails, in world space |
| `CityWindows` | Lit | Procedural tower windows, some lit warm or cool, a few flickering TVs |
| `BlinkLight` | Lit | Aircraft warning lights and other indicators |
| `Neon` | Lit | The neon cactus: saturated parts of the atlas glow, buzz and drop out |
| `FishTankWater` | Lit, transparent | The tank water |
| `FloodWater` | Decal | Standing water with a ragged edge, rippled by drips (sprinklers); also the coffee puddle |
| `Whiteboard` | Decal | Marker text and tally marks |
| `Lightning` | Unlit, additive | Forked bolts |
| `PaperSheet` | Particle | Printed sheets from the photocopier |
| `NightShift` | Post Process (after tonemap) | Grain, chromatic fringing and a faint red alarm pulse at the edges |

The fire and candle flames reuse `LostTemple/Flame`.

## Sound

Sixteen looping `AudioSource`s (all **PlayOnAwake**, on the SFX bus) are synthesized by
`Tools/LaunchNightAudio.py` into `Assets/Sounds/LaunchNight/`. The storm and the room tone are 2D;
the rest are 3D with a LinearSquare rolloff, so each fades to silence a few metres away and the
mix changes as the tour moves.

| Sound | Where | Notes |
| --- | --- | --- |
| Storm | everywhere (2D) | Rain and drops on the glass, wind gusts, and thunder after the Storm clip's flashes (same 23 s loop) |
| Room Tone | everywhere (2D) | The air handling, very low |
| Fire, Server Hum, Sprinklers | the server room | Roar and crackle, fans and mains hum, hiss and spatter |
| Fire Alarm | over the server room door | Temporal-three beeps in the Server Room Alarm clip's 5 s |
| Typing | the last developer's keyboard | In step with the Typing clip, pauses included |
| Panel Buzz | his failing ceiling panel | Cuts out and crackles where Office Life flickers it |
| Sparks, Copier | the corridor | The fallen cable arcing; the jammed photocopier |
| Coffee, Microwave | the kitchen | Coffee running off the counter; popcorn popping |
| Fish Tank, Arcade | the lounge | Bubbler; a square-wave attract-mode tune |
| Ceiling Fan | the boss's office | |
| Snoring | the security guard | Snores, sighs and the snort at the nod, in step with Guard Dozing |

The loops are seamless (beds crossfade their tail into their head; events wrap round the end), and
the timed ones share their Sequence's length, so they stay in step when both start on Play.
Automated runs are silent; open the scene in Havana and press Play to hear it.

## Rebuilding

```bash
python3 Tools/BuildLaunchNight.py            # scene, sequences, graphs and the editor flow
python3 Tools/BuildLaunchNight.py --graphs   # graphs only
python3 Tools/LaunchNightAudio.py --force     # rewrite the sound loops (otherwise only missing ones)
```

Both overwrite their files, so save editor changes elsewhere first. After changing a graph,
regenerate its `.sg/` sources: save it in Havana, or run
`ME_SHADERGRAPH_UPDATE=1 .build/Game_linux_Debug/MitchEngine_Tests -tc="*project graphs*"`.

The builder reads three caches in `Tools/`:

- `LaunchNightParts.json`: each Office model's part paths.
- `LaunchNightRigs.json`: the expanded character skeletons.
- `LaunchNightBounds.json`: model bounds, taken from the pack's OBJ files with Z mirrored to match
  the FBX import.

The parts and rigs were recorded by loading the models in Havana and saving the scene. A new
model needs a round trip first.

The builder also replaces the Unity YAML `.meta` sidecars of the textures it uses with JSON ones,
with stable GUIDs (the engine would otherwise set a YAML sidecar aside and write a fresh one). The
originals are kept in `.tmp/LaunchNightImport/`.

The flow checks every graph and plays the scene:

```bash
Engine/Tools/Headless.sh .build/Editor_Debug/Havana --scene Assets/Scenes/LaunchNight.lvl --editor-exec Assets/Scenes/LaunchNight.edscript
```

## Things learned building it

- Synty walls are single-sided: only the face on their local -Z side renders. The builder runs each
  outer wall with the room on that side, so from outside the building you see straight in. The facade
  boxes outside the storm glass cover that in the opening shot. Interior glass walls get a mirrored
  twin (`partition`), with near-clear glass so the panes don't double the tint.
- The `*_Blinds_*` wall models are only the slats; put them over a glass wall.
- `SM_Bld_Floor_Panel_01` is a thin trim strip, not a floor tile. Bounds tops can mislead too: the
  cake's is its own centre candle (the icing is at 0.29 m), and a chair's seat sits ahead of its
  bounds' centre. Measure the OBJ when something has to touch it.
- With a procedural sky, every directional light follows the sun or moon. The lightning is a
  distant shadowed spot light instead.
- A Multiply between a scalar and an inline vector default used to resolve to a scalar; the compiler
  now widens the group to the vector.
- The office has no indoor reflection probes, so glossy screens reflect the night sky. Screen
  graphs output low Occlusion to stay black.
