using ScriptCore;

// Fires guided missiles from where this entity sits (a mount on the car's roof). Fire (left click)
// shoots one missile; Aim (right click) unleashes a barrage of 20-50 small rockets that spray out
// in every direction and then home in on the aim. While a missile flies it steers toward wherever the
// camera is looking (AimPoint), so you can bend it onto a target. A marker shows the aim point.
public class MissileLauncher : Script
{
    public string CameraName = "Main Camera";
    public string VehicleName = "Vehicle";
    public string MissilePrefab = "Assets/Prefabs/Drive/Missile.prefab";
    public float Cooldown = 0.6f;
    public float AimRange = 400.0f;
    public string RocketPrefab = "Assets/Prefabs/Drive/Rocket.prefab";
    public int BarrageMin = 20;
    public int BarrageMax = 50;
    public float BarrageInterval = 0.025f;
    public float BarrageCooldown = 3.0f;
    // Hold Fire / trigger a barrage, for automated captures.
    public bool TestFire = false;
    public bool TestBarrage = false;

    // Shared with Missile: where the player is aiming and which entity fired.
    public static Vector3 AimPoint;
    public static Entity Shooter;

    private Entity cameraEntity;
    private float reload;
    private float barrageReload;
    private int barrageLeft;
    private float barrageTimer;
    private readonly System.Random random = new System.Random();

    public override void OnStart()
    {
        cameraEntity = World.Find(CameraName);
        Shooter = World.Find(VehicleName);
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnUpdate(float deltaTime)
    {
        if (!cameraEntity)
        {
            return;
        }
        Transform view = cameraEntity.Transform;
        Vector3 origin = view.WorldPosition;
        Vector3 forward = view.Forward;
        AimPoint = origin + forward * AimRange;
        if (Physics.Raycast(origin, forward, AimRange, out var hit) && hit.Entity != Shooter)
        {
            AimPoint = hit.Point;
        }
        float distance = Vector3.Distance(origin, AimPoint);
        Debug.DrawSphere(AimPoint, Mathf.Clamp(distance * 0.008f, 0.08f, 2.0f), new Vector3(1f, 0.25f, 0.1f));

        reload -= deltaTime;
        if (reload <= 0f && ((CockpitCamera.Aiming && Input.IsActionPressed("Fire")) || TestFire))
        {
            reload = Cooldown;
            Vector3 start = transform.WorldPosition;
            Entity missile = World.Instantiate(MissilePrefab);
            if (missile)
            {
                missile.Transform.WorldPosition = start;
                // Launch upward-forward; the guidance pulls it onto the aim.
                missile.Transform.LookAt(start + (AimPoint - start).Normalized() + Vector3.Up * 0.35f);
            }
        }

        barrageReload -= deltaTime;
        if (barrageReload <= 0f && barrageLeft == 0 && ((CockpitCamera.Aiming && Input.WasActionPressed("Aim")) || TestBarrage))
        {
            TestBarrage = false;
            barrageReload = BarrageCooldown;
            barrageLeft = random.Next(BarrageMin, BarrageMax + 1);
            barrageTimer = 0f;
        }
        for (barrageTimer -= deltaTime; barrageLeft > 0 && barrageTimer <= 0f; barrageTimer += BarrageInterval)
        {
            --barrageLeft;
            LaunchRocket();
        }
    }

    // One rocket of the barrage, thrown out in a random upper-hemisphere direction biased toward the aim.
    private void LaunchRocket()
    {
        Vector3 start = transform.WorldPosition;
        Vector3 toAim = (AimPoint - start).Normalized();
        Vector3 scatter = new Vector3(Rand(-1f, 1f), Rand(0.3f, 1.2f), Rand(-1f, 1f)).Normalized();
        Vector3 direction = (scatter * 1.2f + toAim * 0.5f).Normalized();
        Entity rocket = World.Instantiate(RocketPrefab);
        if (rocket)
        {
            rocket.Transform.WorldPosition = start + direction * 0.4f;
            rocket.Transform.LookAt(start + direction * 2f);
        }
    }

    private float Rand(float min, float max) => min + (float)random.NextDouble() * (max - min);
}
