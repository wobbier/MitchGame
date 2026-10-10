using ScriptCore;

// Drives ScriptTest.lvl / ScriptFlows.edscript: every effect is visible on the entity's Transform,
// so the editor script can assert the lifecycle and the engine API from outside.
public class ScriptProbe : Script
{
    public float RiseSpeed = 1.0f;
    public int FixedSteps = 0;
    public string GroundName = "";

    public override void OnStart()
    {
        // Physics + entity names: grow when the ray down finds the ground by name.
        var origin = transform.WorldPosition;
        if (Physics.Raycast(origin, new Vector3(0, -1, 0), 50.0f, out var hit))
        {
            GroundName = hit.Entity.Name;
            if (GroundName == "Ground")
            {
                transform.Scale = new Vector3(2, 2, 2);
            }
        }
        Debug.Log($"ScriptProbe started on {Entity.Name}, ground '{GroundName}'");
    }

    public override void OnFixedUpdate(float fixedDeltaTime)
    {
        FixedSteps++;
        // Turns 1 degree per fixed step about Y.
        var rotation = transform.Rotation;
        transform.Rotation = new Vector3(rotation.x, FixedSteps, rotation.z);
    }

    public override void OnUpdate(float deltaTime)
    {
        var position = transform.Position;
        transform.Position = new Vector3(position.x, position.y + RiseSpeed * Time.DeltaTime, position.z);
        Debug.DrawLine(transform.WorldPosition, transform.WorldPosition + transform.Forward, new Vector3(1, 1, 0));
    }
}
