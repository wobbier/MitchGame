using ScriptCore;

// Drifts the entity around where it started on a slow, looping path and blinks its light,
// like a firefly. Deterministic (no random state), so fixed-step captures repeat.
public class Wander : Script
{
    public float Radius = 1.5f;
    public float Speed = 0.4f;
    public float Seed = 0.0f;
    public float BlinkSpeed = 0.7f;

    private Vector3 origin;
    private float baseIntensity;
    private float time;

    public override void OnStart()
    {
        origin = transform.Position;
        baseIntensity = Entity.GetField("Light", "Intensity", 1f);
        time = Seed * 7.31f;
    }

    public override void OnUpdate(float deltaTime)
    {
        time += deltaTime;
        float t = time * Speed;
        Vector3 offset = new Vector3(Mathf.Sin(t * 1.13f + Seed) + 0.4f * Mathf.Sin(t * 2.71f),
                                     0.35f * Mathf.Sin(t * 1.91f + Seed * 2.0f),
                                     Mathf.Cos(t * 0.87f + Seed * 1.3f) + 0.4f * Mathf.Cos(t * 2.33f));
        transform.Position = origin + offset * Radius;
        float blink = Mathf.Max(0f, Mathf.Sin(time * BlinkSpeed * 6.2831853f + Seed * 3.1f));
        Entity.SetField("Light", "Intensity", baseIntensity * (0.15f + 0.85f * blink * blink));
    }
}
