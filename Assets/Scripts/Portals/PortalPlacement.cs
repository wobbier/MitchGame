using ScriptCore;

// Shared by the gun and the runtime regression probe. Only stationary, continuous faces qualify.
public static class PortalPlacement
{
    public static bool Shoot(string name, Vector3 origin, Vector3 direction, out Vector3 impact)
    {
        impact = origin + direction.Normalized() * 100f;
        RaycastHit target = default;
        bool found = false;
        foreach (RaycastHit hit in Physics.RaycastAll(origin, direction, 100f))
        {
            if (hit.Entity.Name == "Player" || hit.Entity.Name.StartsWith("Portal Window") || IsPortalPart(hit.Entity)) continue;
            target = hit;
            impact = hit.Point;
            found = true;
            break;
        }
        if (!found || target.Entity.HasComponent<Rigidbody>() || !Portal.Instances.TryGetValue(name, out Portal portal)) return false;
        // Test chamber walls and machinery are not portal conductors; the white inserts are.
        if (ChamberController.Active != null && !target.Entity.Name.StartsWith("Portal Panel")) return false;
        Vector3 normal = target.Normal.Normalized();
        Vector3 up = Mathf.Abs(normal.y) > 0.9f ? new Vector3(0, 0, 1) : Vector3.Up;
        Vector3 right = Vector3.Cross(up, normal).Normalized();
        up = Vector3.Cross(normal, right).Normalized();
        Vector3 center = target.Point;
        // Let a shot near the floor settle into a walkable opening instead of leaving a high sill.
        if (Mathf.Abs(normal.y) < 0.1f && Physics.Raycast(center + normal * 0.15f, -Vector3.Up,
            portal.Height * 0.5f + 0.85f, out RaycastHit floor) && floor.Normal.y > 0.9f)
            center.y = floor.Point.y + portal.Height * 0.5f + 0.10f;
        for (int x = -1; x <= 1; ++x)
        for (int y = -1; y <= 1; ++y)
        {
            Vector3 sample = center + right * (x * (portal.Width * 0.5f + 0.06f))
                + up * (y * (portal.Height * 0.5f + 0.06f));
            if (!Physics.Raycast(sample + normal * 0.12f, -normal, 0.24f, out RaycastHit fit)
                || fit.Entity != target.Entity || Vector3.Dot(fit.Normal, normal) < 0.98f) return false;
        }
        foreach (Portal other in Portal.Instances.Values)
        {
            if (other == portal) continue;
            Vector3 offset = other.transform.WorldPosition - center;
            // Coplanar openings must not intersect, including when their facing is reversed.
            if (Mathf.Abs(Vector3.Dot(other.transform.Forward, normal)) > 0.95f
                && Mathf.Abs(Vector3.Dot(offset, normal)) < 0.2f
                && Mathf.Abs(Vector3.Dot(offset, right)) < portal.Width + 0.15f
                && Mathf.Abs(Vector3.Dot(offset, up)) < portal.Height + 0.15f) return false;
        }
        portal.Place(center + normal * 0.035f, normal, up, target.Entity);
        impact = center;
        return true;
    }

    private static bool IsPortalPart(Entity entity)
    {
        for (Entity e = entity; e; e = e.Transform.Parent)
            if (e.Name == "Blue Portal" || e.Name == "Orange Portal") return true;
        return false;
    }
}
