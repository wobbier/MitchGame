using System.Collections.Generic;
using ScriptCore;

// Left click throws a physics ball where the camera looks. Goes on the player's camera. Balls are
// ordinary rigidbodies, so they bounce around and fly through Portals like anything else; the
// oldest is removed once there are more than MaxBalls.
public class BallLauncher : Script
{
    public string BallPrefab = "Assets/Prefabs/Portals/PortalBall.prefab";
    public float Speed = 14.0f;
    public float Cooldown = 0.15f;
    public int MaxBalls = 40;
    // Inherit the thrower's motion, so balls don't lag behind when you run and throw.
    public string Thrower = "Player";

    private readonly Queue<Entity> balls = new Queue<Entity>();
    private CharacterController thrower;
    private float reload;
    private bool wasCaptured;

    public override void OnStart()
    {
        Entity body = World.Find(Thrower);
        thrower = body ? body.GetComponent<CharacterController>() : null;
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnUpdate(float deltaTime)
    {
        reload -= deltaTime;
        // The click that captures the cursor shouldn't also throw.
        bool captured = Input.MouseCaptured;
        bool canThrow = captured && wasCaptured;
        wasCaptured = captured;
        if (!canThrow || reload > 0f || !Input.WasActionPressed("Fire"))
        {
            return;
        }
        reload = Cooldown;

        Entity ball = World.Instantiate(BallPrefab);
        if (!ball)
        {
            return;
        }
        Vector3 aim = transform.Forward;
        ball.Transform.WorldPosition = transform.WorldPosition + aim * 0.6f;
        Vector3 velocity = aim * Speed;
        if (thrower != null)
        {
            velocity = velocity + thrower.Velocity;
        }
        ball.GetComponent<Rigidbody>().Velocity = velocity;

        balls.Enqueue(ball);
        while (balls.Count > MaxBalls)
        {
            Entity oldest = balls.Dequeue();
            if (oldest)
            {
                oldest.Destroy();
            }
        }
    }
}
