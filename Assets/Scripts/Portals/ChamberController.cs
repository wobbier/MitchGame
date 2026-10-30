using System.Collections.Generic;
using ScriptCore;

// Puzzle state belongs to the chamber, rather than the gun: returning to a checkpoint keeps
// completed work, while physics objects and pressure switches continue to behave normally.
[ExecutionOrder(150)]
public class ChamberController : Script
{
    public static ChamberController Active;
    [HideInInspector] public bool Powered;
    [HideInInspector] public bool PlateWeighted;
    [HideInInspector] public bool Completed;
    [HideInInspector] public int CheckpointIndex;
    [HideInInspector] public bool HatchOpened;
    [HideInInspector] public EntityRef HeldReference;

    public Entity HeldCube => heldCube;
    // If the cube was lost after reaching the fling room, return in front of the switch gate
    // instead of trapping the player behind it while the cube has respawned in the gallery.
    public Vector3 CheckpointPosition => CheckpointIndex >= 2 && (Completed || (Powered && PlateWeighted))
        ? new Vector3(0, 0.9f, 20.5f) : CheckpointIndex >= 1 ? new Vector3(0, 0.9f, 8) : new Vector3(0, 0.9f, -11);
    public static bool IsHolding(Entity entity) => Active != null && Active.heldCube && Active.heldCube == entity;

    private Entity player, cube, receiver, plate, bridge, gateLeft, gateRight, exitDoor, hatch;
    private Entity heldCube;
    private CharacterController mover;
    private Transform camera;
    private UIModel hud;
    private readonly Dictionary<Entity, Vector3> ballPositions = new Dictionary<Entity, Vector3>();
    private Vector3 cubeSpawn = new Vector3(7.5f, 3.55f, 12.5f);
    private float toastTime, strandedTime;
    private bool ready;

    public override void OnStart()
    {
        Active = this;
        player = World.Find("Player");
        cube = World.Find("Companion Cube");
        receiver = World.Find("Relay Receiver");
        plate = World.Find("Pressure Plate");
        bridge = World.Find("Bridge");
        gateLeft = World.Find("Gate Left");
        gateRight = World.Find("Gate Right");
        exitDoor = World.Find("Exit Door");
        hatch = World.Find("Portal Window Drop Hatch");
        Entity eye = World.Find("Player Camera");
        camera = eye ? eye.Transform : null;
        mover = player ? player.GetComponent<CharacterController>() : null;
        ready = player && cube && receiver && plate && mover != null && camera != null;
        heldCube = HeldReference.Resolve();
        if (heldCube) SetHeldPhysics(heldCube, true);
        hud = UI.Model("chamber");
        hud.Set("toast", "");
        hud.Set("interaction", "");
        PublishHud();
        UpdateLamps();
        MoveHatch(HatchOpened);
        if (!ready) Debug.Warning("Chamber Controller: missing player, cube, receiver, plate or camera");
    }

    public override void OnReload() { OnStart(); }

    public override void OnDestroy()
    {
        if (heldCube) DropCube();
        if (Active == this) Active = null;
    }

    public override void OnUpdate(float deltaTime)
    {
        if (!ready) return;
        toastTime -= deltaTime;
        if (toastTime <= 0) hud.Set("toast", "");
        if (Input.MouseCaptured && Input.WasKeyPressed(KeyCode.F))
        {
            if (heldCube) DropCube();
            else if (!TryGrabCube()) TryOpenHatch();
        }
        if (Input.WasKeyPressed(KeyCode.R)) ResetToCheckpoint();

        UpdateReceiver();
        UpdatePressurePlate();
        MoveMechanisms(deltaTime);
        UpdateRecovery(deltaTime);
        UpdateCheckpoints();
        CheckCompletion();
        PublishHud();
    }

    // Portals run at order 100. Carrying follows their final eye pose in this same frame.
    public override void OnLateUpdate(float deltaTime)
    {
        if (!ready || !heldCube) return;
        Vector3 origin = camera.WorldPosition;
        Vector3 direction = (camera.Forward * 1.55f - camera.Up * 0.24f).Normalized();
        float distance = 1.55f;
        // The hold ray uses the same opening as the player. A cube can lead the player
        // through a doorway; do not retract it against the host wall or push the capsule.
        Portal passage = Portal.FindRayPassage(origin, direction, distance, out float crossing);
        foreach (RaycastHit hit in Physics.RaycastAll(origin, direction, distance + 0.50f))
        {
            if (hit.Entity == player || hit.Entity == heldCube || IsCubePart(hit.Entity)) continue;
            if (passage != null && hit.Entity == passage.SurfaceHost.Resolve()) continue;
            distance = Mathf.Clamp(hit.Distance - 0.55f, 0.65f, distance);
            break;
        }
        Vector3 target = origin + direction * distance;
        Vector3 forward = camera.Forward, up = camera.Up;
        if (passage != null && distance >= crossing)
        {
            target = passage.ThroughPoint(target);
            forward = passage.ThroughDirection(forward);
            up = passage.ThroughDirection(up);
        }
        Rigidbody body = heldCube.GetComponent<Rigidbody>();
        if (body != null)
        {
            body.Teleport(target, forward, up);
            body.Velocity = Vector3.Zero;
        }
        Portal.UpdateTravellerImages();
    }

    private static void SetHeldPhysics(Entity entity, bool held)
    {
        entity.SetField("Rigidbody", "BodyType", held ? "Kinematic" : "Dynamic");
        // Held geometry is positioned by the carry ray, not the solver. In particular it
        // must never become a kinematic obstacle trapping its own player's capsule.
        entity.SetField("BoxCollider", "IsTrigger", held);
    }

    public bool TryReceiveBall(Entity ball)
    {
        if (!ready || Powered || !ball || !ball.HasComponent<Rigidbody>() || !ball.Name.StartsWith("Portal Ball")) return false;
        if (!InsideReceiver(ball.Transform.WorldPosition)) return false;
        AcceptBall(ball);
        return true;
    }

    private void AcceptBall(Entity ball)
    {
        Powered = true;
        ball.Destroy();
        ballPositions.Clear();
        Toast("RELAY ONLINE  /  BRIDGE DEPLOYING", 4f);
        Audio.PlayOneShot("Assets/Sounds/Portals/Pulse.wav", 0.5f);
        UpdateLamps();
        EventBus.Publish(new ChamberProgressChanged("relay", true));
    }

    private void UpdateReceiver()
    {
        if (Powered) return;
        Vector3 center = receiver.Transform.WorldPosition;
        var positions = new Dictionary<Entity, Vector3>();
        foreach (Entity ball in Query.WithComponent("Rigidbody"))
        {
            if (!ball || !ball.Name.StartsWith("Portal Ball")) continue;
            Vector3 current = ball.Transform.WorldPosition;
            Vector3 previous = ballPositions.TryGetValue(ball, out Vector3 last) ? last : current;
            positions[ball] = current;
            Vector3 segment = current - previous;
            float length = segment.LengthSquared();
            Vector3 normal = receiver.Transform.Forward;
            float along = Vector3.Dot(segment, normal);
            float t = Mathf.Abs(along) > 0.0001f
                ? Vector3.Dot(center - previous, normal) / along : -1f;
            // Match the wide visible collector. Ordinary angled shots from the start platform
            // retain lateral momentum through portals, rather than needing a perpendicular shot.
            bool nearby = InsideReceiver(current);
            bool swept = length < 9f && t >= 0f && t <= 1f && InsideReceiver(previous + segment * t);
            if (!nearby && !swept) continue;
            AcceptBall(ball);
            return;
        }
        ballPositions.Clear();
        foreach (var pair in positions) ballPositions[pair.Key] = pair.Value;
    }

    private bool InsideReceiver(Vector3 point)
    {
        Transform target = receiver.Transform;
        Vector3 offset = point - target.WorldPosition;
        return Mathf.Abs(Vector3.Dot(offset, target.Right)) <= 1.8f
            && Mathf.Abs(Vector3.Dot(offset, target.Up)) <= 1.2f
            && Mathf.Abs(Vector3.Dot(offset, target.Forward)) <= 0.55f;
    }

    private void UpdatePressurePlate()
    {
        Transform box = cube.Transform;
        Transform button = plate.Transform;
        Vector3 cubeSize = cube.GetField("BoxCollider", "Size", new Vector3(2, 2, 2));
        Vector3 plateSize = plate.GetField("BoxCollider", "Size", new Vector3(2, 2, 2));
        Vector3 boxScale = box.Scale, plateScale = button.Scale;
        Vector3 halfBox = new Vector3(Mathf.Abs(boxScale.x * cubeSize.x), Mathf.Abs(boxScale.y * cubeSize.y),
            Mathf.Abs(boxScale.z * cubeSize.z)) * 0.5f;
        Vector3 halfPlate = new Vector3(Mathf.Abs(plateScale.x * plateSize.x), Mathf.Abs(plateScale.y * plateSize.y),
            Mathf.Abs(plateScale.z * plateSize.z)) * 0.5f;
        Vector3 offset = box.WorldPosition - button.WorldPosition;
        float x = Vector3.Dot(offset, button.Right), z = Vector3.Dot(offset, button.Forward);
        float radiusX = ProjectBoxExtent(box, halfBox, button.Right);
        float radiusZ = ProjectBoxExtent(box, halfBox, button.Forward);
        float bottom = Vector3.Dot(offset, button.Up) - ProjectBoxExtent(box, halfBox, button.Up);
        // Test the actual collider footprint: an off-centre or rotated cube still weighs on
        // the plate. Floor-level cubes beside it and held/hovering cubes do not press it.
        float overlapX = Mathf.Min(halfPlate.x, x + radiusX) - Mathf.Max(-halfPlate.x, x - radiusX);
        float overlapZ = Mathf.Min(halfPlate.z, z + radiusZ) - Mathf.Max(-halfPlate.z, z - radiusZ);
        bool weighted = !heldCube && overlapX > 0.08f && overlapZ > 0.08f
            && bottom >= halfPlate.y - 0.08f && bottom <= halfPlate.y + 0.10f;
        if (weighted == PlateWeighted) return;
        PlateWeighted = weighted;
        UpdateLamps();
        EventBus.Publish(new ChamberProgressChanged("plate", weighted));
        Toast(weighted ? (Powered ? "SWITCH HELD  /  GATE OPEN" : "GATE OPEN  /  RELAY STILL OFFLINE")
            : "SWITCH RELEASED  /  GATE CLOSING", 3f);
    }

    private static float ProjectBoxExtent(Transform box, Vector3 half, Vector3 axis)
        => Mathf.Abs(Vector3.Dot(box.Right, axis)) * half.x
            + Mathf.Abs(Vector3.Dot(box.Up, axis)) * half.y
            + Mathf.Abs(Vector3.Dot(box.Forward, axis)) * half.z;

    private void MoveMechanisms(float deltaTime)
    {
        Move(bridge, new Vector3(0, Powered ? -0.15f : -3f, 2), 0.18f, deltaTime);
        // The local switch drives this gate directly. Relay power belongs to the bridge
        // and final launch machinery, so an out-of-order solve still gives immediate feedback.
        bool open = PlateWeighted;
        bool exitUnlocked = Powered && PlateWeighted;
        // Keep the shutters open if the player is directly in their path; the cube still has to
        // hold the switch for progress. This avoids closing a kinematic panel through a capsule.
        Vector3 p = player.Transform.WorldPosition;
        bool crossingGate = Mathf.Abs(p.z - 18f) < 0.8f && Mathf.Abs(p.x) < 2.1f && p.y < 4.8f;
        bool previouslyOpen = gateLeft && Mathf.Abs(gateLeft.Transform.WorldPosition.x) > 1.4f;
        bool gateOpen = open || (crossingGate && previouslyOpen);
        Move(gateLeft, new Vector3(gateOpen ? -3f : -0.95f, 2.25f, 18), 0.12f, deltaTime);
        Move(gateRight, new Vector3(gateOpen ? 3f : 0.95f, 2.25f, 18), 0.12f, deltaTime);
        Move(exitDoor, new Vector3(0, exitUnlocked || Completed ? 11f : 7f, 17.65f), 0.14f, deltaTime);
    }

    private static void Move(Entity entity, Vector3 target, float halfLife, float deltaTime)
    {
        if (!entity) return;
        Vector3 next = Mathf.Damp(entity.Transform.WorldPosition, target, halfLife, deltaTime);
        if (Vector3.Distance(next, target) < 0.001f) next = target;
        entity.Transform.WorldPosition = next;
    }

    public bool TryGrabCube()
    {
        if (!ready || heldCube || !CanGrabCube()) return false;
        heldCube = cube;
        HeldReference = new EntityRef { Guid = cube.Guid };
        SetHeldPhysics(cube, true);
        cube.GetComponent<Rigidbody>().Velocity = Vector3.Zero;
        Toast("CUBE HELD  /  F TO DROP", 2f);
        UpdatePressurePlate();
        return true;
    }

    public void DropCube()
    {
        if (!heldCube) return;
        Entity released = heldCube;
        heldCube = Entity.Null;
        HeldReference = default;
        SetHeldPhysics(released, false);
        Rigidbody body = released.GetComponent<Rigidbody>();
        if (body != null) body.Velocity = mover != null ? mover.Velocity : Vector3.Zero;
    }

    private bool CanGrabCube()
    {
        if (!cube || camera == null) return false;
        Vector3 delta = cube.Transform.WorldPosition - camera.WorldPosition;
        if (delta.LengthSquared() > 2.7f * 2.7f || Vector3.Dot(delta.Normalized(), camera.Forward) < 0.65f) return false;
        foreach (RaycastHit hit in Physics.RaycastAll(camera.WorldPosition, delta.Normalized(), delta.Length()))
        {
            if (hit.Entity == player) continue;
            return hit.Entity == cube || IsCubePart(hit.Entity);
        }
        return true;
    }

    private bool IsCubePart(Entity entity)
    {
        for (Entity e = entity; e; e = e.Transform.Parent)
            if (e == cube) return true;
        return false;
    }

    public void ResetToCheckpoint()
    {
        if (!ready) return;
        if (heldCube)
        {
            DropCube();
            ResetCube();
        }
        Vector3 point = CheckpointPosition;
        mover.Teleport(point, Vector3.Forward);
        mover.Velocity = Vector3.Zero;
        if (FirstPersonController.TryGet(player, out FirstPersonController controller))
            controller.ApplyPortalView(point + Vector3.Up * 0.7f, Vector3.Forward, Vector3.Up);
        Portal.ResetTravellerHistory(player);
        strandedTime = 0f;
        HatchOpened = false;
        MoveHatch(false);
        int restored = point.z > 18 ? 3 : point.z > 0 ? 2 : 1;
        Toast("RETURNED TO CHECKPOINT " + restored, 2.5f);
    }

    public bool TryOpenHatch()
    {
        if (!ready || !hatch || HatchOpened || !NearHatch()) return false;
        if (!Powered || !PlateWeighted)
        {
            Toast(!Powered ? "RELAY OFFLINE  /  POWER THE DROP HATCH" : "SWITCH RELEASED  /  REPLACE THE CUBE", 3f);
            return false;
        }
        HatchOpened = true;
        // Teleport the support sideways rather than sweeping it: a kinematic sweep would give
        // the player a sideways push just before a puzzle that needs a straight vertical fall.
        MoveHatch(true);
        Toast("HATCH RELEASED  /  MOMENTUM TRANSFER", 3f);
        EventBus.Publish(new ChamberProgressChanged("hatch", true));
        return true;
    }

    private bool NearHatch()
    {
        if (!player || !hatch) return false;
        Vector3 p = player.Transform.WorldPosition;
        return Mathf.Abs(p.x) < 1.1f && Mathf.Abs(p.z - 26f) < 1.1f && p.y > -1f && p.y < 3f;
    }

    private void MoveHatch(bool opened)
    {
        if (!hatch) return;
        Vector3 destination = new Vector3(opened ? 6f : 0f, -0.15f, 26f);
        Rigidbody body = hatch.GetComponent<Rigidbody>();
        if (body != null) body.Teleport(destination, Vector3.Forward, Vector3.Up);
        else hatch.Transform.WorldPosition = destination;
    }

    private void ResetCube()
    {
        if (!cube) return;
        if (heldCube) DropCube();
        cube.SetField("Rigidbody", "BodyType", "Dynamic");
        Rigidbody body = cube.GetComponent<Rigidbody>();
        body.Teleport(cubeSpawn, Vector3.Forward, Vector3.Up);
        body.Velocity = Vector3.Zero;
        Portal.ResetTravellerHistory(cube);
    }

    private void UpdateRecovery(float deltaTime)
    {
        Vector3 p = player.Transform.WorldPosition;
        if ((p.z > -2.5f && p.z < 6.5f && p.y < -2.5f) || p.y < -12.5f)
        {
            ResetToCheckpoint();
            return;
        }
        bool atBottom = p.y < -7f && mover.IsGrounded;
        strandedTime = atBottom ? strandedTime + deltaTime : 0;
        if (strandedTime >= 1.7f) ResetToCheckpoint();
        if (!heldCube && cube.Transform.WorldPosition.y < -3f)
        {
            ResetCube();
            Toast("CUBE RETURNED TO THE GALLERY", 3f);
        }
    }

    private void UpdateCheckpoints()
    {
        Vector3 p = player.Transform.WorldPosition;
        int next = CheckpointIndex;
        if (Powered && p.z >= 7f && p.z < 18f && p.y > -1f) next = System.Math.Max(next, 1);
        if (Powered && PlateWeighted && p.z >= 19f && p.y > -1f) next = System.Math.Max(next, 2);
        if (next == CheckpointIndex) return;
        CheckpointIndex = next;
        Toast("CHECKPOINT " + (CheckpointIndex + 1) + " SAVED", 3f);
        EventBus.Publish(new ChamberProgressChanged("checkpoint", true));
    }

    private void CheckCompletion()
    {
        if (Completed || !Powered || !PlateWeighted || !mover.IsGrounded) return;
        Entity goal = World.Find("Exit Goal");
        Vector3 destination = goal ? goal.Transform.WorldPosition : new Vector3(0, 6.1f, 18.8f);
        Vector3 p = player.Transform.WorldPosition;
        Vector3 horizontal = new Vector3(p.x - destination.x, 0, p.z - destination.z);
        if (p.y < 5.7f || p.y > 9f || horizontal.LengthSquared() > 1.7f * 1.7f) return;
        Completed = true;
        Toast("CHAMBER COMPLETE", 8f);
        UpdateLamps();
        EventBus.Publish(new ChamberProgressChanged("complete", true));
    }

    private void UpdateLamps()
    {
        Vector3 relayColor = new Vector3(0.1f, 0.85f, 1f);
        Lamp("Relay Lamp", Powered, relayColor);
        Lamp("Relay Socket Core", Powered, relayColor);
        Lamp("Relay Status Face", Powered, relayColor);
        SetSign("Relay Status Label", Powered ? "RELAY ONLINE" : "RECEIVER / ROUTE AN ENERGY BALL");
        SetSign("Bridge Notice", Powered ? "BRIDGE ONLINE" : "POWER: ROUTE AN ENERGY BALL / E TO FIRE");
        Vector3 switchColor = new Vector3(0.08f, 0.9f, 0.55f);
        Lamp("Plate Lamp", PlateWeighted, switchColor);
        if (plate)
        {
            Mesh mesh = plate.GetComponent<Mesh>();
            mesh?.SetMaterial("DiffuseColor", PlateWeighted ? switchColor : new Vector3(0.33f, 0.16f, 0.055f));
            mesh?.SetMaterial("EmissiveColor", switchColor);
            mesh?.SetMaterial("EmissiveIntensity", PlateWeighted ? 0.5f : 0f);
        }
        Entity plateSign = World.Find("Plate Prompt");
        if (plateSign)
        {
            TextRenderer text = plateSign.GetComponent<TextRenderer>();
            if (text != null) text.Text = PlateWeighted ? "SWITCH HELD / GATE OPEN" : "CUBE ON SWITCH = OPEN GATE";
        }
        Lamp("Exit Lamp", Completed || (Powered && PlateWeighted), new Vector3(0.2f, 1f, 0.55f));
    }

    private static void SetSign(string name, string value)
    {
        Entity sign = World.Find(name);
        if (sign) { TextRenderer text = sign.GetComponent<TextRenderer>(); if (text != null) text.Text = value; }
    }

    private static void Lamp(string name, bool on, Vector3 color)
    {
        Entity lamp = World.Find(name);
        if (!lamp) return;
        Mesh mesh = lamp.GetComponent<Mesh>();
        mesh?.SetMaterial("EmissiveColor", on ? color : new Vector3(0.16f, 0.22f, 0.27f));
        mesh?.SetMaterial("EmissiveIntensity", on ? 3f : 0.3f);
        if (lamp.HasComponent("Light"))
        {
            lamp.SetField("Light", "Color", color);
            lamp.SetField("Light", "Intensity", on ? 2f : 0.2f);
        }
    }

    private void Toast(string text, float seconds)
    {
        toastTime = seconds;
        hud.Set("toast", text);
    }

    private void PublishHud()
    {
        hud.Set("relay", Powered);
        hud.Set("plate", PlateWeighted);
        hud.Set("complete", Completed);
        hud.Set("checkpoint", "CHECKPOINT " + (CheckpointIndex + 1));
        string objective = !Powered ? "01  POWER THE RELAY" : !PlateWeighted ? "02  WEIGHT THE SWITCH" : "03  USE YOUR MOMENTUM";
        string detail = !Powered ? (PlateWeighted
            ? "Power is still off: left click BALL ENTRY, right click the white wall through the glass, then aim inside blue and press E."
            : "1. Left click BALL ENTRY for blue. 2. Right click the white wall THROUGH THE GLASS for orange. 3. Aim inside blue and press E to fire an energy ball.")
            : !PlateWeighted ? "Reach the upper gallery. Bring its cube to the amber floor switch."
            : "Link the shaft floor to the angled panel. Stand on the hatch and press F to drop through.";
        hud.Set("objective", Completed ? "TEST COMPLETE" : objective);
        hud.Set("detail", Completed ? "Relay powered. Switch held. Momentum transfer successful." : detail);
        string interaction = heldCube ? "F  DROP CUBE" : ready && CanGrabCube() ? "F  PICK UP CUBE"
            : ready && Powered && PlateWeighted && !HatchOpened && NearHatch() ? "F  RELEASE DROP HATCH" : "";
        hud.Set("interaction", interaction);
    }
}

public readonly record struct ChamberProgressChanged(string Mechanic, bool Active);
