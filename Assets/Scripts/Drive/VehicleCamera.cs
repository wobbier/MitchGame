using ScriptCore;

// Chase camera: eases in behind the target's heading, Look orbits it for a while before it
// swings back, and it pulls in when the terrain is between the car and the camera.
public class VehicleCamera : Script
{
    public string Target = "Vehicle";
    public float Distance = 9.0f;
    public float Height = 3.2f;
    public float LookHeight = 1.2f;
    public float FollowHalfLife = 0.12f;
    public float Sensitivity = 0.15f;
    public float RecenterDelay = 1.5f;

    private Entity target;
    private float orbit;
    private float idle;

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
        if (Mathf.Abs(look.x) > 0.01f)
        {
            orbit += look.x * Sensitivity;
            idle = 0f;
        }
        else if ((idle += deltaTime) > RecenterDelay)
        {
            orbit = Mathf.Damp(orbit, 0f, 0.3f, deltaTime);
        }

        Vector3 heading = target.Transform.Forward;
        float angle = Mathf.Atan2(heading.x, heading.z) + orbit * Mathf.Deg2Rad;
        Vector3 back = new Vector3(Mathf.Sin(angle), 0f, Mathf.Cos(angle));
        Vector3 pivot = target.Transform.WorldPosition + Vector3.Up * LookHeight;
        Vector3 offset = Vector3.Up * Height - back * Distance;

        float distance = offset.Length();
        Vector3 direction = offset / distance;
        if (Physics.Raycast(pivot, direction, distance, out var hit) && hit.Entity != target)
        {
            distance = Mathf.Max(hit.Distance - 0.4f, 1.0f);
        }
        Vector3 desired = pivot + direction * distance;
        transform.WorldPosition = Mathf.Damp(transform.WorldPosition, desired, FollowHalfLife, deltaTime);
        transform.LookAt(pivot);
    }
}
