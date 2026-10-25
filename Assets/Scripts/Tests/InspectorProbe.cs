using ScriptCore;
using System;
using System.Collections.Generic;

// Drives InspectorTest.lvl / InspectorFlows.edscript: one field of every kind the script
// inspector draws (CS-4), so the flow can edit each through script-set, prove the lot survives
// save -> load, and resolve the EntityRef in play mode.
public enum ProbeMode { Idle, Chase, Flee }

[Serializable]
public struct ProbeNested
{
    public int Inner;
    public Vector2 Offset;
}

public class InspectorProbe : Script
{
    [Header("Basics")]
    [Tooltip("Shown in the panel header")] public string Title = "untitled";
    [Multiline(3)] public string Notes = "";
    public ProbeMode Mode = ProbeMode.Idle;
    [Range(0f, 10f)] public float Clamped = 5f;
    [Range(0f, 8f)] public int Steps = 2;
    public double Precise = 0.25;

    [Header("Math")]
    public Vector4 Tint = new Vector4(1f, 2f, 3f, 4f);
    public Quaternion Spin = Quaternion.Identity;
    public Color Shade = new Color(0.2f, 0.4f, 0.6f, 1f);

    [Header("Collections")]
    public List<float> Weights = new() { 1f, 2f };
    public int[] Counts = { 3, 4 };
    public ProbeNested Nested;

    [Header("References")]
    public EntityRef Target;
    [AssetFilter("Texture")] public AssetRef Portrait;

    [Space]
    [ReadOnly] public bool ResolvedTarget;

    public override void OnStart()
    {
        ResolvedTarget = Target.Resolve().IsAlive;
        Debug.Log($"InspectorProbe: target resolved = {ResolvedTarget}");
    }
}
