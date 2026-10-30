using ScriptCore;

public readonly record struct PortalBallFired(Entity Camera);

// Camera-mounted viewmodel. Recoil is an analytic impulse, so fast clicks stay bounded and
// recovery looks the same at different frame rates. Mouse buttons relocate the linked portals.
public class PortalGun : Script
{
    public float Cooldown = 0.24f;
    public bool TestFire = false;
    [HideInInspector] public float RestFieldOfView;

    private Transform barrel, rotor, flash, turbine;
    private UIModel hud;
    private float statusTime;
    private readonly Transform[] claws = new Transform[3];
    private readonly Mesh[] energy = new Mesh[5];
    private Entity light;
    private Camera camera;
    private float time, age = 10f, reload, spin;
    private float handedness = 1f;
    private bool wasCaptured;
    private System.IDisposable ballSubscription;

    public override void OnStart()
    {
        hud = UI.Model("portalgun");
        hud.Set("status", ChamberController.Active != null ? "WHITE PANELS ACCEPT PORTALS" : "AIM AT A LARGE, FLAT SURFACE");
        hud.Set("failed", false);
        turbine = World.GetTransformByName("Gun Turbine");
        barrel = World.GetTransformByName("Gun Barrel");
        rotor = World.GetTransformByName("Gun Rotor");
        flash = World.GetTransformByName("Gun Flash");
        for (int i = 0; i < claws.Length; ++i)
            claws[i] = World.GetTransformByName("Gun Claw " + i);
        string[] names = { "Gun Core", "Gun Flash", "Gun Rail Left", "Gun Rail Right", "Gun Muzzle" };
        for (int i = 0; i < energy.Length; ++i)
            energy[i] = World.Find(names[i]).GetComponent<Mesh>();
        light = World.Find("Gun Pulse Light");
        camera = transform.Parent.GetComponent<Camera>();
        if (camera != null && RestFieldOfView <= 0f) RestFieldOfView = camera.FieldOfView;
        ballSubscription?.Dispose();
        ballSubscription = On<PortalBallFired>(e =>
        {
            if (e.Camera == transform.Parent) Kick(false);
        });
    }

    public override void OnReload() { OnStart(); }

    public override void OnDestroy()
    {
        ballSubscription?.Dispose();
        if (camera != null && camera.Exists) camera.FieldOfView = RestFieldOfView;
    }

    private void Kick(bool orange)
    {
        age = 0f;
        handedness = orange ? -1f : 1f;
        Vector3 color = orange ? new Vector3(1f, 0.19f, 0.025f) : new Vector3(0.02f, 0.55f, 1f);
        foreach (Mesh mesh in energy)
        {
            mesh?.SetMaterial("EmissiveColor", color);
            mesh?.SetMaterial("DiffuseColor", color);
        }
        if (light) light.SetField("Light", "Color", color);
        Audio.PlayOneShot("Assets/Sounds/Portals/Pulse.wav", 0.7f);
    }

    public override void OnUpdate(float deltaTime)
    {
        time += deltaTime;
        age += deltaTime;
        reload -= deltaTime;
        statusTime -= deltaTime;
        if (statusTime <= 0f)
        {
            hud.Set("status", ChamberController.Active != null ? "WHITE PANELS ACCEPT PORTALS" : "AIM AT A LARGE, FLAT SURFACE");
            hud.Set("failed", false);
        }
        bool captured = Input.MouseCaptured;
        bool ready = captured && wasCaptured;
        wasCaptured = captured;
        if (reload <= 0f && ((ready && (Input.WasActionPressed("Fire") || Input.WasActionPressed("Aim"))) || TestFire))
        {
            reload = Mathf.Max(0.1f, Cooldown);
            bool orange = Input.WasActionPressed("Aim");
            Kick(orange);
            Transform view = camera.transform;
            bool placed = PortalPlacement.Shoot(orange ? "Orange Portal" : "Blue Portal", view.WorldPosition, view.Forward, out Vector3 impact);
            string status = orange ? "ORANGE PORTAL LINKED" : "BLUE PORTAL LINKED";
            if (placed && Portal.Instances.TryGetValue(orange ? "Blue Portal" : "Orange Portal", out Portal other)
                && other.RequirePlacement && !other.IsPlaced)
                status = orange ? "ORANGE READY - PLACE BLUE" : "BLUE READY - PLACE ORANGE";
            hud.Set("status", placed ? status : "PORTAL WON'T FIT HERE");
            hud.Set("failed", !placed);
            statusTime = 1.2f;
            Entity shot = World.Instantiate("Assets/Prefabs/Portals/PortalShot.prefab");
            if (shot)
            {
                Vector3 start = flash.WorldPosition;
                Vector3 delta = impact - start;
                shot.Transform.WorldPosition = (start + impact) * 0.5f;
                shot.Transform.LookDirection(delta.Normalized(), Vector3.Up);
                shot.Transform.Scale = new Vector3(0.012f, 0.012f, delta.Length() * 0.5f);
                Vector3 color = orange ? new Vector3(1, 0.19f, 0.025f) : new Vector3(0.02f, 0.55f, 1);
                shot.GetComponent<Mesh>()?.SetMaterial("EmissiveColor", color);
            }
        }
    }

    public override void OnLateUpdate(float deltaTime)
    {
        float decay = (float)System.Math.Exp(-age * 13f);
        float kick = decay * Mathf.Sin(Mathf.Min(age * 42f, 2.8f));
        float rattle = decay * Mathf.Sin(age * 105f);
        Vector2 move = Input.GetActionVector2("Move");
        Vector2 look = Input.MouseCaptured ? Input.GetActionVector2("Look") : new Vector2();
        float walking = Mathf.Clamp01(move.x * move.x + move.y * move.y);
        float bob = Mathf.Sin(time * 11f) * 0.008f * walking;
        transform.Position = new Vector3(0.24f + rattle * 0.012f, -0.23f + bob + kick * 0.045f, 0.48f - kick * 0.13f);
        transform.Rotation = new Vector3(-kick * 19f - Mathf.Clamp(look.y, -4f, 4f) * 0.4f,
            Mathf.Clamp(look.x, -4f, 4f) * -0.5f, kick * handedness * 11f + bob * 90f);
        if (barrel != null) barrel.Position = new Vector3(0f, 0f, 0.12f - decay * 0.085f);
        spin += deltaTime * (35f + decay * 1600f);
        if (turbine != null) turbine.Rotation = new Vector3(0f, 0f, -spin * 0.7f % 360f);
        if (rotor != null) rotor.Rotation = new Vector3(0f, 0f, spin % 360f);
        for (int i = 0; i < claws.Length; ++i)
        {
            if (claws[i] == null) continue;
            float angle = i * 120f * Mathf.Deg2Rad;
            float radius = 0.09f + decay * 0.055f;
            claws[i].Position = new Vector3(Mathf.Cos(angle) * radius, Mathf.Sin(angle) * radius, 0.24f - decay * 0.035f);
            claws[i].Rotation = new Vector3(decay * 24f * Mathf.Sin(angle), -decay * 24f * Mathf.Cos(angle), i * 120f);
        }
        float flare = Mathf.Clamp01(1f - age / 0.065f);
        float flashSize = Mathf.Max(0.0001f, flare);
        if (flash != null) flash.Scale = new Vector3(0.10f * flashSize, 0.10f * flashSize, 0.22f * flashSize);
        if (light) light.SetField("Light", "Intensity", flare * 7f);
        energy[0]?.SetMaterial("EmissiveIntensity", 2f + decay * 7f + Mathf.Sin(time * 4f) * 0.3f);
        if (camera != null) camera.FieldOfView = RestFieldOfView + decay * 1.8f;
    }
}
