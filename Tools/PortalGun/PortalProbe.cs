using ScriptCore;

// Compiled only by Tools/TestPortalGun.py. Measures the real native mover + managed portal path.
[ExecutionOrder(200)]
public class PortalProbe : Script
{
    private int frame, stage, stageFrame, checks, failures, transfers, transferFrame, caseIndex;
    private Entity player, ball;
    private CharacterController mover;
    private FirstPersonController controller;
    private Transform eye;
    private Portal blue, orange;
    private bool armed, transferred, forbidTransfer, recovery;
    private float initialSpeed;
    private Vector3 postVelocity, postForward, lastUp, lastResidual;
    private string label = "setup";

    private readonly (string Name, Vector3 In, Vector3 InUp, Vector3 Out, Vector3 OutUp, float Speed, bool Pole)[] cases =
    {
        ("wall to perpendicular wall", new Vector3(0,0,-1), Vector3.Up, Vector3.Right, Vector3.Up, 24, false),
        ("floor to wall", Vector3.Up, Vector3.Forward, new Vector3(0,0,-1), Vector3.Up, 32, false),
        ("wall to floor", new Vector3(0,0,-1), Vector3.Up, Vector3.Up, Vector3.Forward, 40, false),
        ("ceiling to wall", -Vector3.Up, Vector3.Forward, -Vector3.Right, Vector3.Up, 32, false),
        ("wall to ceiling", Vector3.Right, Vector3.Up, -Vector3.Up, Vector3.Forward, 40, false),
        ("rolled doorway", new Vector3(0,0,-1), Vector3.Right, Vector3.Forward, -Vector3.Right, 24, false),
        ("oblique doorway", new Vector3(1,1,1).Normalized(), Vector3.Up, new Vector3(-0.4f,0.8f,0.3f).Normalized(), Vector3.Forward, 32, false),
        ("vertical gaze", new Vector3(0,0,-1), Vector3.Up, Vector3.Right, Vector3.Up, 24, true),
        ("120 metre per second fling", new Vector3(0,0,-1), Vector3.Up, Vector3.Up, Vector3.Forward, 120, false),
    };

    private void Check(bool result, string name)
    {
        ++checks;
        if (result) return;
        ++failures;
        Debug.Log("PORTAL FAIL: " + label + ": " + name);
    }

    private static Vector3 MapDirection(Transform from, Transform to, Vector3 value)
        => to.Right * -Vector3.Dot(value, from.Right) + to.Up * Vector3.Dot(value, from.Up)
            + to.Forward * -Vector3.Dot(value, from.Forward);
    private static Vector3 MapPoint(Transform from, Transform to, Vector3 value)
        => to.WorldPosition + MapDirection(from, to, value - from.WorldPosition);
    private bool Shoot(string name, Vector3 origin, Vector3 direction)
        => PortalPlacement.Shoot(name, origin, direction, out _);
    private void Advance(int next)
    {
        stage = next;
        stageFrame = frame;
    }
    private void ResetPortalHistory()
    {
        blue.Place(blue.transform.WorldPosition, blue.transform.Forward, blue.transform.Up, blue.SurfaceHost.Resolve());
        orange.Place(orange.transform.WorldPosition, orange.transform.Forward, orange.transform.Up, orange.SurfaceHost.Resolve());
    }
    private void PreparePlayer(Vector3 position, Vector3 gaze, Vector3 up, Vector3 velocity)
    {
        Vector3 heading = new Vector3(gaze.x,0,gaze.z);
        if (heading.LengthSquared() < 0.01f) heading = Vector3.Forward;
        mover.Teleport(position - Vector3.Up * 0.7f, heading.Normalized());
        controller.ApplyPortalView(position, gaze, up);
        mover.Velocity = velocity;
        initialSpeed = velocity.Length();
        ResetPortalHistory();
        armed = true;
        transferred = recovery = false;
    }

    public override void OnStart()
    {
        On<PortalTraversed>(e =>
        {
            if (e.Traveller != player) return;
            ++transfers;
            if (forbidTransfer) Check(false, "unexpected transfer outside aperture");
            if (!armed) return;
            armed = false;
            transferred = recovery = true;
            transferFrame = frame;
            Transform source = e.Entrance.Transform, destination = e.Exit.Transform;
            Check(Vector3.Dot(e.IncomingEye - source.WorldPosition, source.Forward) < 0.0001f,
                "camera reaches portal plane before transfer");
            Check(Vector3.Distance(eye.WorldPosition, MapPoint(source, destination, e.IncomingEye)) < 0.001f,
                "exact eye position across seam");
            Check(Vector3.Dot(eye.Forward, MapDirection(source,destination,e.IncomingForward)) > 0.99999f,
                "complete forward orientation preserved");
            Check(Vector3.Dot(eye.Up, MapDirection(source,destination,e.IncomingUp)) > 0.99999f,
                "complete up orientation preserved");
            // Before transfer each fixture uses its authored 70 cm vertical eye offset.
            Vector3 expectedBody = MapPoint(source, destination, e.IncomingEye - Vector3.Up * 0.7f);
            Check(Vector3.Distance(player.Transform.WorldPosition, expectedBody) < 0.002f,
                "body maps without exit clearance shove");
            postVelocity = MapDirection(source, destination, e.IncomingVelocity);
            Check(Vector3.Distance(mover.Velocity, postVelocity) < 0.001f, "velocity rotates without changing magnitude");
            Check(System.Math.Abs(e.IncomingVelocity.Length() - initialSpeed) < 0.02f,
                "wall contact did not brake incoming momentum");
            Check(!mover.IsGrounded, "teleport clears stale grounded state");
            postForward = eye.Forward;
            lastUp = eye.Up;
            lastResidual = eye.WorldPosition - player.Transform.WorldPosition - Vector3.Up * 0.7f;
        });
    }

    public override void OnUpdate(float dt)
    {
        ++frame;
        if (frame < 6) return;
        if (stage == 0)
        {
            player = World.Find("Player");
            mover = player.GetComponent<CharacterController>();
            eye = World.GetTransformByName("Player Camera");
            Check(FirstPersonController.TryGet(player,out controller), "player controller registered");
            Input.MouseCaptured = false;
            foreach (float pitch in new[] { -80f, -45f, 0f, 45f, 80f })
            foreach (float yaw in new[] { 0f, 45f, 90f, 135f, 180f, 225f, 270f, 315f })
            {
                Vector3 Direction(float y, float p) => new Vector3(
                    Mathf.Sin(y * Mathf.Deg2Rad) * Mathf.Cos(p * Mathf.Deg2Rad),
                    Mathf.Sin(p * Mathf.Deg2Rad),
                    Mathf.Cos(y * Mathf.Deg2Rad) * Mathf.Cos(p * Mathf.Deg2Rad));
                controller.ApplyPortalView(eye.WorldPosition, Direction(yaw, pitch), Vector3.Up);
                controller.ApplyLookInput(new Vector2(5, 2));
                controller.OnUpdate(0);
                Check(Vector3.Dot(eye.Forward, Direction(yaw + 5, pitch + 2)) > 0.99999f,
                    "diagonal mouse input retains yaw and pitch accuracy at every heading and elevation");
                controller.ApplyLookInput(new Vector2(-5, -2));
                controller.OnUpdate(0);
                Check(Vector3.Dot(eye.Forward, Direction(yaw, pitch)) > 0.99999f,
                    "opposite mouse delta returns to the same aim without drift");
            }
            controller.ApplyPortalView(eye.WorldPosition, Vector3.Forward, Vector3.Up);
            controller.ApplyLookInput(new Vector2(0, -120));
            controller.OnUpdate(0);
            Check(eye.Forward.y < -0.99f && eye.Up.y > 0f, "large downward mouse delta clamps before somersault");
            controller.ApplyLookInput(new Vector2(0, 260));
            controller.OnUpdate(0);
            Check(eye.Forward.y > 0.99f && eye.Up.y > 0f, "large upward mouse delta clamps before somersault");
            controller.ApplyLookInput(new Vector2(0, -20));
            controller.OnUpdate(0);
            Check(eye.Forward.y < 0.99f, "looking away from pitch limit responds immediately");
            blue = Portal.Instances["Blue Portal"];
            orange = Portal.Instances["Orange Portal"];
            player.SetField("CharacterController", "GravityScale", 0f);
            Input.MouseCaptured = false;
            Check(Shoot("Blue Portal",new Vector3(0,3,-8),Vector3.Forward), "blue wall placement");
            Check(Shoot("Orange Portal",new Vector3(8,3,-8),Vector3.Forward), "orange wall placement");
            foreach (string color in new[] { "Blue", "Orange" })
            {
                Transform surface = World.GetTransformByName(color + " Portal Surface");
                float near = eye.Entity.GetComponent<Camera>().Near;
                Check(surface.Scale.z * 2f > near,
                    "portal view volume extends beyond camera near plane at crossing");
                Check(System.Math.Abs(surface.Position.z + surface.Scale.z) < 0.001f,
                    "portal view volume front stays on transfer plane");
            }
            Vector3 old = orange.transform.WorldPosition;
            Check(!Shoot("Orange Portal",new Vector3(0,3,-8),Vector3.Forward), "overlap rejected");
            Check(Vector3.Distance(old,orange.transform.WorldPosition)<0.001f, "rejection keeps old entrance");
            Check(!Shoot("Blue Portal",new Vector3(0,10,-8),Vector3.Up), "sky rejected");
            Check(!Shoot("Blue Portal",new Vector3(-10,2,-8),Vector3.Forward), "small face rejected");
            label = "mounted wall traversal";
            PreparePlayer(blue.transform.WorldPosition + blue.transform.Up * 0.6f + blue.transform.Forward * 0.9f,
                -blue.transform.Forward, Vector3.Up, -blue.transform.Forward * 8);
            Advance(1);
        }
        else if (stage == 1)
        {
            if (transferred && frame >= transferFrame+5)
            {
                Check(player.Transform.WorldPosition.x > 7, "emerges at linked wall");
                Debug.Log("PORTAL PASS: " + label);
                armed = recovery = false;
                label = "mounted ball traversal";
                mover.Teleport(new Vector3(14,20,-8),Vector3.Forward);
                controller.ApplyPortalView(player.Transform.WorldPosition+Vector3.Up*0.7f,Vector3.Forward,Vector3.Up);
                ball = World.Instantiate("Assets/Prefabs/Portals/PortalBall.prefab");
                ball.SetField("Rigidbody","GravityScale",0f);
                ball.SetField("Rigidbody","LinearDamping",0f);
                ball.Transform.WorldPosition=blue.transform.WorldPosition+blue.transform.Forward*0.7f;
                ball.GetComponent<Rigidbody>().Velocity=-blue.transform.Forward*20;
                Advance(2);
            }
            else if (frame-stageFrame>50) { Check(false,"timed out reaching actual wall plane"); Advance(2); }
        }
        else if (stage == 2)
        {
            if (ball && ball.Transform.WorldPosition.x>7)
            {
                Check(ball.GetComponent<Rigidbody>().Velocity.z < -19.9f, "ball exits with full speed");
                Debug.Log("PORTAL PASS: " + label);
                ball.Destroy();
                label="solid wall outside doorway";
                forbidTransfer=true;
                mover.Teleport(new Vector3(14,3,28),Vector3.Forward);
                controller.ApplyPortalView(player.Transform.WorldPosition+Vector3.Up*0.7f,Vector3.Forward,Vector3.Up);
                mover.Velocity=Vector3.Forward*12;
                ResetPortalHistory();
                Advance(3);
            }
            else if(frame-stageFrame>45) { Check(false,"ball stopped at host wall"); Advance(3); }
        }
        else if(stage==3 && frame-stageFrame>=20)
        {
            Check(player.Transform.WorldPosition.z<29.3f,"rest of host wall remains solid");
            Check(player.Transform.WorldPosition.z>28.5f,"approach actually reaches solid host wall");
            Debug.Log("PORTAL PASS: " + label);
            forbidTransfer=false;
            label="mounted floor traversal";
            Check(Shoot("Blue Portal",new Vector3(-10,10,-10),-Vector3.Up),"floor placed");
            PreparePlayer(blue.transform.WorldPosition+Vector3.Up*1.6f,-Vector3.Up,Vector3.Forward,-Vector3.Up*12);
            Advance(4);
        }
        else if(stage==4)
        {
            if(transferred && frame>=transferFrame+5)
            {
                Check(player.Transform.WorldPosition.x>7,"floor entry emerges at linked wall");
                Debug.Log("PORTAL PASS: " + label);
                recovery=armed=false;
                Advance(5);
            }
            else if(frame-stageFrame>50) { Check(false,"floor host stopped capsule before eye plane"); Advance(5); }
        }
        else if(stage==5)
        {
            if(caseIndex>=cases.Length)
            {
                Debug.Log(failures==0 ? "PORTAL ALL PASSED: "+checks : "PORTAL FAILED: "+failures+" of "+checks);
                Advance(9);
                return;
            }
            var c=cases[caseIndex];
            label=c.Name;
            blue.Place(new Vector3(-8,40,0),c.In,c.InUp);
            orange.Place(new Vector3(8,40,0),c.Out,c.OutUp);
            Vector3 gaze=c.Pole ? Vector3.Up : (-blue.transform.Forward+blue.transform.Right*0.15f).Normalized();
            Vector3 up=c.Pole ? Vector3.Forward : Vector3.Up;
            PreparePlayer(blue.transform.WorldPosition+blue.transform.Forward*1.2f,gaze,up,
                -blue.transform.Forward*c.Speed+blue.transform.Right*2);
            Advance(6);
        }
        else if(stage==6)
        {
            if(transferred && frame>=transferFrame+9)
            {
                Debug.Log("PORTAL PASS: "+label);
                armed=recovery=false;
                ++caseIndex;
                Advance(5);
            }
            else if(frame-stageFrame>35)
            {
                Check(false,"timed out crossing free doorway");
                armed=recovery=false;
                ++caseIndex;
                Advance(5);
            }
        }
    }

    public override void OnLateUpdate(float dt)
    {
        if(stage==3)
            Check(player.Transform.WorldPosition.z<29.3f,"outside aperture stays blocked across physics steps");
        if(!recovery || frame==transferFrame) return;
        Check(Vector3.Dot(eye.Forward,postForward)>0.99998f,"upright recovery preserves aim");
        float angle=(float)System.Math.Acos(Mathf.Clamp(Vector3.Dot(eye.Up,lastUp),-1,1))*Mathf.Rad2Deg;
        Check(angle<=180f*dt+0.1f,"upright recovery has no orientation snap");
        Vector3 residual=eye.WorldPosition-player.Transform.WorldPosition-Vector3.Up*0.7f;
        Check((residual-lastResidual).Length()<12.6f*dt+0.001f,"eye offset recovers without a position snap");
        Check(Vector3.Distance(mover.Velocity,postVelocity)<0.02f,"idle air movement retains fling velocity");
        foreach(Portal portal in new[]{blue,orange})
        {
            Transform destination=World.GetTransformByName(portal.LinkedPortal);
            Transform view=World.GetTransformByName(portal.Entity.Name+" Camera");
            Check(Vector3.Distance(view.WorldPosition,MapPoint(portal.transform,destination,eye.WorldPosition))<0.001f,
                "portal render camera uses final transferred eye");
            Check(Vector3.Dot(view.Forward,MapDirection(portal.transform,destination,eye.Forward))>0.99999f,
                "portal render camera uses final transferred orientation");
        }
        lastUp=eye.Up;
        lastResidual=residual;
    }
}
