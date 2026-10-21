using ScriptCore;

// Fades the explosion's flash light out and removes the effect once the particles are done.
public class Explosion : Script
{
    public float FlashIntensity = 60.0f;
    public float FlashTime = 0.35f;
    public float Lifetime = 3.0f;

    private float age;

    public override void OnUpdate(float deltaTime)
    {
        age += deltaTime;
        float flash = Mathf.Max(1f - age / FlashTime, 0f);
        Entity.SetField("Light", "Intensity", FlashIntensity * flash * flash);
        if (age > Lifetime)
        {
            Entity.Destroy();
        }
    }
}
