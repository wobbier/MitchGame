using ScriptCore;

// The Lost Temple's camera: a slow cinematic tour through seven framed shots, or free flight.
//   1-7 jump to a shot, T toggles the tour, Space the hand-held sway,
//   WASD / Q E fly, arrows look, Left Shift is faster. Any movement key leaves the tour.
public class LostTempleCamera : Script
{
    public bool Tour = true;
    // The shot the tour is on (0-6): the starting shot, and kept across hot reloads.
    public int Shot = 0;
    public float Hold = 9.0f;
    public float Blend = 4.5f;
    public float Sway = 0.18f;
    public float FlySpeed = 4.0f;
    public float LookSpeed = 45.0f;

    // The shot table lives in LostTempleShots.cs (generated with the scene).
    private static Vector3[] From => LostTempleShots.From;
    private static Vector3[] To => LostTempleShots.To;

    private float shotTime;
    private float blendTime = -1f;
    private Vector3 blendFromPos;
    private float blendFromYaw, blendFromPitch;
    private Vector3 position;
    private float yaw, pitch;
    private float clock;
    private bool handheld = true;

    public override void OnStart()
    {
        Cut(Shot);
    }

    // A reload makes a new instance: ease back into the current shot from wherever the camera is.
    public override void OnReload()
    {
        position = transform.WorldPosition;
        Vector3 forward = transform.Forward;
        yaw = Mathf.Atan2(forward.x, forward.z) * Mathf.Rad2Deg;
        pitch = -Mathf.Atan2(forward.y, Mathf.Sqrt(forward.x * forward.x + forward.z * forward.z)) * Mathf.Rad2Deg;
        Go(Shot);
    }

    private static void Angles(Vector3 from, Vector3 to, out float yawOut, out float pitchOut)
    {
        Vector3 d = to - from;
        yawOut = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
        pitchOut = -Mathf.Atan2(d.y, Mathf.Sqrt(d.x * d.x + d.z * d.z)) * Mathf.Rad2Deg;
    }

    private void Cut(int index)
    {
        Shot = ((index % From.Length) + From.Length) % From.Length;
        shotTime = 0f;
        blendTime = -1f;
        position = From[Shot];
        Angles(From[Shot], To[Shot], out yaw, out pitch);
    }

    private void Go(int index)
    {
        blendFromPos = position;
        blendFromYaw = yaw;
        blendFromPitch = pitch;
        Shot = ((index % From.Length) + From.Length) % From.Length;
        shotTime = 0f;
        blendTime = 0f;
    }

    // Each shot drifts gently towards its subject while it holds.
    private Vector3 ShotPosition(int index, float t)
    {
        Vector3 toward = To[index] - From[index];
        float drift = Mathf.Min(t / (Hold + Blend), 1f) * 0.07f;
        return From[index] + toward * drift + new Vector3(0f, t * 0.03f, 0f);
    }

    private static float Smooth(float t) => t * t * (3f - 2f * t);

    private static float WrapAngle(float a)
    {
        while (a > 180f) a -= 360f;
        while (a < -180f) a += 360f;
        return a;
    }

    public override void OnUpdate(float deltaTime)
    {
        clock += deltaTime;
        KeyCode[] keys = { KeyCode.Alpha1, KeyCode.Alpha2, KeyCode.Alpha3, KeyCode.Alpha4, KeyCode.Alpha5, KeyCode.Alpha6, KeyCode.Alpha7 };
        for (int i = 0; i < keys.Length; ++i)
        {
            if (Input.WasKeyPressed(keys[i])) Go(i);
        }
        if (Input.WasKeyPressed(KeyCode.T)) Tour = !Tour;
        if (Input.WasKeyPressed(KeyCode.Space)) handheld = !handheld;

        float turn = (Input.IsKeyDown(KeyCode.RightArrow) ? 1f : 0f) - (Input.IsKeyDown(KeyCode.LeftArrow) ? 1f : 0f);
        float tilt = (Input.IsKeyDown(KeyCode.DownArrow) ? 1f : 0f) - (Input.IsKeyDown(KeyCode.UpArrow) ? 1f : 0f);
        float a = yaw * Mathf.Deg2Rad;
        Vector3 forward = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
        Vector3 right = new Vector3(Mathf.Cos(a), 0f, -Mathf.Sin(a));
        Vector3 move = new Vector3(0f, 0f, 0f);
        if (Input.IsKeyDown(KeyCode.W)) move += forward;
        if (Input.IsKeyDown(KeyCode.S)) move -= forward;
        if (Input.IsKeyDown(KeyCode.D)) move += right;
        if (Input.IsKeyDown(KeyCode.A)) move -= right;
        if (Input.IsKeyDown(KeyCode.E)) move += Vector3.Up;
        if (Input.IsKeyDown(KeyCode.Q)) move -= Vector3.Up;
        bool flying = turn != 0f || tilt != 0f || move.x != 0f || move.y != 0f || move.z != 0f;
        if (flying)
        {
            Tour = false;
            blendTime = -1f;
            yaw += turn * LookSpeed * deltaTime;
            pitch = Mathf.Clamp(pitch + tilt * LookSpeed * deltaTime, -80f, 80f);
            position += move * FlySpeed * (Input.IsKeyDown(KeyCode.LeftShift) ? 3f : 1f) * deltaTime;
        }
        else if (blendTime >= 0f)
        {
            blendTime += deltaTime;
            float k = Smooth(Mathf.Min(blendTime / Blend, 1f));
            Angles(From[Shot], To[Shot], out float toYaw, out float toPitch);
            position = Mathf.Lerp(blendFromPos, ShotPosition(Shot, 0f), k);
            yaw = blendFromYaw + WrapAngle(toYaw - blendFromYaw) * k;
            pitch = Mathf.Lerp(blendFromPitch, toPitch, k);
            if (blendTime >= Blend) blendTime = -1f;
        }
        else if (Tour || shotTime < Hold)
        {
            shotTime += deltaTime;
            position = ShotPosition(Shot, shotTime);
            Angles(position, To[Shot], out yaw, out pitch);
            if (Tour && shotTime >= Hold) Go((Shot + 1) % From.Length);
        }

        float sway = handheld ? Sway : 0f;
        transform.WorldPosition = position + new Vector3(Mathf.Sin(clock * 0.63f) * sway * 0.12f,
                                                         Mathf.Sin(clock * 1.07f) * sway * 0.08f, 0f);
        transform.Rotation = new Vector3(pitch + Mathf.Sin(clock * 0.91f) * sway,
                                         yaw + Mathf.Sin(clock * 0.53f) * sway * 1.3f,
                                         Mathf.Sin(clock * 0.37f) * sway * 0.5f);
    }
}
