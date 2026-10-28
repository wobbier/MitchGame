using System.Collections.Generic;
using ScriptCore;

// A guided missile: accelerates along its heading while turning toward MissileLauncher.AimPoint (or
// the point it was given in Targets) at a limited rate, and explodes on the first thing it touches
// (or when its fuel runs out), shoving every rigidbody in the blast radius.
public class Missile : Script
{
    public float StartSpeed = 18.0f;
    public float MaxSpeed = 70.0f;
    public float Thrust = 60.0f;
    public float TurnDegreesPerSecond = 160.0f;
    public float Lifetime = 7.0f;
    public float BlastRadius = 7.0f;
    public float BlastImpulse = 30.0f;
    public string ExplosionPrefab = "Assets/Prefabs/Drive/Explosion.prefab";
    // Seconds of free flight before guidance (randomised up to x1.5 per missile) and a corkscrew
    // wobble, which make a barrage fan out before it converges.
    public float GuidanceDelay = 0.15f;
    public float Wobble = 0.0f;
    // Scorch mark left on the surface hit (parented to it when it can move); the oldest marks
    // are removed past MaxScorches.
    public string ScorchPrefab = "Assets/Prefabs/Drive/Scorch.prefab";
    public float ScorchSize = 3.0f;
    public static int MaxScorches = 150;
    private static readonly Queue<Entity> scorches = new Queue<Entity>();
    // Missiles listed here (by whoever spawned them) home on a fixed point instead of the aim.
    public static readonly Dictionary<Entity, Vector3> Targets = new Dictionary<Entity, Vector3>();

    private static readonly System.Random random = new System.Random();
    private float delay;
    private float wobblePhase;

    private Vector3 direction;
    private float speed;
    private float age;
    private bool hasTarget;
    private Vector3 target;

    public override void OnStart()
    {
        direction = transform.Forward;
        speed = StartSpeed;
        delay = GuidanceDelay * (1f + 0.5f * (float)random.NextDouble());
        wobblePhase = (float)random.NextDouble() * 6.28f;
    }

    public override void OnUpdate(float deltaTime)
    {
        float dt = Mathf.Min(deltaTime, 0.05f);
        age += dt;
        Vector3 position = transform.WorldPosition;

        if (!hasTarget && Targets.Remove(Entity, out target))
        {
            hasTarget = true;
        }

        // Turn toward the aim point, no faster than the turn rate (after a short boost phase).
        Vector3 desired = ((hasTarget ? target : MissileLauncher.AimPoint) - position).Normalized();
        if (age > delay && desired.LengthSquared() > 0.5f)
        {
            float maxTurn = TurnDegreesPerSecond * Mathf.Deg2Rad * dt;
            float angle = (float)System.Math.Acos(Mathf.Clamp(Vector3.Dot(direction, desired), -1f, 1f));
            float t = angle > maxTurn ? maxTurn / angle : 1f;
            direction = Vector3.Lerp(direction, desired, t).Normalized();
        }
        if (Wobble > 0f)
        {
            Vector3 side = Vector3.Cross(direction, Vector3.Up);
            if (side.LengthSquared() > 0.01f)
            {
                side = side.Normalized();
                Vector3 up = Vector3.Cross(side, direction);
                float spin = age * 9f + wobblePhase;
                direction = (direction + (side * Mathf.Cos(spin) + up * Mathf.Sin(spin)) * Wobble * dt).Normalized();
            }
        }
        speed = Mathf.Min(speed + Thrust * dt, MaxSpeed);

        float step = speed * dt;
        if (Physics.Raycast(position, direction, step + 0.3f, out var hit) && hit.Entity != MissileLauncher.Shooter)
        {
            LeaveScorch(hit);
            Explode(hit.Point - direction * 0.2f);
            return;
        }
        if (age > Lifetime)
        {
            Explode(position);
            return;
        }
        position += direction * step;
        transform.WorldPosition = position;
        transform.LookAt(position + direction);
    }

    private void LeaveScorch(RaycastHit hit)
    {
        Entity scorch = World.Instantiate(ScorchPrefab);
        if (!scorch)
        {
            return;
        }
        // Project into the surface along its normal; the box is deep enough to wrap small bumps.
        scorch.Transform.WorldPosition = hit.Point;
        scorch.Transform.LookAt(hit.Point - hit.Normal);
        scorch.SetField("Decal", "Size", new Vector3(ScorchSize, ScorchSize, ScorchSize * 0.5f));
        if (hit.Entity && hit.Entity.HasComponent<Rigidbody>())
        {
            scorch.Transform.Parent = hit.Entity;
        }

        scorches.Enqueue(scorch);
        while (scorches.Count > MaxScorches)
        {
            Entity oldest = scorches.Dequeue();
            if (oldest)
            {
                oldest.Destroy();
            }
        }
    }

    private void Explode(Vector3 point)
    {
        Entity explosion = World.Instantiate(ExplosionPrefab);
        if (explosion)
        {
            explosion.Transform.WorldPosition = point;
        }

        // No overlap query from scripts: fan rays out over a sphere to find nearby bodies.
        var pushed = new HashSet<Entity>();
        for (int i = 0; i < 64; ++i)
        {
            float y = 1f - (i + 0.5f) / 64f * 2f;
            float r = Mathf.Sqrt(1f - y * y);
            float phi = i * 2.39996323f;
            Vector3 ray = new Vector3(Mathf.Cos(phi) * r, y, Mathf.Sin(phi) * r);
            if (!Physics.Raycast(point, ray, BlastRadius, out var hit) || hit.Entity == MissileLauncher.Shooter)
            {
                continue;
            }
            if (!pushed.Add(hit.Entity) || !hit.Entity.TryGetComponent<Rigidbody>(out var body))
            {
                continue;
            }
            Vector3 away = (hit.Point - point).Normalized() + Vector3.Up * 0.6f;
            float falloff = 1f - hit.Distance / BlastRadius;
            body.AddForce(away.Normalized() * BlastImpulse * falloff, ForceMode.VelocityChange);
        }
        Entity.Destroy();
    }
}
