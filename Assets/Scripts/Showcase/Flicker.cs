using ScriptCore;

// Fire-light flicker through generic component access (the Light component has no C# wrapper):
// layered sines, so captures with a fixed frame time stay repeatable.
public class Flicker : Script
{
    public float Strength = 0.25f;
    public float Speed = 1.0f;
    public float Seed = 0.0f;

    private float baseIntensity;
    private float time;

    public override void OnStart()
    {
        baseIntensity = Entity.GetField("Light", "Intensity", 1f);
        time = Seed * 17.0f;
    }

    public override void OnUpdate(float deltaTime)
    {
        time += deltaTime * Speed;
        float wave = Mathf.Sin(time * 7.3f) * 0.5f + Mathf.Sin(time * 13.1f + 1.7f) * 0.3f + Mathf.Sin(time * 23.7f + 4.1f) * 0.2f;
        Entity.SetField("Light", "Intensity", baseIntensity * (1f + wave * Strength));
    }
}
