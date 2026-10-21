using ScriptCore;

// Driver's-seat FPS look: parented to the car body, the mouse (or right stick) turns the head.
// The cursor is captured while driving; Pause (Escape) releases it and clicking recaptures it.
// Its forward is the aim for MissileLauncher.
public class CockpitCamera : Script
{
    public float Sensitivity = 1.0f;
    public bool InvertY = false;
    public float MaxYaw = 150.0f;
    public float MinPitch = -60.0f;
    public float MaxPitch = 60.0f;
    public float StartYaw = 0.0f;

    // False while the cursor is released, so a click to recapture doesn't also fire.
    public static bool Aiming;

    private float yaw;
    private float pitch;
    private float shakeTime;

    public override void OnStart()
    {
        // Keep the pitch the camera was placed with in the editor.
        pitch = transform.Rotation.x;
        yaw = StartYaw;
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
        transform.Rotation = new Vector3(pitch + Mathf.Sin(t * 47f) * shake, yaw + Mathf.Sin(t * 39f + 1.3f) * shake,
                                         Mathf.Sin(t * 31f + 2.1f) * shake * 0.5f);
    }
}
