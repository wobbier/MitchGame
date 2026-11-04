using System;
using ScriptCore;

/// <summary>The part of the day a <see cref="DayNightCycle"/> is in.</summary>
public enum DayPhase { Night, Dawn, Day, Dusk }

/// <summary>Published on the EventBus when the phase of the day changes.</summary>
public readonly record struct DayPhaseChanged(DayPhase Phase, float Hour);

/// <summary>Published on the EventBus when the weather preset changes.</summary>
public readonly record struct WeatherChanged(string Weather);

// A dynamic sky (issue board #18): drives a Camera's procedural sky through a day/night cycle and a
// set of weather presets, and tells gameplay about it. Attach it to the camera entity (or any
// entity; it finds the current camera). The engine's procedural sky already models the sun, moon,
// stars, atmosphere and clouds; this script owns the clock and the weather on top of it:
//
//   - Hour advances at 24 h per DayLengthSeconds (0 holds it), wrapping at midnight. Setting the
//     camera's ProceduralSky.Time every frame keeps the authored field authoritative when Running is
//     false, so the inspector and edscripts can still scrub it.
//   - Weather presets blend cloud coverage / density, wind and haze towards a target over
//     WeatherTransitionSeconds; WeatherCycleSeconds > 0 walks through the presets automatically.
//   - DayPhaseChanged / WeatherChanged events let lights, audio and AI react ("lights on at Night").
public class DayNightCycle : Script
{
    public float DayLengthSeconds = 600f;          // real seconds per 24 h; 0 holds the time of day
    public float StartHour = 6f;                   // hour the cycle starts at on Play
    public bool Running = true;
    public float Hour;                             // the current time of day, read-only in practice
    public string Weather = "Clear";               // Clear, Cloudy, Overcast or Storm
    public float WeatherCycleSeconds = 0f;         // > 0: next preset every N seconds
    public float WeatherTransitionSeconds = 8f;
    public bool ForceProceduralSky = true;         // switch the camera's background to Procedural Sky

    private struct SkyState
    {
        public float Coverage, Density, Wind, Turbidity;
        public static SkyState Lerp(SkyState a, SkyState b, float t) => new SkyState
        {
            Coverage = a.Coverage + (b.Coverage - a.Coverage) * t,
            Density = a.Density + (b.Density - a.Density) * t,
            Wind = a.Wind + (b.Wind - a.Wind) * t,
            Turbidity = a.Turbidity + (b.Turbidity - a.Turbidity) * t,
        };
    }

    private static readonly (string Name, SkyState Sky)[] Presets =
    {
        ("Clear", new SkyState { Coverage = 0.15f, Density = 1.0f, Wind = 6f, Turbidity = 1.9f }),
        ("Cloudy", new SkyState { Coverage = 0.5f, Density = 1.2f, Wind = 10f, Turbidity = 2.5f }),
        ("Overcast", new SkyState { Coverage = 0.9f, Density = 1.6f, Wind = 14f, Turbidity = 3.5f }),
        ("Storm", new SkyState { Coverage = 1.0f, Density = 2.5f, Wind = 30f, Turbidity = 5f }),
    };

    private Entity camera;
    private SkyState current, target;
    private DayPhase phase;
    private bool phaseKnown;
    private float weatherTimer;
    private int presetIndex;

    /// <summary>The current phase of the day.</summary>
    public DayPhase Phase => phase;
    /// <summary>Whether it is night (before 5 h or from 20 h).</summary>
    public bool IsNight => PhaseOf(Hour) == DayPhase.Night;

    public override void OnStart()
    {
        Hour = Wrap(StartHour);
        Bind();
    }

    public override void OnReload() => Bind();

    private void Bind()
    {
        camera = Entity.HasComponent<Camera>() ? Entity : FindCurrentCamera();
        if (!camera.IsAlive)
        {
            Debug.Log("DayNightCycle: no camera to drive");
            return;
        }
        if (ForceProceduralSky && camera.GetField("Camera", "ClearType", "") != "Procedural")
        {
            camera.SetField("Camera", "ClearType", "Procedural");
        }
        current = new SkyState
        {
            Coverage = camera.GetField("Camera", "ProceduralSky.CloudCoverage", 0.4f),
            Density = camera.GetField("Camera", "ProceduralSky.CloudDensity", 1f),
            Wind = camera.GetField("Camera", "ProceduralSky.WindSpeed", 8f),
            Turbidity = camera.GetField("Camera", "ProceduralSky.Turbidity", 1.9f),
        };
        presetIndex = Math.Max(0, Array.FindIndex(Presets, p => p.Name == Weather));
        Weather = Presets[presetIndex].Name;
        target = Presets[presetIndex].Sky;
        weatherTimer = 0f;
        phaseKnown = false;
        ApplyTime();
        UpdatePhase();
        Debug.Log($"DayNightCycle: weather {Weather}");
    }

    public override void OnUpdate(float dt)
    {
        if (!camera.IsAlive)
        {
            return;
        }
        if (Running && DayLengthSeconds > 0f)
        {
            Hour = Wrap(Hour + dt * 24f / DayLengthSeconds);
        }
        ApplyTime();
        UpdatePhase();

        if (WeatherCycleSeconds > 0f)
        {
            weatherTimer += dt;
            if (weatherTimer >= WeatherCycleSeconds)
            {
                weatherTimer -= WeatherCycleSeconds;
                SetWeather(Presets[(presetIndex + 1) % Presets.Length].Name);
            }
        }
        // Exponential blend: frame-rate independent, settles within a few transition lengths.
        float k = WeatherTransitionSeconds <= 0f ? 1f : 1f - MathF.Exp(-dt / WeatherTransitionSeconds);
        SkyState next = SkyState.Lerp(current, target, k);
        if (MathF.Abs(next.Coverage - current.Coverage) + MathF.Abs(next.Density - current.Density)
            + MathF.Abs(next.Wind - current.Wind) + MathF.Abs(next.Turbidity - current.Turbidity) > 1e-4f)
        {
            current = next;
            camera.SetField("Camera", "ProceduralSky.CloudCoverage", current.Coverage);
            camera.SetField("Camera", "ProceduralSky.CloudDensity", current.Density);
            camera.SetField("Camera", "ProceduralSky.WindSpeed", current.Wind);
            camera.SetField("Camera", "ProceduralSky.Turbidity", current.Turbidity);
        }
    }

    /// <summary>Jumps to an hour of the day (0..24, wrapping).</summary>
    public void SetHour(float hour)
    {
        Hour = Wrap(hour);
        ApplyTime();
        UpdatePhase();
    }

    /// <summary>Starts blending towards a weather preset; false for an unknown name.</summary>
    public bool SetWeather(string name)
    {
        int index = Array.FindIndex(Presets, p => string.Equals(p.Name, name, StringComparison.OrdinalIgnoreCase));
        if (index < 0)
        {
            return false;
        }
        presetIndex = index;
        target = Presets[index].Sky;
        if (Weather != Presets[index].Name)
        {
            Weather = Presets[index].Name;
            Debug.Log($"DayNightCycle: weather {Weather}");
            EventBus.Publish(new WeatherChanged(Weather));
        }
        return true;
    }

    private void ApplyTime() => camera.SetField("Camera", "ProceduralSky.Time", Hour);

    private void UpdatePhase()
    {
        DayPhase now = PhaseOf(Hour);
        if (phaseKnown && now == phase)
        {
            return;
        }
        phase = now;
        phaseKnown = true;
        Debug.Log($"DayNightCycle: phase {phase} at {Hour:F1} h");
        EventBus.Publish(new DayPhaseChanged(phase, Hour));
    }

    private static DayPhase PhaseOf(float hour)
    {
        if (hour < 5f || hour >= 20f) return DayPhase.Night;
        if (hour < 8f) return DayPhase.Dawn;
        if (hour < 17f) return DayPhase.Day;
        return DayPhase.Dusk;
    }

    private static float Wrap(float hour)
    {
        hour %= 24f;
        return hour < 0f ? hour + 24f : hour;
    }

    private static Entity FindCurrentCamera()
    {
        Entity first = Entity.Null;
        foreach (Entity candidate in Query.WithComponent("Camera"))
        {
            if (candidate.GetField("Camera", "IsCurrent", false))
            {
                return candidate;
            }
            if (!first.IsAlive)
            {
                first = candidate;
            }
        }
        return first;
    }

    public override void OnEditorInspect()
    {
        ImGui.Text($"{Hour:F2} h  ({phase})  weather {Weather}");
        if (ImGui.Button("Dawn")) SetHour(6f);
        ImGui.SameLine();
        if (ImGui.Button("Noon")) SetHour(12f);
        ImGui.SameLine();
        if (ImGui.Button("Dusk")) SetHour(18f);
        ImGui.SameLine();
        if (ImGui.Button("Midnight")) SetHour(0f);
        for (int i = 0; i < Presets.Length; ++i)
        {
            if (i > 0) ImGui.SameLine();
            if (ImGui.Button(Presets[i].Name)) SetWeather(Presets[i].Name);
        }
    }
}
