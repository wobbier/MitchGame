using ScriptCore;

// A very short energy streak along the actual shot ray; never participates in physics.
public class PortalShot : Script
{
    private float age;
    public override void OnUpdate(float deltaTime)
    {
        age += deltaTime;
        Vector3 scale = transform.Scale;
        scale.x = scale.y = 0.012f * Mathf.Max(0.001f, 1f - age / 0.12f);
        transform.Scale = scale;
        if (age >= 0.12f) Entity.Destroy();
    }
}
