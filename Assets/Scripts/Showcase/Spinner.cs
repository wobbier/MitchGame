using ScriptCore;

// Turns the entity at a constant rate about one of its Euler axes (a kinematic Rigidbody follows,
// pushing what it meets).
public class Spinner : Script
{
    public float DegreesPerSecond = 45.0f;
    public int Axis = 1;   // 0 = X, 1 = Y, 2 = Z

    private float angle;

    public override void OnStart()
    {
        Vector3 rotation = transform.Rotation;
        angle = Axis == 0 ? rotation.x : (Axis == 1 ? rotation.y : rotation.z);
    }

    public override void OnUpdate(float deltaTime)
    {
        angle = (angle + DegreesPerSecond * deltaTime) % 360f;
        Vector3 rotation = transform.Rotation;
        transform.Rotation = Axis == 0 ? new Vector3(angle, rotation.y, rotation.z)
            : (Axis == 1 ? new Vector3(rotation.x, angle, rotation.z) : new Vector3(rotation.x, rotation.y, angle));
    }
}
