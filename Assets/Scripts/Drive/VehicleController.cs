using ScriptCore;

// Arcade car on a kinematic body: Move drives (W/S throttle and reverse, A/D steer), Jump is the
// handbrake. Four wheel raycasts follow the ground and tilt the body child; driving off a crest
// leaves the ground and gravity takes over until it lands. Falling off the world respawns it.
public class VehicleController : Script
{
    public string BodyName = "Vehicle Body";
    public float MaxSpeed = 28.0f;
    public float ReverseSpeed = 8.0f;
    public float Acceleration = 14.0f;
    public float BrakeDeceleration = 30.0f;
    public float Drag = 0.25f;
    public float RollingResistance = 2.0f;
    public float SteerDegreesPerSecond = 95.0f;
    public float Grip = 0.08f;
    public float HandbrakeGrip = 0.6f;
    public float Gravity = 22.0f;
    public float RideHeight = 0.0f;
    public float HalfTrack = 0.85f;
    public float HalfWheelbase = 1.35f;
    public float TiltHalfLife = 0.06f;
    public float MaxStep = 0.6f;
    public float MaxClimbSpeed = 12.0f;
    // Constant inputs added to Move, for automated captures.
    public float TestThrottle = 0.0f;
    public float TestSteer = 0.0f;

    private Entity body;
    private Vector3 position;
    private Vector3 velocity;
    private float yaw;
    private float speed;
    private float pitch;
    private float roll;
    private bool grounded;
    private Vector3 spawnPosition;
    private float spawnYaw;

    public override void OnStart()
    {
        body = World.Find(BodyName);
        position = transform.WorldPosition;
        yaw = transform.Rotation.y;
        spawnPosition = position;
        spawnYaw = yaw;
    }

    public override void OnReload()
    {
        body = World.Find(BodyName);
    }

    public override void OnUpdate(float deltaTime)
    {
        float dt = Mathf.Min(deltaTime, 0.05f);
        Vector2 move = Input.GetActionVector2("Move");
        move = new Vector2(Mathf.Clamp(move.x + TestSteer, -1f, 1f), Mathf.Clamp(move.y + TestThrottle, -1f, 1f));
        bool handbrake = Input.IsActionPressed("Jump");

        float yawRad = yaw * Mathf.Deg2Rad;
        Vector3 forward = new Vector3(Mathf.Sin(yawRad), 0f, Mathf.Cos(yawRad));
        Vector3 right = new Vector3(forward.z, 0f, -forward.x);

        // Wheel contact heights; a missing wheel counts as the root's own ground.
        float fl, fr, rl, rr;
        bool anyHit = false;
        fl = SampleGround(position + forward * HalfWheelbase - right * HalfTrack, ref anyHit);
        fr = SampleGround(position + forward * HalfWheelbase + right * HalfTrack, ref anyHit);
        rl = SampleGround(position - forward * HalfWheelbase - right * HalfTrack, ref anyHit);
        rr = SampleGround(position - forward * HalfWheelbase + right * HalfTrack, ref anyHit);
        if (!anyHit)
        {
            Respawn();
            return;
        }
        float groundY = (fl + fr + rl + rr) * 0.25f + RideHeight;
        float slope = ((fl + fr) - (rl + rr)) * 0.5f / (2f * HalfWheelbase);

        if (grounded)
        {
            // Throttle, brake and reverse along the car's heading.
            if (move.y > 0.05f)
            {
                speed += (speed < 0f ? BrakeDeceleration : Acceleration) * move.y * dt;
            }
            else if (move.y < -0.05f)
            {
                speed += (speed > 0f ? BrakeDeceleration : Acceleration * 0.6f) * move.y * dt;
            }
            else
            {
                speed = MoveTowards(speed, 0f, RollingResistance * dt);
            }
            if (handbrake)
            {
                speed = MoveTowards(speed, 0f, BrakeDeceleration * 0.5f * dt);
            }
            speed -= Gravity * slope * 0.5f * dt;
            speed -= speed * Mathf.Abs(speed) * Drag * 0.01f * dt;
            speed = Mathf.Clamp(speed, -ReverseSpeed, MaxSpeed);

            // Steering scales in with speed and flips in reverse.
            float steerScale = Mathf.Clamp(speed / 6f, -1f, 1f);
            yaw += move.x * SteerDegreesPerSecond * steerScale * dt;

            // The tyres pull the velocity toward the heading; the handbrake lets it slide.
            Vector3 target = forward * speed;
            Vector3 horizontal = new Vector3(velocity.x, 0f, velocity.z);
            horizontal = Mathf.Damp(horizontal, target, handbrake ? HandbrakeGrip : Grip, dt);
            velocity = new Vector3(horizontal.x, velocity.y, horizontal.z);
        }

        // Vertical: follow the ground while on it, fall when it drops away faster than gravity.
        float previousY = position.y;
        velocity.y -= Gravity * dt;
        position += velocity * dt;
        if (position.y <= groundY)
        {
            if (!grounded)
            {
                speed = Vector3.Dot(new Vector3(velocity.x, 0f, velocity.z), forward);
            }
            position.y = groundY;
            velocity.y = Mathf.Clamp((groundY - previousY) / dt, 0f, MaxClimbSpeed);
            grounded = true;
        }
        else
        {
            grounded = position.y - groundY < 0.05f;
        }

        transform.WorldPosition = position;
        transform.Rotation = new Vector3(0f, yaw, 0f);

        // Tilt the body to the wheel contacts on the ground; level out slowly in the air.
        if (body)
        {
            float targetPitch = grounded ? -Mathf.Atan2(((fl + fr) - (rl + rr)) * 0.5f, 2f * HalfWheelbase) * Mathf.Rad2Deg : pitch;
            float targetRoll = grounded ? Mathf.Atan2(((fr + rr) - (fl + rl)) * 0.5f, 2f * HalfTrack) * Mathf.Rad2Deg : roll * 0.98f;
            pitch = Mathf.Damp(pitch, targetPitch, TiltHalfLife, dt);
            roll = Mathf.Damp(roll, targetRoll, TiltHalfLife, dt);
            body.Transform.Rotation = new Vector3(pitch, 0f, roll);
        }
    }

    // Height of the ground under a point, skipping the car's own collider and anything taller than
    // a step (crates get pushed by the body rather than driven over).
    private float SampleGround(Vector3 point, ref bool anyHit)
    {
        Vector3 origin = new Vector3(point.x, position.y + 4f, point.z);
        for (int attempt = 0; attempt < 3; ++attempt)
        {
            if (!Physics.Raycast(origin, -Vector3.Up, 60f, out var hit))
            {
                break;
            }
            if (hit.Entity != Entity && hit.Point.y <= position.y + MaxStep)
            {
                anyHit = true;
                return hit.Point.y;
            }
            origin = new Vector3(point.x, hit.Point.y - 0.05f, point.z);
        }
        return position.y - 60f;
    }

    private void Respawn()
    {
        position = spawnPosition;
        yaw = spawnYaw;
        velocity = Vector3.Zero;
        speed = 0f;
        grounded = false;
    }

    private static float MoveTowards(float current, float target, float maxDelta)
    {
        if (Mathf.Abs(target - current) <= maxDelta)
        {
            return target;
        }
        return current + (target > current ? maxDelta : -maxDelta);
    }
}
