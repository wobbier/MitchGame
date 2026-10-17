using ScriptCore;

// A hand-held camera with three composed shots. Only this transform moves;
// scenery stays static so the renderer can reuse its batches and bounds.
public class LastTapeCamera : Script
{
    public float Sway = 0.12f;
    public float WalkSpeed = 2.5f;
    public float LookSpeed = 36f;

    private Vector3 position;
    private Vector3 destination;
    private float yaw;
    private float pitch;
    private float clock;
    private bool handheld = true;

    public override void OnStart()
    {
        position = destination = transform.WorldPosition;
        // Euler readback can flip pitch/roll on views past 90 degrees of yaw.
        Vector3 forward = transform.Forward;
        yaw = Mathf.Atan2(forward.x, forward.z) * Mathf.Rad2Deg;
        pitch = -Mathf.Atan2(forward.y, Mathf.Sqrt(forward.x * forward.x + forward.z * forward.z)) * Mathf.Rad2Deg;
    }

    public override void OnReload() => OnStart();

    private void Shot(Vector3 from, Vector3 to)
    {
        destination = from;
        Vector3 direction = to - from;
        yaw = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;
        pitch = -Mathf.Atan2(direction.y, Mathf.Sqrt(direction.x * direction.x + direction.z * direction.z)) * Mathf.Rad2Deg;
    }

    public override void OnUpdate(float deltaTime)
    {
        clock += deltaTime;
        if (Input.WasKeyPressed(KeyCode.Alpha1)) Shot(new Vector3(-7f, 2.2f, -7.8f), new Vector3(-1.2f, 1.3f, 10.5f));
        if (Input.WasKeyPressed(KeyCode.Alpha2)) Shot(new Vector3(-3.8f, 1.65f, 2.1f), new Vector3(-2.8f, 1.65f, 10.8f));
        if (Input.WasKeyPressed(KeyCode.Alpha3)) Shot(new Vector3(4.5f, 2.25f, -3.5f), new Vector3(-2.5f, 1.5f, 9.5f));
        if (Input.WasKeyPressed(KeyCode.Space)) handheld = !handheld;

        float turn = (Input.IsKeyDown(KeyCode.RightArrow) ? 1f : 0f) - (Input.IsKeyDown(KeyCode.LeftArrow) ? 1f : 0f);
        float tilt = (Input.IsKeyDown(KeyCode.DownArrow) ? 1f : 0f) - (Input.IsKeyDown(KeyCode.UpArrow) ? 1f : 0f);
        yaw += turn * LookSpeed * deltaTime;
        pitch = Mathf.Clamp(pitch + tilt * LookSpeed * deltaTime, -65f, 65f);
        float angle = yaw * Mathf.Deg2Rad;
        Vector3 forward = new Vector3(Mathf.Sin(angle), 0f, Mathf.Cos(angle));
        Vector3 right = new Vector3(Mathf.Cos(angle), 0f, -Mathf.Sin(angle));
        float speed = WalkSpeed * (Input.IsKeyDown(KeyCode.LeftShift) ? 3f : 1f) * deltaTime;
        if (Input.IsKeyDown(KeyCode.W)) destination += forward * speed;
        if (Input.IsKeyDown(KeyCode.S)) destination -= forward * speed;
        if (Input.IsKeyDown(KeyCode.D)) destination += right * speed;
        if (Input.IsKeyDown(KeyCode.A)) destination -= right * speed;
        if (Input.IsKeyDown(KeyCode.E)) destination += Vector3.Up * speed;
        if (Input.IsKeyDown(KeyCode.Q)) destination -= Vector3.Up * speed;
        destination.y = Mathf.Clamp(destination.y, 0.4f, 12f);
        position = Mathf.Damp(position, destination, 0.14f, deltaTime);

        float sway = handheld ? Sway : 0f;
        transform.WorldPosition = position + new Vector3(Mathf.Sin(clock * 0.63f) * sway * 0.2f,
                                                         Mathf.Sin(clock * 1.13f) * sway * 0.12f, 0f);
        transform.Rotation = new Vector3(pitch + Mathf.Sin(clock * 0.9f) * sway,
                                        yaw + Mathf.Sin(clock * 0.57f) * sway * 1.4f,
                                        Mathf.Sin(clock * 0.41f) * sway * 0.4f);
    }
}
