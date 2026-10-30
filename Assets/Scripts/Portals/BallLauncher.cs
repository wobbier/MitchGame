using System.Collections.Generic;
using ScriptCore;

// E (Interact) throws a physics ball where the camera looks. Goes on the player's camera. Balls are
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
    public static BallLauncher Active;

    private readonly Queue<Entity> balls = new Queue<Entity>();
    private CharacterController thrower;
    private float reload;
    private bool wasCaptured;
    private Entity gun;

    public override void OnStart()
    {
        Active = this;
        UIModel hud = UI.Model("portalgun");
        hud.Set("status", "AIM AT A LARGE, FLAT SURFACE");
        hud.Set("failed", false);
        if (!gun)
        {
            Entity existing = World.Find("Portal Gun");
            if (existing && existing.Transform.Parent == Entity) gun = existing;
        }
        if (!gun)
            gun = World.Instantiate("Assets/Prefabs/Portals/PortalGun.prefab", Entity);
        Entity body = World.Find(Thrower);
        thrower = body ? body.GetComponent<CharacterController>() : null;
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnDestroy()
    {
        if (Active == this) Active = null;
        if (gun) gun.Destroy();
    }

    public override void OnUpdate(float deltaTime)
    {
        reload -= deltaTime;
        // Only accept gameplay input while the cursor is captured.
        bool captured = Input.MouseCaptured;
        bool canThrow = captured && wasCaptured;
        wasCaptured = captured;
        if (!canThrow || reload > 0f || !Input.WasActionPressed("Interact"))
        {
            return;
        }
        FireBall();
    }

    // The same launch path is used by E and the chamber's end-to-end gameplay probe.
    public Entity FireBall()
    {
        if (reload > 0f) return Entity.Null;
        reload = Cooldown;
        Entity ball = World.Instantiate(BallPrefab);
        if (!ball) return Entity.Null;
        // Chamber energy balls follow the aim ray so a shot from the normal starting area
        // reaches the portal instead of dropping to the floor before the opening.
        if (ChamberController.Active != null) ball.SetField("Rigidbody", "GravityScale", 0f);
        Vector3 aim = transform.Forward;
        ball.Transform.WorldPosition = transform.WorldPosition + aim * 0.6f;
        Vector3 velocity = aim * Speed;
        if (thrower != null)
        {
            velocity = velocity + thrower.Velocity;
        }
        ball.GetComponent<Rigidbody>().Velocity = velocity;

        EventBus.Publish(new PortalBallFired(Entity));
        balls.Enqueue(ball);
        while (balls.Count > MaxBalls)
        {
            Entity oldest = balls.Dequeue();
            if (oldest)
            {
                oldest.Destroy();
            }
        }
        return ball;
    }
}
