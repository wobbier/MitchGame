using System.Collections.Generic;
using ScriptCore;

// The capsule stays upright, while the view keeps a complete orientation through a portal.
// Recover only roll and the temporary eye offset afterwards: neither recovery changes the aim.
public class FirstPersonController : Script
{
    public string CameraName = "Player Camera";
    public float Sensitivity = 1.0f;
    public bool InvertY = false;
    public float WalkSpeed = 5.0f;
    public float SprintSpeed = 9.0f;
    public float AirAcceleration = 6.0f;
    public float UprightDegreesPerSecond = 180.0f;
    public float EyeOffsetHalfLife = 0.12f;

    // Preserve the authored offset and native settings across a script hot reload.
    [HideInInspector] public Vector3 AuthoredEyeOffset;
    [HideInInspector] public bool HasAuthoredEyeOffset;
    [HideInInspector] public float OriginalAirControl = -1f;

    private static readonly Dictionary<Entity, FirstPersonController> instances = new Dictionary<Entity, FirstPersonController>();
    private CharacterController character;
    private Transform head;
    private Quaternion viewRotation = Quaternion.Identity;
    private Vector3 eyeOffsetWorld;
    private Vector3 movementForward = Vector3.Forward;
    private Vector3 moveDirection;
    private float recoveryDelay;
    private float rollSign = 1f;

    public static bool TryGet(Entity traveller, out FirstPersonController controller)
        => instances.TryGetValue(traveller, out controller);

    public override void OnStart()
    {
        instances[Entity] = this;
        character = GetComponent<CharacterController>();
        Entity camera = World.Find(CameraName);
        head = camera ? camera.Transform : null;
        if (head != null)
        {
            if (!HasAuthoredEyeOffset)
            {
                AuthoredEyeOffset = head.Position;
                HasAuthoredEyeOffset = true;
            }
            viewRotation = Quaternion.LookRotation(head.Forward, head.Up);
            eyeOffsetWorld = head.WorldPosition - transform.WorldPosition - ToWorldDirection(AuthoredEyeOffset);
        }
        Vector3 facing = transform.Forward;
        movementForward = new Vector3(facing.x, 0f, facing.z).Normalized();
        if (movementForward.LengthSquared() < 0.01f) movementForward = Vector3.Forward;
        if (character != null)
        {
            if (OriginalAirControl < 0f) OriginalAirControl = Entity.GetField("CharacterController", "AirControl", 0.3f);
            // The native mover otherwise brakes every airborne velocity toward walking speed.
            // Air steering below adds bounded acceleration without discarding a portal fling.
            Entity.SetField("CharacterController", "AirControl", 0f);
        }
        Input.MouseCaptured = true;
    }

    public override void OnReload() { OnStart(); }

    public override void OnDestroy()
    {
        instances.Remove(Entity);
        if (Entity && OriginalAirControl >= 0f) Entity.SetField("CharacterController", "AirControl", OriginalAirControl);
        Input.MouseCaptured = false;
    }

    // Called immediately after the upright capsule has been teleported. Both eye position and
    // the complete view frame are the exact portal transform, including at a vertical gaze.
    public void ApplyPortalView(Vector3 eyePosition, Vector3 forward, Vector3 up)
    {
        if (head == null) return;
        viewRotation = Quaternion.LookRotation(forward, up);
        Vector3 bodyFacing = transform.Forward;
        Vector3 planarFacing = new Vector3(bodyFacing.x, 0f, bodyFacing.z);
        if (planarFacing.LengthSquared() > 0.001f) movementForward = planarFacing.Normalized();
        eyeOffsetWorld = eyePosition - transform.WorldPosition - ToWorldDirection(AuthoredEyeOffset);
        head.WorldPosition = eyePosition;
        head.LookDirection(viewRotation * Vector3.Forward, viewRotation * Vector3.Up);
        recoveryDelay = 0.04f;
    }

    public override void OnUpdate(float deltaTime)
    {
        if (character == null) return;
        if (Input.WasActionPressed("Pause")) Input.MouseCaptured = false;
        else if (!Input.MouseCaptured && Input.WasActionPressed("Fire")) Input.MouseCaptured = true;

        if (head != null)
        {
            if (Input.MouseCaptured)
            {
                ApplyLookInput(Input.GetActionVector2("Look"));
            }

            recoveryDelay -= deltaTime;
            if (recoveryDelay <= 0f)
            {
                RecoverUpright(deltaTime);
                eyeOffsetWorld = Mathf.Damp(eyeOffsetWorld, Vector3.Zero, EyeOffsetHalfLife, deltaTime);
            }
            Vector3 gaze = viewRotation * Vector3.Forward;
            Vector3 planar = new Vector3(gaze.x, 0, gaze.z);
            // At a vertical gaze yaw is undefined. Retain the last stable movement heading.
            if (planar.LengthSquared() > 0.01f) movementForward = planar.Normalized();
            transform.LookDirection(movementForward, Vector3.Up);
            head.Position = AuthoredEyeOffset + new Vector3(
                Vector3.Dot(eyeOffsetWorld, transform.Right),
                Vector3.Dot(eyeOffsetWorld, transform.Up),
                Vector3.Dot(eyeOffsetWorld, transform.Forward));
            head.LookDirection(gaze, viewRotation * Vector3.Up);
        }

        Vector2 move = Input.GetActionVector2("Move");
        Vector3 movementRight = Vector3.Cross(Vector3.Up, movementForward);
        moveDirection = movementRight * move.x + movementForward * move.y;
        if (moveDirection.LengthSquared() > 1f) moveDirection = moveDirection.Normalized();
        character.MaxSpeed = Input.IsActionPressed("Sprint") ? SprintSpeed : WalkSpeed;
        character.SetMoveInput(moveDirection);
        if (Input.WasActionPressed("Jump") && character.IsGrounded) character.Jump();
    }

    // Clamp the swept pitch angle, rather than testing only the final direction: a
    // large mouse delta can jump over a pole and end up inside the old direction limit.
    public void ApplyLookInput(Vector2 look)
    {
        viewRotation = (Quaternion.AngleAxis(look.x * Sensitivity, Vector3.Up) * viewRotation).Normalized();
        Vector3 forward = viewRotation * Vector3.Forward;
        Vector3 right = viewRotation * Vector3.Right;
        float elevation = Mathf.Atan2(forward.y, Mathf.Sqrt(forward.x * forward.x + forward.z * forward.z)) * Mathf.Rad2Deg;
        float requested = (InvertY ? look.y : -look.y) * Sensitivity;
        if (requested == 0f) return; // An exact portal-mapped pole remains untouched until input.
        // Positive rotation about right lowers the gaze. Account for temporary portal roll
        // without discarding the mapped view frame or moving the aim during roll recovery.
        float pitchSign = Vector3.Dot(Vector3.Cross(right, forward), Vector3.Up) > 0f ? 1f : -1f;
        float change = Mathf.Clamp(elevation + requested * pitchSign, -89f, 89f) - elevation;
        viewRotation = (Quaternion.AngleAxis(change * pitchSign, right) * viewRotation).Normalized();
    }

    public override void OnFixedUpdate(float deltaTime)
    {
        if (character == null || character.IsGrounded) return;
        float amount = moveDirection.Length();
        if (amount < 0.001f) return;
        Vector3 direction = moveDirection / amount;
        Vector3 velocity = character.Velocity;
        float along = Vector3.Dot(velocity, direction);
        float limit = character.MaxSpeed * amount;
        // Keep all perpendicular and excess forward momentum. Releasing input adds no drag.
        if (along < limit)
            character.Velocity = velocity + direction * Mathf.Min(limit - along, AirAcceleration * amount * deltaTime);
    }

    private Vector3 ToWorldDirection(Vector3 local)
        => transform.Right * local.x + transform.Up * local.y + transform.Forward * local.z;

    private void RecoverUpright(float deltaTime)
    {
        Vector3 forward = viewRotation * Vector3.Forward;
        Vector3 up = viewRotation * Vector3.Up;
        Vector3 desiredUp = Vector3.Up - forward * Vector3.Dot(Vector3.Up, forward);
        // The horizon is undefined looking straight up/down; do not manufacture a 180-degree flip.
        if (desiredUp.LengthSquared() < 0.04f) return;
        desiredUp = desiredUp.Normalized();
        float sin = Vector3.Dot(Vector3.Cross(up, desiredUp), forward);
        float cos = Mathf.Clamp(Vector3.Dot(up, desiredUp), -1f, 1f);
        float angle = Mathf.Atan2(sin, cos) * Mathf.Rad2Deg;
        if (Mathf.Abs(sin) > 0.001f) rollSign = angle < 0f ? -1f : 1f;
        else if (cos < 0f) angle = rollSign * 180f;
        float correction = angle * (1f - (float)System.Math.Exp(-deltaTime * 8f));
        float limit = Mathf.Max(0f, UprightDegreesPerSecond) * deltaTime;
        correction = Mathf.Clamp(correction, -limit, limit);
        viewRotation = (Quaternion.AngleAxis(correction, forward) * viewRotation).Normalized();
    }
}
