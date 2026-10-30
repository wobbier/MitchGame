using ScriptCore;

// Focused gameplay regression: use the actual carry/drop path, then let native physics settle.
[ExecutionOrder(250)]
public class PressurePlateProbe : Script
{
    private ChamberController chamber;
    private FirstPersonController controller;
    private CharacterController mover;
    private Entity player, cube;
    private Transform eye, gate;
    private int frame, stage, started, index, checks, failures;
    private bool reported;
    private readonly (string Name, float X, float Z, float Pitch, float Yaw, bool Pressed)[] cases =
    {
        ("center carry/drop before relay power", 0, 0, 0, 0, true),
        ("supported right edge", 1.0f, 0, 0, 0, true),
        ("supported front edge with yaw", 0, -1.0f, 0, 40, true),
        ("supported corner with yaw", 0.98f, 0.98f, 0, 30, true),
        ("tilted normal drop", 0, 0, 25, 35, true),
        ("outside plate", 1.65f, 0, 0, 0, false),
    };
    private string Label => index < cases.Length ? cases[index].Name : "hover";
    private void Check(bool value, string description)
    {
        ++checks;
        if (value) return;
        ++failures;
        Debug.Log("PLATE FAIL: " + Label + ": " + description);
    }
    private void Begin(int next) { stage = next; started = frame; }
    private bool Elapsed(int frames) => frame - started >= frames;
    private void Pose(Vector3 body, Vector3 forward, Vector3 up)
    {
        Vector3 heading = new Vector3(forward.x, 0, forward.z).Normalized();
        mover.Teleport(body, heading.LengthSquared() > 0.01f ? heading : Vector3.Forward);
        controller.ApplyPortalView(body + Vector3.Up * 0.7f, forward, up);
        mover.Velocity = Vector3.Zero;
        Portal.ResetTravellerHistory(player);
    }
    private void MoveCube(Vector3 point, bool dynamic = true)
    {
        if (ChamberController.IsHolding(cube)) chamber.DropCube();
        cube.SetField("Rigidbody", "BodyType", dynamic ? "Dynamic" : "Kinematic");
        cube.GetComponent<Rigidbody>().Teleport(point, Vector3.Forward, Vector3.Up);
        cube.GetComponent<Rigidbody>().Velocity = Vector3.Zero;
    }
    public override void OnUpdate(float dt)
    {
        ++frame;
        if (frame < 8) return;
        if (stage == 0)
        {
            chamber = ChamberController.Active;
            player = World.Find("Player");
            cube = World.Find("Companion Cube");
            eye = World.GetTransformByName("Player Camera");
            gate = World.GetTransformByName("Gate Left");
            mover = player.GetComponent<CharacterController>();
            Check(FirstPersonController.TryGet(player, out controller), "controller exists");
            player.SetField("CharacterController", "GravityScale", 0f);
            Input.MouseCaptured = false;
            Check(!chamber.Powered, "fixture starts without relay power");
            Begin(1);
        }
        if (stage == 1)
        {
            if (index >= cases.Length)
            {
                Pose(new Vector3(0, 0.9f, 9), Vector3.Forward, Vector3.Up);
                MoveCube(new Vector3(0, 2.1f, 13), false);
                Begin(5);
                return;
            }
            var c = cases[index];
            Quaternion rotation = Quaternion.Euler(c.Pitch, c.Yaw, 0);
            Vector3 forward = rotation * Vector3.Forward;
            Vector3 up = rotation * Vector3.Up;
            Vector3 carry = (forward * 1.55f - up * 0.24f).Normalized() * 1.55f;
            Vector3 body = new Vector3(c.X - carry.x, 0.9f, 13 + c.Z - carry.z);
            Pose(body, forward, up);
            MoveCube(eye.WorldPosition + forward * 1.4f);
            Check(chamber.TryGrabCube(), "cube can be grabbed through normal gameplay API");
            Begin(2);
        }
        else if (stage == 2 && Elapsed(7))
        {
            Check(ChamberController.IsHolding(cube), "cube stays held above plate");
            Check(!chamber.PlateWeighted, "held cube does not weigh the plate");
            chamber.DropCube();
            Pose(new Vector3(0, 0.9f, 8), Vector3.Forward, Vector3.Up);
            Begin(3);
        }
        else if (stage == 3 && Elapsed(90))
        {
            var c = cases[index];
            Vector3 p = cube.Transform.WorldPosition;
            Debug.Log("PLATE DROP: " + c.Name + " cube " + p + " pressed " + chamber.PlateWeighted
                + " powered " + chamber.Powered + " gateX " + gate.WorldPosition.x);
            Check(chamber.PlateWeighted == c.Pressed, "settled physical cube has expected plate response");
            Check(c.Pressed ? gate.WorldPosition.x < -2.7f : gate.WorldPosition.x > -1.1f,
                "local switch drives its gate without relay prerequisite");
            Check(World.GetTransformByName("Exit Door").WorldPosition.y < 7.1f,
                "final exit still requires relay power");
            if (index == 0)
            {
                Pose(new Vector3(0, 0.9f, 26), Vector3.Forward, Vector3.Up);
                Check(!chamber.TryOpenHatch() && !chamber.HatchOpened,
                    "weighted switch alone cannot release unpowered final hatch");
            }
            Pose(new Vector3(p.x, 0.9f, p.z - 1.6f), (p - new Vector3(p.x, 1.6f, p.z - 1.6f)).Normalized(), Vector3.Up);
            Check(chamber.TryGrabCube(), "settled cube can be picked back up");
            Begin(4);
        }
        else if (stage == 4 && Elapsed(65))
        {
            Check(!chamber.PlateWeighted, "lifting cube releases the pressure plate");
            Check(gate.WorldPosition.x > -1.1f, "gate closes when cube is lifted");
            chamber.DropCube();
            MoveCube(new Vector3(4, 1.0f, 13));
            ++index;
            Begin(1);
        }
        else if (stage == 5 && Elapsed(20))
        {
            Check(!chamber.PlateWeighted, "hovering cube above plate does not press it");
            Check(gate.WorldPosition.x > -1.1f, "hovering cube does not open gate");
            MoveCube(new Vector3(1.0f, 0.85f, 13));
            Pose(new Vector3(4, 2.3f, 8), new Vector3(-4, -2.7f, 5).Normalized(), Vector3.Up);
            Begin(6);
        }
        else if (stage == 6 && Elapsed(60) && !reported)
        {
            reported = true;
            Debug.Log(failures == 0 ? "PLATE ALL PASSED: " + checks : "PLATE FAILED: " + failures + " of " + checks);
            Begin(9);
        }
    }
}
