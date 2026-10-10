using ScriptCore;

// Floats the entity up and down around where it started.
public class Bobber : Script
{
    public float Amplitude = 0.25f;
    public float Frequency = 0.5f;
    public float Phase = 0.0f;

    private Vector3 origin;
    private float time;

    public override void OnStart()
    {
        origin = transform.Position;
        time = 0f;
    }

    public override void OnUpdate(float deltaTime)
    {
        time += deltaTime;
        float offset = Mathf.Sin((time * Frequency + Phase) * 2f * (float)Mathf.PI) * Amplitude;
        transform.Position = origin + Vector3.Up * offset;
    }
}
