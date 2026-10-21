using System.Collections.Generic;
using ScriptCore;

// One end of a portal pair. Put it on an empty entity standing in the doorway, facing out of the
// portal (its forward axis points at the side you walk in from), and name the other end in
// LinkedPortal. Each end needs:
//   - a surface: an entity with a Mesh (a box filling the doorway and reaching back behind it,
//     so walking through never clips its front face) named in Surface, "<portal name> Surface" when
//     left empty. Its material becomes a window onto the view through the portal.
//   - nothing else: the portal makes its own camera at runtime.
//
// What you see in portal A is what you would see stepping out of portal B: A's camera mirrors the
// main camera into B's frame every frame and hides everything behind B. Whatever crosses A's
// doorway comes out of B, turned to match, with its velocity turned too: the Traveller (the entity
// with the CharacterController, judged by ViewCamera's position) and any Rigidbody.
public class Portal : Script
{
    public string LinkedPortal = "Orange Portal";
    public string Surface = "";
    public string Traveller = "Player";
    // The camera you look through: its position decides when you have crossed.
    public string ViewCamera = "Player Camera";
    // The doorway's size in metres, centred on this entity.
    public float Width = 1.6f;
    public float Height = 2.4f;

    private Transform exit;
    private Camera portalCamera;
    private Transform viewCamera;
    private Transform traveller;
    private float lastSide;
    // Each nearby rigidbody's side of the doorway last frame.
    private Dictionary<Entity, float> bodySides = new Dictionary<Entity, float>();

    public override void OnStart()
    {
        Entity linked = World.Find(LinkedPortal);
        Entity surface = World.Find(string.IsNullOrEmpty(Surface) ? $"{Entity.Name} Surface" : Surface);
        Entity view = World.Find(ViewCamera);
        Entity body = World.Find(Traveller);
        if (!linked || !surface || !view)
        {
            Debug.Warning($"Portal '{Entity.Name}': can't find LinkedPortal '{LinkedPortal}', Surface '{Surface}' or ViewCamera '{ViewCamera}'");
            return;
        }
        exit = linked.Transform;
        viewCamera = view.Transform;
        traveller = body ? body.Transform : null;

        if (portalCamera == null || !portalCamera.Exists)
        {
            portalCamera = World.CreateEntity($"{Entity.Name} Camera").AddComponent<Camera>();
        }
        surface.GetComponent<Mesh>()?.ShowCameraView(portalCamera);
        lastSide = Side(viewCamera.WorldPosition);
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnDestroy()
    {
        if (portalCamera != null && portalCamera.Exists)
        {
            portalCamera.Entity.Destroy();
        }
    }

    // Late, so the player has moved and turned this frame before we teleport and aim the camera.
    public override void OnLateUpdate(float deltaTime)
    {
        if (exit == null || !viewCamera.Exists)
        {
            return;
        }

        // Crossed from the front of the doorway to behind it, inside its frame: send it through.
        Vector3 eye = viewCamera.WorldPosition;
        float side = Side(eye);
        if (lastSide >= 0f && side < 0f && InsideDoorway(eye) && traveller != null && traveller.Exists)
        {
            Teleport(traveller);
            eye = viewCamera.WorldPosition;
            side = Side(eye);
        }
        lastSide = side;
        SendBodiesThrough();

        // Stand where the main camera would be if this portal were the other one.
        Transform cameraTransform = portalCamera.transform;
        cameraTransform.WorldPosition = ThroughPoint(eye);
        cameraTransform.LookDirection(ThroughDirection(viewCamera.Forward), ThroughDirection(viewCamera.Up));
        // Everything between that camera and the exit doorway (the exit's wall, its own surface)
        // would block the view, so cut it away just in front of the exit.
        portalCamera.SetClipPlane(exit.WorldPosition + exit.Forward * 0.005f, exit.Forward);
    }

    private void Teleport(Transform body)
    {
        Vector3 position = ThroughPoint(body.WorldPosition);
        Vector3 forward = ThroughDirection(body.Forward);
        CharacterController character = body.GetComponent<CharacterController>();
        if (character != null)
        {
            // Through physics: a plain Transform move is undone by interpolation between steps.
            Vector3 velocity = ThroughDirection(character.Velocity);
            character.Teleport(position, forward);
            character.Velocity = velocity;
            return;
        }
        body.WorldPosition = position;
        body.LookDirection(forward, ThroughDirection(body.Up));
    }

    // Rigidbodies (thrown balls, crates) go through too: whatever crossed the doorway since last frame.
    private void SendBodiesThrough()
    {
        float reach = Mathf.Sqrt(Width * Width + Height * Height) * 0.5f + 2f;
        var sides = new Dictionary<Entity, float>();
        foreach (Entity entity in Physics.OverlapSphere(transform.WorldPosition, reach, 128))
        {
            if (sides.ContainsKey(entity) || !entity.TryGetComponent(out Rigidbody rigidbody))
            {
                continue;
            }
            Transform body = entity.Transform;
            Vector3 position = body.WorldPosition;
            float side = Side(position);
            if (bodySides.TryGetValue(entity, out float last) && last >= 0f && side < 0f && InsideDoorway(position))
            {
                Vector3 velocity = ThroughDirection(rigidbody.Velocity);
                rigidbody.Teleport(ThroughPoint(position), ThroughDirection(body.Forward), ThroughDirection(body.Up));
                rigidbody.Velocity = velocity;
                continue;
            }
            sides[entity] = side;
        }
        bodySides = sides;
    }

    // > 0 in front of the doorway (the side its forward points to), < 0 behind it.
    private float Side(Vector3 point) => Vector3.Dot(point - transform.WorldPosition, transform.Forward);

    private bool InsideDoorway(Vector3 point)
    {
        Vector3 offset = point - transform.WorldPosition;
        return Mathf.Abs(Vector3.Dot(offset, transform.Right)) <= Width * 0.5f
            && Mathf.Abs(Vector3.Dot(offset, transform.Up)) <= Height * 0.5f;
    }

    // A point in this portal's space, carried to the same place relative to the exit. The exit faces
    // the other way (you walk into one and out of the other), so right and forward flip.
    private Vector3 ThroughPoint(Vector3 point)
    {
        return exit.WorldPosition + ThroughDirection(point - transform.WorldPosition);
    }

    private Vector3 ThroughDirection(Vector3 direction)
    {
        float right = Vector3.Dot(direction, transform.Right);
        float up = Vector3.Dot(direction, transform.Up);
        float forward = Vector3.Dot(direction, transform.Forward);
        return exit.Right * -right + exit.Up * up + exit.Forward * -forward;
    }
}
