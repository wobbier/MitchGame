using ScriptCore;

// Arcade car on a kinematic body: Move drives (W/S throttle and reverse, A/D steer), Jump is the
// handbrake. Each wheel raycasts the ground and pushes on the chassis through a spring-damper, so
// the chassis heaves, pitches and rolls on its suspension; a wheel that drops off an edge just
// stops pushing while the others keep driving. Grip, throttle and steering scale with the weight
// the wheels carry, so a crest lightens the car instead of cutting it out. Driving off a ramp
// leaves the ground and gravity takes over until it lands. Falling off the world respawns it.
// The wheels spin, steer and ride the suspension, the steering wheel turns, and the body leans
// under acceleration; CockpitCamera reads Active for the driver's head motion.
// Walls (anything solid and steep that isn't a loose physics object) stop the car; hitting one
// faster than CrashSpeed wrecks it: the car freezes where it hit and CarCrash takes over.
public class VehicleController : Script
{
    public string BodyName = "Vehicle Body";
    public float MaxSpeed = 28.0f;
    public float ReverseSpeed = 8.0f;
    public float Acceleration = 14.0f;
    public float BrakeDeceleration = 30.0f;
    public float Drag = 0.25f;
    public float RollingResistance = 2.0f;
    public float SteerDegreesPerSecond = 110.0f;
    // Steering eases in/out over this half-life and tightens to HighSpeedSteer at MaxSpeed.
    public float SteerHalfLife = 0.06f;
    public float HighSpeedSteer = 0.55f;
    public float Grip = 0.06f;
    public float HandbrakeGrip = 0.6f;
    public float Gravity = 22.0f;
    public float RideHeight = 0.0f;
    public float HalfTrack = 0.85f;
    public float HalfWheelbase = 1.35f;
    // Suspension: bounce frequency (Hz), damping ratio and how far a wheel compresses before the
    // bump stop. A wheel droops Gravity / (2π·Frequency)² below rest before it leaves the ground.
    public float SuspensionFrequency = 1.6f;
    public float SuspensionDamping = 0.6f;
    public float SuspensionTravel = 0.25f;
    // How fast (1/s) the chassis levels out in the air.
    public float AirLevelling = 1.5f;
    public float MaxStep = 0.6f;
    // Cosmetics: the model's wheel pivots, steering wheel and how far the body leans per m/s².
    public string WheelPivotFormat = "SM_Veh_4x4_Car_Wheel_{0}_01_$AssimpFbx$_RotationPivot";
    public string SteeringWheelName = "SM_Veh_4x4_Car_SteeringW_01_$AssimpFbx$_Rotation";
    public float WheelRadius = 0.46f;
    // Spinning faster than this per frame strobes (the wheels seem to stop or turn backwards).
    public float MaxWheelSpinPerFrame = 25.0f;
    public float MaxWheelSteer = 28.0f;
    public float SteeringWheelLock = 240.0f;
    public float SteeringColumnTilt = -22.3f;
    public float BodyRollPerAccel = 0.3f;
    public float BodyPitchPerAccel = 0.2f;
    public float AccelHalfLife = 0.08f;
    // Closing speed (m/s) that wrecks the car, and how far the bumpers reach from its centre.
    public float CrashSpeed = 12.0f;
    public float BumperLength = 2.2f;
    // Constant inputs added to Move, for automated captures.
    public float TestThrottle = 0.0f;
    public float TestSteer = 0.0f;

    // Wheel corners fl, fr, rl, rr in units of HalfTrack (x, right) and HalfWheelbase (z, forward).
    private static readonly float[] CornerX = { -1f, 1f, -1f, 1f };
    private static readonly float[] CornerZ = { 1f, 1f, -1f, -1f };

    private Entity body;
    private Vector3 position;
    private Vector3 velocity;
    private float yaw;
    private float speed;
    // The chassis plane: rise per metre forward and per metre right, and their rates.
    private float pitchSlope;
    private float rollSlope;
    private float pitchRate;
    private float rollRate;
    private float traction;
    private float steer;
    private float wheelSpin;
    private Entity[] wheels = new Entity[4];
    private Vector3[] wheelRest = new Vector3[4];
    private float[] wheelDrop = new float[4];
    private bool[] hasGround = new bool[4];
    private bool[] contact = new bool[4];
    private float[] groundHeight = new float[4];
    private float[] groundSlopeX = new float[4];
    private float[] groundSlopeZ = new float[4];
    private float[] compression = new float[4];
    private Entity steeringWheel;
    private Vector3 previousVelocity;

    public static VehicleController Active;
    public float Speed => speed;
    public float Steer => steer;
    public bool Grounded => grounded;
    // Smoothed acceleration in the car's frame: x is right, z is forward (m/s²).
    public Vector3 LocalAcceleration { get; private set; }
    // Bumped on every touchdown; LandingSpeed is how fast it was falling.
    public int Landings { get; private set; }
    public float LandingSpeed { get; private set; }
    public Vector3 Velocity => velocity;
    // Bumped on every wreck; the car stays put until ResetTo / Respawn.
    public int Crashes { get; private set; }
    public bool Crashed { get; private set; }
    public Vector3 ImpactVelocity { get; private set; }
    public Vector3 ImpactPoint { get; private set; }
    public Vector3 ImpactNormal { get; private set; }
    private bool grounded;
    private Vector3 spawnPosition;
    private float spawnYaw;

    public override void OnStart()
    {
        FindParts();
        position = transform.WorldPosition;
        yaw = transform.Rotation.y;
        spawnPosition = position;
        spawnYaw = yaw;
    }

    public override void OnReload()
    {
        // Only public fields survive a hot reload: pick the pose back up from the transform.
        FindParts();
        Vector3 heading = transform.Forward;
        position = transform.WorldPosition;
        yaw = Mathf.Atan2(heading.x, heading.z) * Mathf.Rad2Deg;
    }

    public override void OnDestroy()
    {
        if (Active == this)
        {
            Active = null;
        }
    }

    private void FindParts()
    {
        Active = this;
        body = World.Find(BodyName);
        string[] corners = { "fl", "fr", "rl", "rr" };
        for (int i = 0; i < 4; ++i)
        {
            wheels[i] = World.Find(string.Format(WheelPivotFormat, corners[i]));
            // The pivot's inverse child undoes its offset, so it holds the rest position even after
            // a hot reload has found the pivot mid-bounce.
            Entity inverse = World.Find(string.Format(WheelPivotFormat + "Inverse", corners[i]));
            if (inverse)
            {
                wheelRest[i] = -inverse.Transform.Position;
            }
            else if (wheels[i])
            {
                wheelRest[i] = wheels[i].Transform.Position;
            }
        }
        steeringWheel = World.Find(SteeringWheelName);
    }

    public override void OnUpdate(float deltaTime)
    {
        float dt = Mathf.Min(deltaTime, 0.05f);
        if (dt <= 0f || Crashed)
        {
            return;
        }
        Vector2 move = Input.GetActionVector2("Move");
        move = new Vector2(Mathf.Clamp(move.x + TestSteer, -1f, 1f), Mathf.Clamp(move.y + TestThrottle, -1f, 1f));
        bool handbrake = Input.IsActionPressed("Jump");

        float yawRad = yaw * Mathf.Deg2Rad;
        Vector3 forward = new Vector3(Mathf.Sin(yawRad), 0f, Mathf.Cos(yawRad));
        Vector3 right = new Vector3(forward.z, 0f, -forward.x);

        // The ground under each wheel, looked for from that corner of the chassis.
        bool anyGround = false;
        for (int i = 0; i < 4; ++i)
        {
            float x = CornerX[i] * HalfTrack, z = CornerZ[i] * HalfWheelbase;
            Vector3 point = position + forward * z + right * x;
            hasGround[i] = SampleGround(point, position.y + pitchSlope * z + rollSlope * x, i);
            anyGround |= hasGround[i];
        }
        if (!anyGround)
        {
            Respawn();
            return;
        }

        steer = Mathf.Damp(steer, move.x, SteerHalfLife, dt);
        // Throttle, brake and reverse along the car's heading, as far as the tyres are loaded; a
        // light car keeps the speed it is actually moving at.
        float forwardSpeed = Vector3.Dot(new Vector3(velocity.x, 0f, velocity.z), forward);
        speed = Mathf.Lerp(forwardSpeed, speed, traction);
        if (move.y > 0.05f)
        {
            speed += (speed < 0f ? BrakeDeceleration : Acceleration) * move.y * traction * dt;
        }
        else if (move.y < -0.05f)
        {
            speed += (speed > 0f ? BrakeDeceleration : Acceleration * 0.6f) * move.y * traction * dt;
        }
        else
        {
            speed = MoveTowards(speed, 0f, RollingResistance * traction * dt);
        }
        if (handbrake)
        {
            speed = MoveTowards(speed, 0f, BrakeDeceleration * 0.5f * traction * dt);
        }
        // Hills pull at the full g·sinθ, so the rim's mountains can't be taken flat out.
        speed -= Gravity * pitchSlope / Mathf.Sqrt(1f + pitchSlope * pitchSlope) * traction * dt;
        speed -= speed * Mathf.Abs(speed) * Drag * 0.01f * dt;
        speed = Mathf.Clamp(speed, -ReverseSpeed, MaxSpeed);

        // Steering scales in with speed and flips in reverse.
        float steerScale = Mathf.Clamp(speed / 4f, -1f, 1f);
        float speedFactor = 1f - (1f - HighSpeedSteer) * Mathf.Clamp(Mathf.Abs(speed) / MaxSpeed, 0f, 1f);
        yaw += steer * SteerDegreesPerSecond * steerScale * speedFactor * traction * dt;

        // The tyres pull the velocity toward the heading; the handbrake lets it slide.
        if (traction > 0.01f)
        {
            Vector3 target = forward * speed;
            Vector3 horizontal = new Vector3(velocity.x, 0f, velocity.z);
            horizontal = Mathf.Damp(horizontal, target, (handbrake ? HandbrakeGrip : Grip) / traction, dt);
            velocity = new Vector3(horizontal.x, velocity.y, horizontal.z);
        }

        if (HitWall(forward, right, dt))
        {
            return;
        }

        float fallSpeed = -velocity.y;
        bool wasGrounded = grounded;
        Suspension(dt);
        grounded = contact[0] || contact[1] || contact[2] || contact[3];
        if (grounded && !wasGrounded)
        {
            LandingSpeed = Mathf.Max(fallSpeed, 0f);
            ++Landings;
        }

        transform.WorldPosition = position;
        transform.Rotation = new Vector3(0f, yaw, 0f);

        // Acceleration felt in the seat, from the change in horizontal velocity (cornering included).
        Vector3 accel = Vector3.Zero;
        if (grounded)
        {
            Vector3 delta = new Vector3(velocity.x - previousVelocity.x, 0f, velocity.z - previousVelocity.z) / dt;
            accel = new Vector3(Vector3.Dot(delta, right), 0f, Vector3.Dot(delta, forward));
        }
        previousVelocity = velocity;
        LocalAcceleration = Mathf.Damp(LocalAcceleration, accel, AccelHalfLife, dt);

        // Tilt the body with the chassis, rolling out of turns and squatting under throttle.
        if (body)
        {
            float lean = Mathf.Clamp(LocalAcceleration.x * BodyRollPerAccel, -6f, 6f);
            float squat = Mathf.Clamp(LocalAcceleration.z * BodyPitchPerAccel, -4f, 4f);
            float pitch = -Mathf.Atan2(pitchSlope, 1f) * Mathf.Rad2Deg - squat;
            float roll = Mathf.Atan2(rollSlope, 1f) * Mathf.Rad2Deg + lean;
            body.Transform.Rotation = new Vector3(pitch, 0f, roll);
        }
        AnimateParts(dt);
    }

    // Moves the car through the frame in small steps: each loaded wheel pushes its corner up with
    // a spring-damper (measured against the ground's own rise under the moving wheel), and corners
    // pressed past the travel hit the bump stop. The chassis is four equal masses at the wheels,
    // so heave, pitch and roll all bounce at SuspensionFrequency.
    private void Suspension(float dt)
    {
        int steps = (int)System.Math.Ceiling(dt * 120f);
        float h = dt / steps;
        float omega = SuspensionOmega;
        float stiffness = omega * omega * 0.25f;
        float damping = 2f * SuspensionDamping * omega * 0.25f;
        float droop = Droop;
        float pitchInertia = HalfWheelbase * HalfWheelbase;
        float rollInertia = HalfTrack * HalfTrack;
        Vector3 start = position;
        float load = 0f;
        for (int step = 0; step < steps; ++step)
        {
            position = new Vector3(position.x + velocity.x * h, position.y, position.z + velocity.z * h);
            float lift = 0f, pitchTorque = 0f, rollTorque = 0f;
            bool touching = false;
            for (int i = 0; i < 4; ++i)
            {
                contact[i] = false;
                if (!hasGround[i])
                {
                    continue;
                }
                float x = CornerX[i] * HalfTrack, z = CornerZ[i] * HalfWheelbase;
                float c = Compression(i, start, x, z);
                compression[i] = c;
                if (c <= -droop)
                {
                    continue;
                }
                float force = Mathf.Max(stiffness * (c + droop) - damping * CornerApproach(i, x, z), 0f);
                contact[i] = touching = true;
                lift += force;
                pitchTorque += force * z;
                rollTorque += force * x;
            }
            velocity.y += (lift - Gravity) * h;
            pitchRate += pitchTorque / pitchInertia * h;
            rollRate += rollTorque / rollInertia * h;
            if (!touching)
            {
                pitchRate = Mathf.Damp(pitchRate, -pitchSlope * AirLevelling, 0.2f, h);
                rollRate = Mathf.Damp(rollRate, -rollSlope * AirLevelling, 0.2f, h);
            }
            position.y += velocity.y * h;
            pitchSlope += pitchRate * h;
            rollSlope += rollRate * h;
            load += lift * h;

            // Bump stops: lift each corner out of the ground and stop it sinking further. A push at
            // one corner moves that corner three times as far as the centre.
            for (int pass = 0; pass < 4; ++pass)
            {
                for (int i = 0; i < 4; ++i)
                {
                    if (!hasGround[i])
                    {
                        continue;
                    }
                    float x = CornerX[i] * HalfTrack, z = CornerZ[i] * HalfWheelbase;
                    float excess = Compression(i, start, x, z) - SuspensionTravel;
                    if (excess <= 0f)
                    {
                        continue;
                    }
                    float push = excess / 3f;
                    position.y += push;
                    pitchSlope += push * z / pitchInertia;
                    rollSlope += push * x / rollInertia;
                    float approach = CornerApproach(i, x, z);
                    if (approach < 0f)
                    {
                        float impulse = -approach / 3f;
                        velocity.y += impulse;
                        pitchRate += impulse * z / pitchInertia;
                        rollRate += impulse * x / rollInertia;
                    }
                    contact[i] = true;
                }
            }
            if (Mathf.Abs(pitchSlope) > 0.8f)
            {
                pitchSlope = Mathf.Clamp(pitchSlope, -0.8f, 0.8f);
                pitchRate = 0f;
            }
            if (Mathf.Abs(rollSlope) > 0.8f)
            {
                rollSlope = Mathf.Clamp(rollSlope, -0.8f, 0.8f);
                rollRate = 0f;
            }
        }
        // Full grip while the wheels carry at least half the car's weight.
        traction = Mathf.Clamp01(load / dt / (Gravity * 0.5f));
    }

    private float SuspensionOmega => 2f * (float)System.Math.PI * SuspensionFrequency;
    private float Droop => Gravity / (SuspensionOmega * SuspensionOmega);

    // How far the ground sits above corner i of the chassis, following the ground's slope from
    // where it was sampled (start) to where the car is now.
    private float Compression(int i, Vector3 start, float x, float z)
    {
        float ground = groundHeight[i] + groundSlopeX[i] * (position.x - start.x) + groundSlopeZ[i] * (position.z - start.z) + RideHeight;
        return ground - (position.y + pitchSlope * z + rollSlope * x);
    }

    // How fast corner i moves up relative to the ground under its wheel.
    private float CornerApproach(int i, float x, float z)
    {
        float groundRise = groundSlopeX[i] * velocity.x + groundSlopeZ[i] * velocity.z;
        return velocity.y + pitchRate * z + rollRate * x - groundRise;
    }

    // The model faces -Z, so rolling forward is a negative turn about its X axis. The steering
    // wheel spins about its own column (clockwise from the seat for a right turn), which tilts by
    // SteeringColumnTilt; the composed rotation
    // is handed back as the engine's Z-Y-X Euler angles.
    private void AnimateParts(float dt)
    {
        float droop = Droop;
        float spin = Mathf.Clamp(-speed / WheelRadius * Mathf.Rad2Deg * dt, -MaxWheelSpinPerFrame, MaxWheelSpinPerFrame);
        wheelSpin = (wheelSpin + spin) % 360f;
        for (int i = 0; i < 4; ++i)
        {
            if (wheels[i])
            {
                // Wheels follow the ground within the suspension's reach and hang at full droop in the air.
                float drop = contact[i] ? Mathf.Clamp(compression[i], -droop, SuspensionTravel) : -droop;
                wheelDrop[i] = Mathf.Damp(wheelDrop[i], drop, 0.02f, dt);
                wheels[i].Transform.Position = wheelRest[i] + Vector3.Up * wheelDrop[i];
                wheels[i].Transform.Rotation = new Vector3(wheelSpin, i < 2 ? steer * MaxWheelSteer : 0f, 0f);
            }
        }
        if (steeringWheel)
        {
            float a = SteeringColumnTilt * Mathf.Deg2Rad;
            float s = -steer * SteeringWheelLock * Mathf.Deg2Rad;
            float sa = Mathf.Sin(a), ca = Mathf.Cos(a), ss = Mathf.Sin(s), cs = Mathf.Cos(s);
            steeringWheel.Transform.Rotation = new Vector3(Mathf.Atan2(sa * cs, ca), -(float)System.Math.Asin(sa * ss), Mathf.Atan2(ca * ss, cs)) * Mathf.Rad2Deg;
        }
    }

    // Records the ground under a wheel (height and slope), skipping the car's own collider, loose
    // physics objects (the body pushes those around rather than riding on them) and anything more
    // than a step above that corner of the chassis.
    private bool SampleGround(Vector3 point, float cornerY, int i)
    {
        Vector3 origin = new Vector3(point.x, cornerY + 4f, point.z);
        for (int attempt = 0; attempt < 4; ++attempt)
        {
            if (!Physics.Raycast(origin, -Vector3.Up, 80f, out var hit))
            {
                break;
            }
            if (hit.Entity != Entity && hit.Point.y <= cornerY + MaxStep && !hit.Entity.HasComponent<Rigidbody>())
            {
                float up = Mathf.Max(hit.Normal.y, 0.45f);
                groundHeight[i] = hit.Point.y;
                groundSlopeX[i] = Mathf.Clamp(-hit.Normal.x / up, -2f, 2f);
                groundSlopeZ[i] = Mathf.Clamp(-hit.Normal.z / up, -2f, 2f);
                return true;
            }
            origin = new Vector3(point.x, hit.Point.y - 0.05f, point.z);
        }
        return false;
    }

    // Looks for walls just past the bumper on the side the car is moving to, at headlight and
    // window height (lower things are steps the wheels ride over). A hit closing faster than
    // CrashSpeed wrecks the car; a slower one cancels the velocity into the wall so it scrapes along.
    private bool HitWall(Vector3 forward, Vector3 right, float dt)
    {
        float along = Vector3.Dot(new Vector3(velocity.x, 0f, velocity.z), forward);
        if (Mathf.Abs(along) < 0.5f)
        {
            return false;
        }
        float side = along > 0f ? 1f : -1f;
        float z = side * (BumperLength + 0.02f);
        float reach = Mathf.Abs(along) * dt + 0.15f;
        for (int i = 0; i < 6; ++i)
        {
            float x = (i % 3 - 1) * HalfTrack;
            float height = i < 3 ? 0.75f : 1.3f;
            Vector3 origin = position + forward * z + right * x + Vector3.Up * (height + pitchSlope * z + rollSlope * x);
            if (!Physics.Raycast(origin, forward * side, reach, out var hit) || hit.Entity == Entity || hit.Normal.y > 0.5f || hit.Entity.HasComponent<Rigidbody>())
            {
                continue;
            }
            Vector3 normal = new Vector3(hit.Normal.x, 0f, hit.Normal.z).Normalized();
            float closing = -Vector3.Dot(velocity, normal);
            if (closing <= 0f)
            {
                continue;
            }
            if (closing >= CrashSpeed)
            {
                Wreck(velocity, hit.Point, normal);
                return true;
            }
            velocity += normal * closing;
            speed = Vector3.Dot(new Vector3(velocity.x, 0f, velocity.z), forward);
        }
        return false;
    }

    // Stops the car dead where it hit; ImpactVelocity is how fast it was going.
    public void Wreck(Vector3 impactVelocity, Vector3 point, Vector3 normal)
    {
        ImpactVelocity = impactVelocity;
        ImpactPoint = point;
        ImpactNormal = normal;
        Crashed = true;
        ++Crashes;
        velocity = previousVelocity = LocalAcceleration = Vector3.Zero;
        speed = 0f;
        pitchRate = rollRate = 0f;
    }

    // Kicks the car (a jump, a launch) by adding to its velocity; off the ground it flies on that
    // until it lands.
    public void Launch(Vector3 kick)
    {
        if (Crashed)
        {
            return;
        }
        velocity += kick;
        float yawRad = yaw * Mathf.Deg2Rad;
        speed = Vector3.Dot(new Vector3(velocity.x, 0f, velocity.z), new Vector3(Mathf.Sin(yawRad), 0f, Mathf.Cos(yawRad)));
    }

    public void Respawn()
    {
        ResetTo(spawnPosition, spawnYaw);
    }

    // Puts the car back on the road at rest, facing yaw (degrees).
    public void ResetTo(Vector3 newPosition, float newYaw)
    {
        Crashed = false;
        position = newPosition;
        yaw = newYaw;
        transform.WorldPosition = position;
        transform.Rotation = new Vector3(0f, yaw, 0f);
        velocity = Vector3.Zero;
        previousVelocity = Vector3.Zero;
        speed = 0f;
        pitchSlope = rollSlope = pitchRate = rollRate = 0f;
        traction = 0f;
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
