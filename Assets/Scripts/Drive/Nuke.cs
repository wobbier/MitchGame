using ScriptCore;

// The falling bomb: accelerates down and detonates on the first surface below it.
public class Nuke : Script
{
    public float Gravity = 25.0f;
    public float MaxFallSpeed = 90.0f;
    public string BlastPrefab = "Assets/Prefabs/Drive/NukeBlast.prefab";

    private float speed = 5.0f;

    public override void OnUpdate(float deltaTime)
    {
        float dt = Mathf.Min(deltaTime, 0.05f);
        speed = Mathf.Min(speed + Gravity * dt, MaxFallSpeed);
        Vector3 position = transform.WorldPosition;
        float step = speed * dt;
        if (Physics.Raycast(position, -Vector3.Up, step + 1.0f, out var hit) || position.y < -100f)
        {
            Entity blast = World.Instantiate(BlastPrefab);
            if (blast)
            {
                blast.Transform.WorldPosition = hit.Entity ? hit.Point : position;
            }
            Entity.Destroy();
            return;
        }
        transform.WorldPosition = position - Vector3.Up * step;
    }
}
