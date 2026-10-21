using ScriptCore;

// The detonation: a blinding flash, a shockwave that throws every rigidbody in range, a giant
// scorch, an expanding ground ring and a mushroom cloud that climbs and spreads, then everything
// is cleaned up. Shake is read by CockpitCamera.
public class NukeBlast : Script
{
    public float BlastRadius = 110.0f;
    public float BlastSpeed = 70.0f;
    public float FlashIntensity = 4000.0f;
    public float RingSpeed = 90.0f;
    public float CloudRiseSpeed = 14.0f;
    public float CloudHeight = 90.0f;
    public float Lifetime = 30.0f;
    public string CloudPrefab = "Assets/Prefabs/Drive/NukeCloud.prefab";
    public string RingPrefab = "Assets/Prefabs/Drive/NukeRing.prefab";
    public string ScorchPrefab = "Assets/Prefabs/Drive/Scorch.prefab";

    // Camera shake strength in degrees, decaying; CockpitCamera applies it.
    public static float Shake;

    private Entity cloud;
    private Entity ring;
    private Vector3 origin;
    private float age;
    private int pushedWaves;

    public override void OnStart()
    {
        origin = transform.WorldPosition;
        cloud = World.Instantiate(CloudPrefab);
        if (cloud)
        {
            cloud.Transform.WorldPosition = origin + Vector3.Up * 4f;
        }
        ring = World.Instantiate(RingPrefab);
        if (ring)
        {
            ring.Transform.WorldPosition = origin + Vector3.Up * 0.5f;
        }
        Entity scorch = World.Instantiate(ScorchPrefab);
        if (scorch)
        {
            scorch.Transform.WorldPosition = origin;
            scorch.Transform.LookAt(origin - Vector3.Up);
            scorch.SetField("Decal", "Size", new Vector3(45f, 45f, 30f));
        }
        Shake = 6f;
    }

    public override void OnUpdate(float deltaTime)
    {
        age += deltaTime;

        // Flash: white-hot, then a long orange glow.
        float flash = Mathf.Max(1f - age / 0.6f, 0f);
        float glow = Mathf.Max(1f - age / 8f, 0f);
        Entity.SetField("Light", "Intensity", FlashIntensity * flash * flash + 300f * glow);

        // The shockwave pushes bodies as the ring sweeps over them, in three expanding shells.
        float front = age * RingSpeed;
        while (pushedWaves < 3 && front >= BlastRadius * (pushedWaves + 1) / 3f)
        {
            Push(BlastRadius * pushedWaves / 3f, BlastRadius * (pushedWaves + 1) / 3f);
            ++pushedWaves;
        }
        if (ring)
        {
            float r = Mathf.Min(front, BlastRadius * 1.3f);
            ring.Transform.Scale = new Vector3(r, 0.6f + r * 0.02f, r);
            if (front > BlastRadius * 1.3f)
            {
                ring.Destroy();
            }
        }

        if (cloud)
        {
            float rise = Mathf.Min(age * CloudRiseSpeed, CloudHeight);
            cloud.Transform.WorldPosition = origin + Vector3.Up * (4f + rise);
            float spread = 1f + Mathf.Min(age / 6f, 1f) * 2.5f;
            cloud.Transform.Scale = new Vector3(spread, spread * 0.7f, spread);
        }

        Shake = Mathf.Max(Shake - deltaTime * 2.5f, 0f);
        if (age > Lifetime)
        {
            if (cloud)
            {
                cloud.Destroy();
            }
            Entity.Destroy();
        }
    }

    private void Push(float innerRadius, float outerRadius)
    {
        foreach (Entity hit in Physics.OverlapSphere(origin, outerRadius, 4096))
        {
            if (!hit.TryGetComponent<Rigidbody>(out var body))
            {
                continue;
            }
            Vector3 offset = hit.Transform.WorldPosition - origin;
            float distance = offset.Length();
            if (distance < innerRadius)
            {
                continue;
            }
            float falloff = 1f - distance / BlastRadius;
            Vector3 away = (offset / Mathf.Max(distance, 0.01f) + Vector3.Up * 0.8f).Normalized();
            body.AddForce(away * BlastSpeed * Mathf.Max(falloff, 0.15f), ForceMode.VelocityChange);
        }
    }
}
