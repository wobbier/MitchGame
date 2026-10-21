using System;
using ScriptCore;

// Attach to the camera. Reads the reflected PostProcess fields so inspector/automation edits
// remain authoritative until a button is pressed or the optional rack-focus animation runs.
public class DepthOfFieldTest : Script
{
    public bool RackFocus = false;
    public float CycleSeconds = 12.0f;
    private float elapsed;

    public override void OnUpdate(float dt)
    {
        elapsed += dt;
        if (RackFocus)
        {
            float t = 0.5f - 0.5f * (float)Math.Cos(elapsed * Math.PI * 2.0 / Math.Max(CycleSeconds, 1.0f));
            // Interpolate diopters to make a lens-like focus pull between 3.5 and 18 metres.
            Entity.SetField("PostProcess", "DoFFocusDistance", 1.0f / ((1.0f - t) / 3.5f + t / 18.0f));
        }
        if (ImGui.Begin("Depth of Field Test"))
        {
            ImGui.Text("Near: red at 3.5m | Middle: cyan at 8m | Far: gold at 18m");
            ImGui.Text($"Focus: {Entity.GetField<float>("PostProcess", "DoFFocusDistance"):F2} m");
            bool enabled = Entity.GetField<bool>("PostProcess", "DepthOfField");
            if (ImGui.Checkbox("Depth of field", ref enabled)) Entity.SetField("PostProcess", "DepthOfField", enabled);
            bool debug = Entity.GetField<bool>("PostProcess", "DoFDebugCoC");
            if (ImGui.Checkbox("CoC: red near / green far / black sharp", ref debug)) Entity.SetField("PostProcess", "DoFDebugCoC", debug);
            ImGui.Checkbox("Animate rack focus", ref RackFocus);
            if (ImGui.Button("Focus near (3.5m)")) Focus(3.5f);
            if (ImGui.Button("Focus middle (8m)")) Focus(8.0f);
            if (ImGui.Button("Focus far (18m)")) Focus(18.0f);
            if (ImGui.Button("Aperture f/1")) Entity.SetField("PostProcess", "DoFAperture", 1.0f);
            if (ImGui.Button("Aperture f/2.8")) Entity.SetField("PostProcess", "DoFAperture", 2.8f);
            if (ImGui.Button("Aperture f/8")) Entity.SetField("PostProcess", "DoFAperture", 8.0f);
        }
        ImGui.End();
    }

    private void Focus(float distance)
    {
        RackFocus = false;
        Entity.SetField("PostProcess", "DoFFocusDistance", distance);
    }
}
