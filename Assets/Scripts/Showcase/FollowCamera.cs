using ScriptCore;

// Orbiting third-person camera: Look turns it around the target, it eases after the target, and
// it pulls in when geometry is between the target and the camera.
public class FollowCamera : Script
{
    public string Target = "Player";
    public float Distance = 7.0f;
    public float Height = 1.5f;
    public float Yaw = 0.0f;
    public float Pitch = 20.0f;
    public float Sensitivity = 0.15f;
    public float FollowHalfLife = 0.05f;

    private Entity target;

    public override void OnStart()
    {
        target = World.Find(Target);
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnUpdate(float deltaTime)
    {
        if (!target)
        {
            return;
        }
        Vector2 look = Input.GetActionVector2("Look");
        Yaw += look.x * Sensitivity;
        Pitch = Mathf.Clamp(Pitch - look.y * Sensitivity, -10f, 70f);

        float yaw = Yaw * Mathf.Deg2Rad;
        float pitch = Pitch * Mathf.Deg2Rad;
        Vector3 forward = new Vector3(Mathf.Sin(yaw) * Mathf.Cos(pitch), -Mathf.Sin(pitch), Mathf.Cos(yaw) * Mathf.Cos(pitch));
        Vector3 pivot = target.Transform.WorldPosition + Vector3.Up * Height;

        // Keep a little clear of walls between the pivot and the camera.
        float distance = Distance;
        if (Physics.Raycast(pivot, -forward, Distance, out var hit) && hit.Entity != target)
        {
            distance = Mathf.Max(hit.Distance - 0.3f, 0.5f);
        }
        Vector3 desired = pivot - forward * distance;
        transform.WorldPosition = Mathf.Damp(transform.WorldPosition, desired, FollowHalfLife, deltaTime);
        transform.LookAt(pivot);
    }
}
