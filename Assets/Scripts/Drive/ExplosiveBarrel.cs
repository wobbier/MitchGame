using ScriptCore;

// A red fuel drum that goes up when something knocks it about: moving faster than ArmSpeed (rammed
// by the car, shoved by a blast, hit by a flying crate) lights a short fuse, then it explodes,
// throwing every loose body nearby (which sets off the drums next to it) and tossing the car if it's
// close. Drums ignore the first SettleTime seconds while the level's physics settle.
public class ExplosiveBarrel : Script
{
    public float ArmSpeed = 6.0f;
    public float SettleTime = 1.0f;
    public float BlastRadius = 9.0f;
    public float BlastSpeed = 22.0f;
    public float CarLaunch = 10.0f;
    public string ExplosionPrefab = "Assets/Prefabs/Drive/Explosion.prefab";

    private static readonly System.Random random = new System.Random();
    private Rigidbody body;
    private float fuse = -1f;
    private float age;

    public override void OnStart()
    {
        Entity.TryGetComponent(out body);
    }

    public override void OnUpdate(float deltaTime)
    {
        age += deltaTime;
        if (age < SettleTime || body == null)
        {
            return;
        }
        if (fuse < 0f && body.Velocity.Length() > ArmSpeed)
        {
            // Neighbours go off one after another rather than all on the same frame.
            fuse = 0.08f + (float)random.NextDouble() * 0.22f;
        }
        if (fuse >= 0f && (fuse -= deltaTime) <= 0f)
        {
            Explode();
        }
    }

    private void Explode()
    {
        Vector3 center = transform.WorldPosition;
        Entity explosion = World.Instantiate(ExplosionPrefab);
        if (explosion)
        {
            explosion.Transform.WorldPosition = center;
        }
        VehicleController car = VehicleController.Active;
        foreach (Entity hit in Physics.OverlapSphere(center, BlastRadius, 512))
        {
            if (hit == Entity)
            {
                continue;
            }
            Vector3 away = hit.Transform.WorldPosition - center;
            float distance = away.Length();
            float falloff = Mathf.Max(1f - distance / BlastRadius, 0.2f);
            Vector3 flat = new Vector3(away.x, 0f, away.z);
            Vector3 direction = flat.LengthSquared() > 0.01f ? flat.Normalized() : Vector3.Up;
            if (car != null && hit == car.Entity)
            {
                car.Launch((direction * 0.6f + Vector3.Up) * CarLaunch * falloff);
            }
            else if (hit.TryGetComponent<Rigidbody>(out var other))
            {
                other.AddForce((direction + Vector3.Up * 0.6f) * BlastSpeed * falloff, ForceMode.VelocityChange);
            }
        }
        Entity.Destroy();
    }
}
