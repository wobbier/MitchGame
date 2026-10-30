using ScriptCore;

// Compiled only by Tools/TestPortalChamber.py. Exercises the real chamber and native physics.
[ExecutionOrder(250)]
public class ChamberProbe : Script
{
    private ChamberController chamber;
    private FirstPersonController controller;
    private CharacterController playerMover;
    private Entity player, cube, ball;
    private Transform eye, bridge, leftGate, rightGate;
    private int frame, stage, began, checks, failures, portalTransfers;
    private bool finishReported;
    private Vector3 gateClosedLeft, gateClosedRight, resetTarget;
    private string label = "setup";

    private void Check(bool value, string description)
    {
        ++checks;
        if (value) return;
        ++failures;
        Debug.Log("CHAMBER FAIL: " + label + ": " + description);
    }

    private void Begin(int next, string description)
    {
        stage = next;
        began = frame;
        label = description;
    }

    private void Pass() => Debug.Log("CHAMBER PASS: " + label);
    private bool Elapsed(int frames) => frame - began >= frames;
    private bool Shoot(string name, Vector3 origin, Vector3 target)
        => PortalPlacement.Shoot(name, origin, (target - origin).Normalized(), out _);

    private void PutPlayer(Vector3 position, Vector3 forward)
    {
        Vector3 horizontal = new Vector3(forward.x, 0, forward.z);
        if (horizontal.LengthSquared() < 0.01f) horizontal = Vector3.Forward;
        playerMover.Teleport(position, horizontal.Normalized());
        controller.ApplyPortalView(position + Vector3.Up * 0.7f, forward, Vector3.Up);
        playerMover.Velocity = Vector3.Zero;
    }

    private Entity SpawnBall(Vector3 position, Vector3 velocity, float gravity = 1)
    {
        Entity spawned = World.Instantiate("Assets/Prefabs/Portals/PortalBall.prefab");
        spawned.Transform.WorldPosition = position;
        spawned.SetField("Rigidbody", "GravityScale", gravity);
        spawned.SetField("Rigidbody", "LinearDamping", 0f);
        spawned.GetComponent<Rigidbody>().Velocity = velocity;
        return spawned;
    }

    private void PutCube(Vector3 position)
    {
        if (ChamberController.IsHolding(cube)) chamber.DropCube();
        cube.SetField("Rigidbody", "BodyType", "Dynamic");
        cube.GetComponent<Rigidbody>().Teleport(position, Vector3.Forward, Vector3.Up);
        cube.GetComponent<Rigidbody>().Velocity = Vector3.Zero;
    }

    public override void OnStart()
    {
        On<PortalTraversed>(e =>
        {
            if (e.Traveller != player) return;
            ++portalTransfers;
            if (stage == 11)
            {
                Check(e.IncomingVelocity.Length() > 12f, "drop generates a real high-speed fall");
                Check(playerMover.Velocity.y > 4f, "angled exit redirects falling momentum upward");
                Check(System.Math.Abs(playerMover.Velocity.Length() - e.IncomingVelocity.Length()) < 0.01f,
                    "fling transfer preserves full incoming speed");
            }
        });
    }

    public override void OnUpdate(float dt)
    {
        ++frame;
        if (frame < 8) return;
        if (stage == 0)
        {
            chamber = ChamberController.Active;
            Check(chamber != null, "mechanics controller exists");
            player = World.Find("Player");
            cube = World.Find("Companion Cube");
            playerMover = player.GetComponent<CharacterController>();
            Check(FirstPersonController.TryGet(player, out controller), "first-person controller exists");
            eye = World.GetTransformByName("Player Camera");
            bridge = World.GetTransformByName("Bridge");
            leftGate = World.GetTransformByName("Gate Left");
            rightGate = World.GetTransformByName("Gate Right");
            gateClosedLeft = leftGate.WorldPosition;
            gateClosedRight = rightGate.WorldPosition;
            Check(!chamber.Powered && !chamber.PlateWeighted && !chamber.Completed,
                "puzzle starts unpowered, unweighted and incomplete");
            Check(bridge.WorldPosition.y < -1, "unpowered bridge is retracted");
            Check(World.Find("Portal Panel Entry") && World.Find("Portal Panel Relay")
                && World.Find("Portal Panel Drop") && World.Find("Portal Panel Fling"), "all puzzle portal surfaces exist");
            Check(Physics.Raycast(new Vector3(-8, 1.3f, -5), Vector3.Forward, 8, out RaycastHit glass)
                && glass.Entity.Name.StartsWith("Portal Window"), "relay viewing window blocks physical rays");
            Input.MouseCaptured = false;
            player.SetField("CharacterController", "GravityScale", 0f);
            PutPlayer(World.GetTransformByName("Exit Goal").WorldPosition, Vector3.Forward);
            Begin(1, "completion stays locked before mechanics");
        }
        else if (stage == 1 && Elapsed(3))
        {
            Check(!chamber.Completed, "visiting the exit cannot bypass power and cube requirements");
            PutPlayer(new Vector3(0, 0.9f, -11), Vector3.Forward);
            ball = SpawnBall(new Vector3(-8, 1.3f, -4), Vector3.Forward * 14, 0);
            Begin(2, "relay cannot be shot directly through glass");
        }
        else if (stage == 2 && Elapsed(25))
        {
            Check(!chamber.Powered, "glass prevents a direct receiver shot");
            Check(ball && ball.Transform.WorldPosition.z < -1.1f,
                "physical ball stays on player side of relay window");
            if (ball) ball.Destroy();
            Pass();
            Begin(3, "portal shot route powers the relay");
            Check(Shoot("Blue Portal", new Vector3(-3, 1.6f, -7), new Vector3(-3, 1.6f, -3)),
                "entry panel accepts a portal");
            Vector3 blue = World.GetTransformByName("Blue Portal").WorldPosition;
            Check(!Shoot("Blue Portal", new Vector3(0, 1.6f, -10), new Vector3(0, 12, -10)),
                "dark chamber structure rejects portals");
            Check(Vector3.Distance(blue, World.GetTransformByName("Blue Portal").WorldPosition) < 0.001f,
                "rejected surface leaves existing portal intact");
            Check(Shoot("Orange Portal", new Vector3(-8, 1.6f, -7), new Vector3(-8, 1.6f, 7)),
                "portal beam reaches internal relay panel through viewing window");
            // Use the real E launcher from the normal starting area, including its inherited
            // motion, gravity choice and oblique entry angle. A near-portal synthetic spawn
            // missed the old gravity drop and undersized receiver bugs.
            Transform entrance = World.GetTransformByName("Blue Portal");
            Vector3 firingPosition = new Vector3(0, 0.9f, -11);
            Vector3 aim = (entrance.WorldPosition + entrance.Up * 0.3f
                - (firingPosition + Vector3.Up * 0.7f)).Normalized();
            PutPlayer(firingPosition, aim);
            Check(BallLauncher.Active != null, "normal player launcher exists");
            ball = BallLauncher.Active.FireBall();
            Check(ball && ball.GetField("Rigidbody", "GravityScale", 1f) == 0f,
                "E energy ball follows player aim instead of falling short");
        }
        else if (stage == 3)
        {
            if (chamber.Powered)
            {
                Check(!ball || Vector3.Distance(ball.Transform.WorldPosition,
                    World.GetTransformByName("Relay Receiver").WorldPosition) < 2.3f,
                    "receiver activates from routed ball");
                Pass();
                Begin(4, "powered bridge raises into a usable crossing");
            }
            else if (Elapsed(180))
            {
                Check(false, "routed ball never powered receiver");
                Begin(4, "powered bridge raises into a usable crossing");
            }
        }
        else if (stage == 4 && Elapsed(100))
        {
            Check(chamber.Powered, "relay remains latched after ball absorption");
            Check(System.Math.Abs(bridge.WorldPosition.y + 0.15f) < 0.06f,
                "bridge reaches floor height");
            Check(Physics.Raycast(new Vector3(0, 2, 2), -Vector3.Up, 3, out RaycastHit floor)
                && floor.Entity.Name == "Bridge" && System.Math.Abs(floor.Point.y) < 0.08f,
                "raised bridge has matching collision at floor level");
            Pass();
            Begin(5, "gallery access and cube carrying");
            Check(Shoot("Blue Portal", new Vector3(2, 1.6f, 12), new Vector3(7.5f, 5.2f, 16)),
                "gallery portal is visible and fits from the lab");
            Vector3 cubePosition = cube.Transform.WorldPosition;
            Vector3 cameraPosition = cubePosition + new Vector3(0, 1.1f, -1.6f);
            Vector3 gaze = (cubePosition - cameraPosition).Normalized();
            PutPlayer(cameraPosition - Vector3.Up * 0.7f, gaze);
            Check(chamber.TryGrabCube(), "nearby aimed cube can be grabbed");
        }
        else if (stage == 5 && Elapsed(5))
        {
            Check(ChamberController.IsHolding(cube), "carried cube stays held");
            Check(Vector3.Distance(cube.Transform.WorldPosition, eye.WorldPosition) < 2.4f,
                "held cube follows player camera");
            Check(cube.GetField("BoxCollider", "IsTrigger", false), "held cube cannot block its carrier");
            // Place the held cube ahead of the eye across an actual mounted doorway.
            Check(Shoot("Blue Portal", new Vector3(-3, 1.6f, -7), new Vector3(-3, 1.6f, -3)), "carry entry placed");
            Check(Shoot("Orange Portal", new Vector3(-8, 1.6f, -7), new Vector3(-8, 1.6f, 7)), "carry exit placed");
            Portal entrance = Portal.Instances["Blue Portal"];
            Portal destination = Portal.Instances["Orange Portal"];
            Vector3 heldEye = entrance.transform.WorldPosition + entrance.transform.Up * 0.3f + entrance.transform.Forward * 0.85f;
            PutPlayer(heldEye - Vector3.Up * 0.7f, -entrance.transform.Forward);
            chamber.OnLateUpdate(0);
            Check(Vector3.Dot(cube.Transform.WorldPosition - destination.transform.WorldPosition,
                destination.transform.Forward) > 0f, "held cube leads player through portal instead of hitting host wall");
            Check(World.Find("Portal Image / Companion Cube"), "straddling cube has a visual image at the entrance");
            Portal.ResetTravellerHistory(player);
            playerMover.Velocity = -entrance.transform.Forward * 8f;
            Begin(15, "walking through a portal while carrying");
        }
        else if (stage == 15 && Elapsed(20))
        {
            Check(player.Transform.WorldPosition.x < -6f, "native capsule crosses the portal while holding its cube");
            Check(ChamberController.IsHolding(cube), "portal crossing preserves the held cube");
            Check(Vector3.Distance(cube.Transform.WorldPosition, eye.WorldPosition) < 2.4f, "cube follows carrier after crossing");
            chamber.DropCube();
            Check(!cube.GetField("BoxCollider", "IsTrigger", true), "drop restores solid cube collision");
            Check(!ChamberController.IsHolding(cube), "dropping cube releases carry state");
            Pass();
            PutPlayer(new Vector3(0, 0.9f, 8), Vector3.Forward);
            Begin(6, "cube weights the plate and opens the gate");
            PutCube(new Vector3(0, 0.72f, 13));
        }
        else if (stage == 6 && Elapsed(100))
        {
            Check(chamber.PlateWeighted, "physical cube activates floor plate");
            Check(leftGate.WorldPosition.x < gateClosedLeft.x - 1.6f
                && rightGate.WorldPosition.x > gateClosedRight.x + 1.6f, "split gate opens while weighted");
            Pass();
            PutPlayer(new Vector3(0, 0.9f, 20.5f), Vector3.Forward);
            Begin(13, "gate checkpoint records progress");
        }
        else if (stage == 13 && Elapsed(4))
        {
            Check(chamber.CheckpointIndex >= 2, "entering momentum room saves its checkpoint");
            PutCube(new Vector3(4, 0.7f, 13));
            Begin(7, "removing cube closes the gate");
        }
        else if (stage == 7 && Elapsed(85))
        {
            Check(!chamber.PlateWeighted, "plate clears after cube is removed");
            Check(Vector3.Distance(leftGate.WorldPosition, gateClosedLeft) < 0.08f
                && Vector3.Distance(rightGate.WorldPosition, gateClosedRight) < 0.08f,
                "gate closes again without the cube");
            Check(chamber.CheckpointPosition.z < 18f, "lost switch weight keeps reset on accessible side of gate");
            chamber.ResetToCheckpoint();
            Check(player.Transform.WorldPosition.z < 18f, "reset cannot trap player behind an unweighted gate");
            Pass();
            PutPlayer(new Vector3(0, 0.9f, 8), Vector3.Forward);
            Begin(8, "checkpoint recovers pit falls");
        }
        else if (stage == 8 && Elapsed(4))
        {
            resetTarget = chamber.CheckpointPosition;
            Check(chamber.CheckpointIndex >= 1, "crossing bridge records checkpoint");
            PutPlayer(new Vector3(0, -3.5f, 2), Vector3.Forward);
            Begin(9, "checkpoint recovers pit falls");
        }
        else if (stage == 9 && Elapsed(4))
        {
            Check(Vector3.Distance(player.Transform.WorldPosition, resetTarget) < 0.12f,
                "pit fall respawns at saved checkpoint");
            Check(chamber.Powered, "checkpoint recovery keeps relay power");
            PutPlayer(new Vector3(2, 1.5f, 10), Vector3.Forward);
            chamber.ResetToCheckpoint();
            Check(Vector3.Distance(player.Transform.WorldPosition, resetTarget) < 0.12f,
                "manual reset returns to same checkpoint");
            Pass();
            PutCube(new Vector3(0, 0.72f, 13));
            Begin(10, "fling panels and physical exit route");
        }
        else if (stage == 10 && Elapsed(95))
        {
            Check(chamber.PlateWeighted && chamber.Powered, "exit route is powered and weighted");
            Check(Shoot("Blue Portal", new Vector3(0, 1.6f, 26), new Vector3(0, -10, 26)),
                "drop shaft floor accepts portal");
            Check(Shoot("Orange Portal", new Vector3(0, 1.6f, 21), new Vector3(0, 3.3f, 31)),
                "angled fling panel accepts portal from launch room");
            Check(World.GetTransformByName("Orange Portal").Forward.y > 0.5f,
                "fling exit redirects velocity upward");
            player.SetField("CharacterController", "GravityScale", 1f);
            PutPlayer(new Vector3(0, 0.9f, 26), Vector3.Forward);
            playerMover.Velocity = Vector3.Zero;
            Check(chamber.TryOpenHatch(), "drop hatch opens from its standing platform");
            portalTransfers = 0;
            Begin(11, "fling panels and physical exit route");
        }
        else if (stage == 11)
        {
            if (chamber.Completed)
            {
                Check(portalTransfers > 0, "final route actually traverses a portal");
                Check(player.Transform.WorldPosition.y > 5.4f, "fling reaches the elevated exit");
                Pass();
                Begin(12, "return to overview");
            }
            else if (Elapsed(320))
            {
                Check(false, "drop-to-angled portal route did not reach chamber completion");
                Debug.Log("CHAMBER DIAGNOSTIC: final position " + player.Transform.WorldPosition
                    + " velocity " + playerMover.Velocity + " transfers " + portalTransfers);
                Begin(12, "return to overview");
            }
        }
        else if (stage == 12 && !finishReported)
        {
            finishReported = true;
            player.SetField("CharacterController", "GravityScale", 0f);
            PutPlayer(new Vector3(0, 0.9f, -11), Vector3.Forward);
            Debug.Log(failures == 0 ? "CHAMBER ALL PASSED: " + checks : "CHAMBER FAILED: " + failures + " of " + checks);
        }
    }
}
