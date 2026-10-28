using ScriptCore;

// Driver's-seat FPS look: parented to the car body, the mouse (or right stick) turns the head.
// The cursor is captured while driving; Pause (Escape) releases it and clicking recaptures it.
// Its forward is the aim for MissileLauncher. The head rides a spring: it sways against the car's
// acceleration, drops on landings, rumbles with speed and glances into turns.
public class CockpitCamera : Script
{
    public float Sensitivity = 1.0f;
    public bool InvertY = false;
    public float MaxYaw = 150.0f;
    public float MinPitch = -60.0f;
    public float MaxPitch = 60.0f;
    public float StartYaw = 0.0f;
    public float LeanPerAccel = 0.01f;
    public float HeadTiltPerAccel = 0.3f;
    public float HeadStiffness = 70.0f;
    public float HeadDamping = 10.0f;
    public float LandingJolt = 0.12f;
    public float Rumble = 0.012f;
    public float LookIntoTurn = 10.0f;

    // False while the cursor is released, so a click to recapture doesn't also fire.
    public static bool Aiming;
    // Set while something else (CarCrash) owns the camera: the head and look stop updating.
    public static bool Suspended;

    private float yaw;
    private float pitch;
    private float shakeTime;
    private Vector3 basePosition;
    private Vector3 head;
    private Vector3 headVelocity;
    private float turnLook;
    private float tilt;
    private int landings = -1;

    public override void OnStart()
    {
        // Keep the pitch the camera was placed with in the editor.
        pitch = transform.Rotation.x;
        yaw = StartYaw;
        basePosition = transform.Position;
        Input.MouseCaptured = true;
        Aiming = true;
    }

    public override void OnDestroy()
    {
        Input.MouseCaptured = false;
        Aiming = false;
    }

    public override void OnUpdate(float deltaTime)
    {
        if (Suspended)
        {
            Aiming = false;
            return;
        }
        UpdateHead(deltaTime);
        if (Input.WasActionPressed("Pause"))
        {
            Input.MouseCaptured = false;
        }
        else if (!Input.MouseCaptured && (Input.WasActionPressed("Fire") || Input.WasActionPressed("Aim")))
        {
            Input.MouseCaptured = true;
            Aiming = false;
            return;
        }
        if (!Input.MouseCaptured)
        {
            Aiming = false;
            return;
        }
        if (!Aiming && !Input.IsActionPressed("Fire") && !Input.IsActionPressed("Aim"))
        {
            Aiming = true;
        }

        // Look is +Y up; positive pitch looks down.
        Vector2 look = Input.GetActionVector2("Look");
        yaw = Mathf.Clamp(yaw + look.x * Sensitivity, -MaxYaw, MaxYaw);
        pitch = Mathf.Clamp(pitch + (InvertY ? look.y : -look.y) * Sensitivity, MinPitch, MaxPitch);
        float shake = NukeBlast.Shake;
        float t = (shakeTime += deltaTime);
        transform.Rotation = new Vector3(pitch + Mathf.Sin(t * 47f) * shake, yaw + turnLook + Mathf.Sin(t * 39f + 1.3f) * shake,
                                         tilt + Mathf.Sin(t * 31f + 2.1f) * shake * 0.5f);
    }

    // Spring the head toward where the car's acceleration throws it (in the body's frame: x
    // right, y up, z forward), kick it down on landings and add a speed-scaled road rumble.
    private void UpdateHead(float deltaTime)
    {
        VehicleController car = VehicleController.Active;
        if (car == null)
        {
            return;
        }
        float dt = Mathf.Min(deltaTime, 0.05f);
        Vector3 accel = car.LocalAcceleration;
        Vector3 target = new Vector3(-accel.x, 0f, -accel.z) * LeanPerAccel;
        if (landings >= 0 && car.Landings != landings)
        {
            headVelocity.y -= Mathf.Min(car.LandingSpeed, 20f) * LandingJolt;
        }
        landings = car.Landings;
        headVelocity += ((target - head) * HeadStiffness - headVelocity * HeadDamping) * dt;
        head += headVelocity * dt;
        head = new Vector3(Mathf.Clamp(head.x, -0.15f, 0.15f), Mathf.Clamp(head.y, -0.2f, 0.1f), Mathf.Clamp(head.z, -0.15f, 0.15f));

        float t = shakeTime;
        float speed01 = Mathf.Clamp01(Mathf.Abs(car.Speed) / car.MaxSpeed);
        float rumble = car.Grounded ? Rumble * speed01 : 0f;
        Vector3 jitter = new Vector3(Mathf.Sin(t * 23f) + Mathf.Sin(t * 57f + 0.7f) * 0.5f, Mathf.Sin(t * 31f + 1.9f) + Mathf.Sin(t * 71f) * 0.5f, 0f) * rumble;
        transform.Position = basePosition + head + jitter;

        // Glance into the turn and tip the head with the cornering load.
        turnLook = Mathf.Damp(turnLook, car.Steer * LookIntoTurn * Mathf.Clamp01(Mathf.Abs(car.Speed) / 8f), 0.15f, dt);
        tilt = Mathf.Damp(tilt, Mathf.Clamp(-accel.x * HeadTiltPerAccel, -5f, 5f), 0.1f, dt);
    }
}
