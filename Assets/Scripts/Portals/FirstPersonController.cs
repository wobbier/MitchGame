using ScriptCore;

// First-person walking for the portal demo. Goes on the body (with a CharacterController); the
// camera is a child entity at eye height, named in CameraName. The mouse (or right stick) turns the
// body left and right and tilts the camera up and down; Move walks, Sprint runs, Jump jumps.
// Pause (Escape) frees the cursor, clicking captures it again.
//
// Turning is applied to the body's current facing rather than a stored angle, so anything else that
// turns the body (like a Portal sending it through) just works.
public class FirstPersonController : Script
{
    public string CameraName = "Player Camera";
    public float Sensitivity = 1.0f;
    public bool InvertY = false;
    public float WalkSpeed = 5.0f;
    public float SprintSpeed = 9.0f;

    private CharacterController character;
    private Transform head;
    private float pitch;

    public override void OnStart()
    {
        character = GetComponent<CharacterController>();
        Entity camera = World.Find(CameraName);
        head = camera ? camera.Transform : null;
        pitch = head != null ? head.Rotation.x : 0f;
        Input.MouseCaptured = true;
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnDestroy()
    {
        Input.MouseCaptured = false;
    }

    public override void OnUpdate(float deltaTime)
    {
        if (character == null)
        {
            return;
        }

        if (Input.WasActionPressed("Pause"))
        {
            Input.MouseCaptured = false;
        }
        else if (!Input.MouseCaptured && Input.WasActionPressed("Fire"))
        {
            Input.MouseCaptured = true;
        }

        if (Input.MouseCaptured)
        {
            // Look is +Y up; positive pitch looks down.
            Vector2 look = Input.GetActionVector2("Look");
            transform.Rotate(new Vector3(0f, look.x * Sensitivity, 0f));
            pitch = Mathf.Clamp(pitch + (InvertY ? look.y : -look.y) * Sensitivity, -85f, 85f);
            if (head != null)
            {
                head.Rotation = new Vector3(pitch, 0f, 0f);
            }
        }

        Vector2 move = Input.GetActionVector2("Move");
        Vector3 forward = new Vector3(transform.Forward.x, 0f, transform.Forward.z).Normalized();
        Vector3 right = new Vector3(transform.Right.x, 0f, transform.Right.z).Normalized();
        Vector3 direction = right * move.x + forward * move.y;
        if (direction.LengthSquared() > 1f)
        {
            direction = direction.Normalized();
        }

        character.MaxSpeed = Input.IsActionPressed("Sprint") ? SprintSpeed : WalkSpeed;
        character.SetMoveInput(direction);
        if (Input.WasActionPressed("Jump") && character.IsGrounded)
        {
            character.Jump();
        }
    }
}
