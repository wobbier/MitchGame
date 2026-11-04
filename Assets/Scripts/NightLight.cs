using ScriptCore;

// A lamp that follows the DayNightCycle (issue board #18): it listens for DayPhaseChanged and turns
// its entity's Light on for Dusk and Night, off for Dawn and Day, easing the intensity so the
// switch isn't a pop. Put it on any entity with a Light; the cycle's events reach every subscriber.
public class NightLight : Script
{
    public float OnIntensity = 6f;
    public float FadeSeconds = 1.5f;

    private Light light;
    private float target;
    private bool reported;

    public override void OnStart()
    {
        light = GetComponent<Light>();
        target = 0f;
        light.Intensity = 0f;
        On<DayPhaseChanged>(e => Apply(e.Phase));
        // The cycle may have started (and announced its phase) before this lamp subscribed.
        if (DayNightCycle.Current != null) Apply(DayNightCycle.Current.Phase);
    }

    public override void OnReload()
    {
        // Only public fields survive a hot reload: re-subscribe and re-derive the target so a lit
        // lamp doesn't fade back off until the next phase change.
        light = GetComponent<Light>();
        On<DayPhaseChanged>(e => Apply(e.Phase));
        reported = true;
        if (DayNightCycle.Current != null) Apply(DayNightCycle.Current.Phase);
        else if (light != null) target = light.Intensity;
    }

    private void Apply(DayPhase phase)
    {
        bool on = phase == DayPhase.Dusk || phase == DayPhase.Night;
        float next = on ? OnIntensity : 0f;
        if (next != target || !reported)
        {
            reported = true;
            Debug.Log($"NightLight: {(on ? "on" : "off")} ({Entity.Name}, {phase})");
        }
        target = next;
    }

    public override void OnUpdate(float dt)
    {
        if (light == null)
        {
            return;
        }
        float k = FadeSeconds <= 0f ? 1f : 1f - System.MathF.Exp(-dt / FadeSeconds);
        float current = light.Intensity;
        if (System.MathF.Abs(current - target) > 1e-3f)
        {
            light.Intensity = current + (target - current) * k;
        }
    }
}
