using ScriptCore;

// Turns the entity at a constant rate about one of its local axes (a kinematic Rigidbody follows,
// pushing what it meets).
public class Spinner : Script
{
    public float DegreesPerSecond = 45.0f;
    public int Axis = 1;   // 0 = X, 1 = Y, 2 = Z

    public override void OnUpdate(float deltaTime)
    {
        float delta = DegreesPerSecond * deltaTime;
        transform.Rotate(Axis == 0 ? new Vector3(delta, 0, 0)
            : (Axis == 1 ? new Vector3(0, delta, 0) : new Vector3(0, 0, delta)));
    }
}
