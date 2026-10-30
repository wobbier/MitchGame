using System.Collections.Generic;
using ScriptCore;

// A linked doorway. Camera, eye position, body position and velocity all use the same rigid
// transform through the pair. A mounted doorway registers a narrow opening in its host collider,
// so physics can reach the actual plane instead of teleporting early at capsule contact.
[ExecutionOrder(100)]
public class Portal : Script
{
    public string LinkedPortal = "Orange Portal";
    public string Surface = "";
    public string Traveller = "Player";
    public string ViewCamera = "Player Camera";
    public float Width = 1.6f;
    public float Height = 2.4f;
    public bool SurfaceMounted = false;
    public bool RequirePlacement = false;
    public bool IsPlaced = true;
    [HideInInspector] public EntityRef SurfaceHost;

    public static readonly Dictionary<string, Portal> Instances = new Dictionary<string, Portal>();
    private static readonly Dictionary<Entity, Vector3> previousEyes = new Dictionary<Entity, Vector3>();
    private static Dictionary<Entity, Vector3> previousBodies = new Dictionary<Entity, Vector3>();
    private static readonly Dictionary<Entity, Entity> images = new Dictionary<Entity, Entity>();
    private Transform exit, viewCamera, traveller;
    private Camera portalCamera;
    private Entity surfaceEntity, unlinkedPreview;
    private bool LinkAvailable => !RequirePlacement || (IsPlaced
        && Instances.TryGetValue(LinkedPortal, out Portal other) && (!other.RequirePlacement || other.IsPlaced));
    private bool Ready => exit != null && exit.Exists && viewCamera != null && viewCamera.Exists
        && portalCamera != null && portalCamera.Exists && Entity && Entity.Active && LinkAvailable;

    public override void OnStart()
    {
        Instances[Entity.Name] = this;
        Entity linked = World.Find(LinkedPortal);
        Entity surface = World.Find(string.IsNullOrEmpty(Surface) ? $"{Entity.Name} Surface" : Surface);
        Entity view = World.Find(ViewCamera);
        Entity body = World.Find(Traveller);
        if (!linked || !surface || !view)
        {
            Debug.Warning($"Portal '{Entity.Name}': missing linked portal, surface or view camera");
            return;
        }
        surfaceEntity = surface;
        if (RequirePlacement)
        {
            unlinkedPreview = World.Find($"{Entity.Name} Unlinked");
            if (!unlinkedPreview)
                unlinkedPreview = World.Instantiate("Assets/Prefabs/Portals/UnlinkedPortal.prefab", Entity);
            if (unlinkedPreview)
            {
                unlinkedPreview.Name = $"{Entity.Name} Unlinked";
                Vector3 color = Entity.Name.StartsWith("Orange") ? new Vector3(1f, 0.2f, 0.02f) : new Vector3(0.02f, 0.4f, 1f);
                unlinkedPreview.GetComponent<Mesh>()?.SetMaterial("EmissiveColor", color);
            }
        }
        exit = linked.Transform;
        viewCamera = view.Transform;
        traveller = body ? body.Transform : null;
        Entity existing = World.Find($"{Entity.Name} Camera");
        portalCamera = existing ? existing.GetComponent<Camera>() : World.CreateEntity($"{Entity.Name} Camera").AddComponent<Camera>();
        surface.GetComponent<Mesh>()?.ShowCameraView(portalCamera);
        previousEyes[view] = viewCamera.WorldPosition;
        foreach (Portal portal in Instances.Values) portal.RefreshLink();
    }

    public override void OnReload() { OnStart(); }

    public override void OnDestroy()
    {
        ClearTravellerImages();
        Physics.ClearPortalPassage(Entity);
        Instances.Remove(Entity.Name);
        foreach (Portal portal in Instances.Values) portal.RefreshLink();
        if (portalCamera != null && portalCamera.Exists) portalCamera.Entity.Destroy();
        if (Instances.Count == 0)
        {
            previousEyes.Clear();
            previousBodies.Clear();
        }
    }

    // One coordinator handles all transfers, then updates every portal camera from the final
    // player pose. Neither camera can render a stale pose because of entity update order.
    public override void OnLateUpdate(float deltaTime)
    {
        if (!Ready) { UpdateTravellerImages(); return; }
        foreach (Portal other in Instances.Values)
            if (other.Ready && other.Entity.Index < Entity.Index) return;
        var portals = new List<Portal>(Instances.Values);
        var moved = new HashSet<Entity>();
        foreach (Portal portal in portals)
        {
            if (!portal.Ready || portal.traveller == null || !portal.traveller.Exists
                || moved.Contains(portal.traveller.Entity)) continue;
            Entity camera = portal.viewCamera.Entity;
            Vector3 eye = portal.viewCamera.WorldPosition;
            if (previousEyes.TryGetValue(camera, out Vector3 last) && portal.Crossed(last, eye))
            {
                portal.TeleportPlayer();
                moved.Add(portal.traveller.Entity);
            }
        }
        foreach (Portal portal in portals)
            if (portal.Ready) previousEyes[portal.viewCamera.Entity] = portal.viewCamera.WorldPosition;

        // Track actual segments, including fast bodies that cross the whole opening in one frame.
        var bodies = new Dictionary<Entity, Vector3>();
        foreach (Entity body in Query.WithComponent("Rigidbody"))
        {
            if (!body || !body.Active || ChamberController.IsHolding(body)) continue;
            Transform pose = body.Transform;
            Vector3 position = pose.WorldPosition;
            Rigidbody rigidbody = body.GetComponent<Rigidbody>();
            Vector3 last = previousBodies.TryGetValue(body, out Vector3 stored)
                ? stored : position - rigidbody.Velocity * deltaTime;
            foreach (Portal portal in portals)
            {
                if (!portal.Ready || !portal.Crossed(last, position)) continue;
                Vector3 velocity = rigidbody.Velocity;
                rigidbody.Teleport(portal.ThroughPoint(position), portal.ThroughDirection(pose.Forward), portal.ThroughDirection(pose.Up));
                rigidbody.Velocity = portal.ThroughDirection(velocity);
                break;
            }
            bodies[body] = pose.WorldPosition;
        }
        previousBodies = bodies;
        foreach (Portal portal in portals)
        {
            if (!portal.Ready) continue;
            Transform camera = portal.portalCamera.transform;
            camera.WorldPosition = portal.ThroughPoint(portal.viewCamera.WorldPosition);
            camera.LookDirection(portal.ThroughDirection(portal.viewCamera.Forward), portal.ThroughDirection(portal.viewCamera.Up));
            portal.portalCamera.SetClipPlane(portal.exit.WorldPosition + portal.exit.Forward * 0.005f, portal.exit.Forward);
        }
        UpdateTravellerImages();
    }

    // One visual per mesh (including cube decorations), sharing its native geometry/material.
    // No scripts or colliders are cloned. Reconcile every frame, including deleted/unlinked portals.
    public static void UpdateTravellerImages()
    {
        var visible = new HashSet<Entity>();
        foreach (Entity body in Query.WithComponent("Rigidbody"))
        {
            if (!body || !body.Active) continue;
            Vector3 center = body.Transform.WorldPosition;
            Vector3 scale = body.Transform.Scale;
            Vector3 size = body.GetField("BoxCollider", "Size", new Vector3(2, 2, 2));
            float radius = body.HasComponent("BoxCollider")
                ? new Vector3(scale.x * size.x, scale.y * size.y, scale.z * size.z).Length() * 0.5f
                : body.GetField("SphereCollider", "Radius", 1f) * Mathf.Max(Mathf.Abs(scale.x), Mathf.Max(Mathf.Abs(scale.y), Mathf.Abs(scale.z)));
            Portal closest = null;
            float nearest = float.MaxValue;
            foreach (Portal portal in Instances.Values)
            {
                if (!portal.Ready) continue;
                float side = portal.Side(center);
                Vector3 offset = center - portal.transform.WorldPosition;
                if (side < -0.05f || side > radius || side >= nearest
                    || Mathf.Abs(Vector3.Dot(offset, portal.transform.Right)) > portal.Width * 0.5f
                    || Mathf.Abs(Vector3.Dot(offset, portal.transform.Up)) > portal.Height * 0.5f) continue;
                closest = portal;
                nearest = side;
            }
            if (closest != null) SliceHierarchy(body, closest, visible);
        }
        var stale = new List<Entity>();
        foreach (var pair in images)
        {
            if (visible.Contains(pair.Key)) continue;
            if (pair.Key) pair.Key.GetComponent<Mesh>()?.SetPortalSlice();
            if (pair.Value) pair.Value.Destroy();
            stale.Add(pair.Key);
        }
        foreach (Entity source in stale) images.Remove(source);
    }

    private static void SliceHierarchy(Entity source, Portal portal, HashSet<Entity> visible)
    {
        if (!source || !source.Active) return;
        Mesh mesh = source.GetComponent<Mesh>();
        if (mesh != null)
        {
            if (!images.TryGetValue(source, out Entity image) || !image)
            {
                image = World.CreateEntity("Portal Image / " + source.Name);
                image.AddComponent<Mesh>();
                images[source] = image;
            }
            mesh.SetPortalSlice(image, portal.Entity, portal.exit.Entity);
            visible.Add(source);
        }
        foreach (Entity child in source.Children) SliceHierarchy(child, portal, visible);
    }

    private static void ClearTravellerImages()
    {
        foreach (var pair in images)
        {
            if (pair.Key) pair.Key.GetComponent<Mesh>()?.SetPortalSlice();
            if (pair.Value) pair.Value.Destroy();
        }
        images.Clear();
    }

    // Explicit respawns are not a swept movement through the chamber.
    public static void ResetTravellerHistory(Entity body)
    {
        foreach (Portal portal in Instances.Values)
            if (portal.traveller != null && portal.traveller.Entity == body && portal.viewCamera != null)
                previousEyes[portal.viewCamera.Entity] = portal.viewCamera.WorldPosition;
        previousBodies.Clear();
    }

    private void TeleportPlayer()
    {
        Vector3 eye = viewCamera.WorldPosition;
        Vector3 forward = viewCamera.Forward;
        Vector3 up = viewCamera.Up;
        Vector3 mappedEye = ThroughPoint(eye);
        Vector3 mappedForward = ThroughDirection(forward);
        Vector3 mappedUp = ThroughDirection(up);
        Vector3 bodyForward = ThroughDirection(traveller.Forward);
        Vector3 heading = new Vector3(bodyForward.x, 0f, bodyForward.z);
        if (heading.LengthSquared() < 0.001f) heading = new Vector3(mappedUp.x, 0f, mappedUp.z);
        if (heading.LengthSquared() < 0.001f) heading = new Vector3(mappedForward.x, 0f, mappedForward.z);
        if (heading.LengthSquared() < 0.001f) heading = traveller.Forward;
        CharacterController character = traveller.GetComponent<CharacterController>();
        Vector3 velocity = character != null ? character.Velocity : Vector3.Zero;
        if (character != null)
        {
            character.Teleport(ThroughPoint(traveller.WorldPosition), heading.Normalized());
            character.Velocity = ThroughDirection(velocity);
        }
        else
        {
            traveller.WorldPosition = ThroughPoint(traveller.WorldPosition);
            traveller.LookDirection(heading.Normalized(), Vector3.Up);
        }
        if (FirstPersonController.TryGet(traveller.Entity, out FirstPersonController controller))
            controller.ApplyPortalView(mappedEye, mappedForward, mappedUp);
        else
        {
            viewCamera.WorldPosition = mappedEye;
            viewCamera.LookDirection(mappedForward, mappedUp);
        }
        EventBus.Publish(new PortalTraversed(traveller.Entity, Entity, exit.Entity, eye, forward, up, velocity));
    }

    private bool Crossed(Vector3 previous, Vector3 current)
    {
        float before = Side(previous), after = Side(current);
        if (before < 0f || after >= 0f) return false;
        float fraction = before / (before - after);
        Vector3 intersection = previous + (current - previous) * fraction;
        Vector3 offset = intersection - transform.WorldPosition;
        return Mathf.Abs(Vector3.Dot(offset, transform.Right)) <= Width * 0.5f
            && Mathf.Abs(Vector3.Dot(offset, transform.Up)) <= Height * 0.5f;
    }

    private void RefreshLink()
    {
        bool available = LinkAvailable;
        if (surfaceEntity) surfaceEntity.Active = !RequirePlacement || (IsPlaced && available);
        if (unlinkedPreview) unlinkedPreview.Active = IsPlaced && !available;
        RegisterPassage();
    }

    private void RegisterPassage()
    {
        Entity host = SurfaceHost.Resolve();
        if (SurfaceMounted && host && LinkAvailable)
            Physics.SetPortalPassage(Entity, host, transform.WorldPosition, transform.Right, transform.Up,
                new Vector2(Width * 0.5f, Height * 0.5f));
        else Physics.ClearPortalPassage(Entity);
    }

    public void Place(Vector3 position, Vector3 normal, Vector3 up, Entity host = default)
    {
        transform.WorldPosition = position;
        transform.LookDirection(normal, up);
        SurfaceMounted = true;
        IsPlaced = true;
        SurfaceHost = new EntityRef { Guid = host ? host.Guid : "" };
        foreach (Entity child in Entity.Children)
        {
            if (child.Name.EndsWith("Post L") || child.Name.EndsWith("Post R")
                || child.Name.EndsWith("Lintel") || child.Name.EndsWith("Back")) child.Active = false;
            if (child.Name.EndsWith(" Surface"))
            {
                // Keep a two-sided volume behind the face. Its inside faces still show the
                // portal when the main camera's near plane has clipped the front face away.
                child.Transform.Position = new Vector3(0, 0, -0.5f);
                child.Transform.Scale = new Vector3(Width * 0.5f, Height * 0.5f, 0.5f);
            }
        }
        if (viewCamera != null && viewCamera.Exists) previousEyes[viewCamera.Entity] = viewCamera.WorldPosition;
        previousBodies.Clear();
        foreach (Portal portal in Instances.Values) portal.RefreshLink();
        EventBus.Publish(new PortalPlaced(Entity));
    }

    public static Portal FindRayPassage(Vector3 origin, Vector3 direction, float distance, out float crossing)
    {
        Portal found = null;
        crossing = distance;
        foreach (Portal portal in Instances.Values)
        {
            if (!portal.Ready) continue;
            float approach = Vector3.Dot(direction, portal.transform.Forward);
            if (approach >= -0.0001f || portal.Side(origin) < 0f) continue;
            float t = -portal.Side(origin) / approach;
            if (t > crossing || !portal.Crossed(origin, origin + direction * (t + 0.001f))) continue;
            crossing = t;
            found = portal;
        }
        return found;
    }

    private float Side(Vector3 point) => Vector3.Dot(point - transform.WorldPosition, transform.Forward);

    public Vector3 ThroughPoint(Vector3 point) => exit.WorldPosition + ThroughDirection(point - transform.WorldPosition);

    public Vector3 ThroughDirection(Vector3 direction)
    {
        return exit.Right * -Vector3.Dot(direction, transform.Right)
            + exit.Up * Vector3.Dot(direction, transform.Up)
            + exit.Forward * -Vector3.Dot(direction, transform.Forward);
    }
}

public readonly record struct PortalPlaced(Entity Portal);
public readonly record struct PortalTraversed(Entity Traveller, Entity Entrance, Entity Exit,
    Vector3 IncomingEye, Vector3 IncomingForward, Vector3 IncomingUp, Vector3 IncomingVelocity);
