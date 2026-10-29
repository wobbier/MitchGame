using ScriptCore;

// Moves the entity at a constant velocity (units per second) from where it started.
public class Panner : Script
{
    public Vector3 Velocity = new Vector3(0.37f, 0.11f, 0f);

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
        transform.Position = origin + Velocity * time;
    }
}
