using ScriptCore;

// ScriptFlows.edscript edits `version` while the game plays: the scale shows which code runs, and
// the position shows Ticks kept counting across the reload instead of starting over.
public class HotReloadProbe : Script
{
    public int Ticks = 0;

    public override void OnUpdate(float deltaTime)
    {
        Ticks++;
        float version = 1.0f;
        transform.Scale = new Vector3(version, version, version);
        transform.Position = new Vector3(Ticks * 0.0001f, 3, 0);
    }
}
