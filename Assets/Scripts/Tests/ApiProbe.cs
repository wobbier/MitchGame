using ScriptCore;

// Drives ApiTest.lvl / ApiFlows.edscript (CS-5): entity queries (by component, by name, children,
// GUIDs, layers), AddComponent for a component with no C# wrapper, the application calls, and the
// math types against the engine's own rotation.
public class ApiProbe : Script
{
    public override void OnStart()
    {
        // (h) A hierarchy made here, a component the bindings never registered by hand.
        Entity parent = World.CreateEntity("Probe Parent");
        for (int i = 0; i < 2; ++i)
        {
            Entity child = World.CreateEntity($"Probe Child {i}");
            child.Transform.Parent = parent;
        }
        parent.AddComponent("Light");
        Debug.Log($"ApiProbe: light added {parent.HasComponent("Light")}, lights {Query.WithComponent("Light").Length}");
        Debug.Log($"ApiProbe: children {parent.Children.Length}, named {Query.Named("Probe Child 1").Length}");
        parent.Layer = 3;
        Debug.Log($"ApiProbe: layer {parent.Layer}, guid length {parent.Guid.Length}");

        // (j) The application: the window's there, rumble without a pad says no.
        Debug.Log($"ApiProbe: window {(App.WindowSize.x > 0f ? "sized" : "missing")}, rumble {App.Rumble(0, 0.5f, 0.5f, 0.1f)}");

        // (k) A C# rotation matches the engine's for the same Euler angles.
        var euler = new Vector3(20f, 35f, 50f);
        transform.Rotation = euler;
        var engineForward = transform.Forward;
        var scriptForward = Quaternion.Euler(euler) * new Vector3(0f, 0f, 1f);
        Debug.Log($"ApiProbe: forward matches {(engineForward - scriptForward).Length() < 1e-3f}");
        var rng = new Rng(42, 54);
        Debug.Log($"ApiProbe: pcg {rng.NextUInt():x8}");

        // (b, c) An audio source with no clip, and a stopped particle system that bursts.
        Entity fx = World.CreateEntity("Probe Effects");
        var audio = fx.AddComponent<AudioSource>();
        audio.Play();
        Debug.Log($"ApiProbe: audio without a clip playing {audio.IsPlaying}");
        var particles = fx.AddComponent<ParticleSystem>();
        particles.Stop();
        Burst(particles);
    }

    private async void Burst(ParticleSystem particles)
    {
        await Async.Frames(2, this);
        // (f) The wall at z = 5 (layer 0): masked rays see it or don't, a sphere sweep and a box find it.
        Entity wall = World.Find("Probe Wall");
        bool seen = Physics.Raycast(new Vector3(0f, 0f, -2f), new Vector3(0f, 0f, 1f), 50f, Physics.LayerMask(0), out RaycastHit hit);
        bool masked = Physics.Raycast(new Vector3(0f, 0f, -2f), new Vector3(0f, 0f, 1f), 50f, Physics.LayerMask(5), out _);
        int all = Physics.RaycastAll(new Vector3(0f, 0f, -2f), new Vector3(0f, 0f, 1f), 50f).Length;
        bool swept = Physics.SphereCast(new Vector3(1.5f, 0f, -2f), 0.5f, new Vector3(0f, 0f, 1f), 50f, out _);
        int boxed = Physics.OverlapBox(new Vector3(0f, 0f, 5f), new Vector3(0.5f, 0.5f, 0.5f), new Vector3(0f, 45f, 0f)).Length;
        Debug.Log($"ApiProbe: ray hits wall {seen && hit.Entity == wall} at {hit.Distance:F2}, masked out {!masked}, all {all}, sphere {swept}, box {boxed}");
        particles.Burst(25);
        await Async.Frames(2, this);
        Debug.Log($"ApiProbe: particles after a burst {particles.ParticleCount}");

        // (g) 2D: a ray down finds the ground under the ball's column, the ball takes a velocity.
        Entity ground = World.Find("Probe Ground 2D");
        Entity ball = World.Find("Probe Ball 2D");
        bool down = Physics2D.Raycast(new Vector2(18f, 0f), new Vector2(0f, -1f), 10f, out RaycastHit hit2d);
        var body = ball.GetComponent<Rigidbody2D>();
        body.Velocity = new Vector2(4f, 0f);
        await Async.Frames(2, this);
        Debug.Log($"ApiProbe: 2D ray hits ground {down && hit2d.Entity == ground}, point {Physics2D.OverlapPoint(new Vector2(20f, -2f)).Length}, ball moving right {body.Velocity.x > 1f}");

        // (e) The main camera: a point straight ahead lands mid-screen, one to its right lands right
        // of centre, and the ray back through that pixel passes through the point.
        var cam = World.Find("Main Camera").GetComponent<Camera>();
        Vector2 size = cam.OutputSize;
        Vector3 ahead = cam.transform.Position + cam.transform.Forward * 10f;
        Vector3 onScreen = cam.WorldToScreen(ahead);
        Vector3 right = cam.WorldToScreen(ahead + cam.transform.Right * 2f);
        cam.ScreenToRay(new Vector2(right.x, right.y), out Vector3 origin, out Vector3 dir);
        Vector3 target = ahead + cam.transform.Right * 2f;
        float miss = Vector3.Cross(target - origin, dir).Length();
        bool centred = System.Math.Abs(onScreen.x - size.x / 2f) < 1f && System.Math.Abs(onScreen.y - size.y / 2f) < 1f;
        Debug.Log($"ApiProbe: camera centred {centred}, depth {onScreen.z:F1}, right of centre {right.x > size.x / 2f}, ray through point {miss < 0.01f}, fov {cam.FieldOfView:F0}");
        // (d) and lights: a mesh's own material and a light's fields.
        var mesh = World.Find("Probe Cube").GetComponent<Mesh>();
        mesh.SetMaterial("DiffuseColor", new Vector3(1f, 0f, 0f));
        var light = World.Find("Probe Parent").GetComponent<Light>();
        light.Intensity = 3.5f;
        Debug.Log($"ApiProbe: material red {mesh.GetMaterial<Vector3>("DiffuseColor").x:F1}{mesh.GetMaterial<Vector3>("DiffuseColor").y:F1}, light {light.Intensity:F1}");
    }
}
