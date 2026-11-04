using System.Threading.Tasks;
using ScriptCore;

// ECS play-mode tests (issue board #7): the entity / component / hierarchy contract as scripts see it.
// They complement the engine's C++ suite (Engine/Tests/Source/ECSTests.cpp) by going through the
// script bindings, which is what game code actually uses. Run in Play with the console:
//     game-tests EcsTests
// EcsFlows.edscript does that on EcsTest.lvl and waits for "GameTests: N passed, 0 failed".
public static class EcsTests
{
    private const string Scene = "Assets/Scenes/Tests/EcsTest.lvl";

    [GameTest(Scene)]
    public static async Task Entities_are_created_found_and_destroyed_at_frame_end()
    {
        Entity probe = World.CreateEntity("Ecs Probe");
        GameAssert.True(probe.IsAlive, "a new entity is alive");
        GameAssert.Equal("Ecs Probe", probe.Name, "name");
        GameAssert.Equal(probe, World.Find("Ecs Probe"), "World.Find");
        GameAssert.Equal(1, Query.Named("Ecs Probe").Length, "Query.Named");

        probe.Name = "Ecs Probe Renamed";
        GameAssert.Equal("Ecs Probe Renamed", probe.Name, "rename");
        GameAssert.True(!World.Find("Ecs Probe").IsAlive, "the old name no longer resolves");

        probe.Destroy();
        GameAssert.True(probe.IsAlive, "destruction is deferred to the end of the frame");
        await Async.NextFrame();
        GameAssert.True(!probe.IsAlive, "destroyed after the frame");
        GameAssert.True(!World.Find("Ecs Probe Renamed").IsAlive, "a destroyed entity is not found");

        // A stale handle stays dead even when the slot is reused: entity ids are generational.
        Entity replacement = World.CreateEntity("Ecs Replacement");
        GameAssert.True(!probe.IsAlive, "the stale handle stays dead");
        GameAssert.True(probe != replacement, "a reused slot is a different entity");
        replacement.Destroy();
    }

    [GameTest(Scene)]
    public static async Task Components_add_query_and_round_trip_fields()
    {
        int lightsBefore = Query.WithComponent("Light").Length;
        Entity lamp = World.CreateEntity("Ecs Lamp");
        GameAssert.True(!lamp.HasComponent<Light>(), "no light yet");

        Light light = lamp.AddComponent<Light>();
        GameAssert.True(lamp.HasComponent<Light>(), "HasComponent<T> after AddComponent<T>");
        GameAssert.True(lamp.HasComponent("Light"), "HasComponent by name");
        GameAssert.Equal(lightsBefore + 1, Query.WithComponent("Light").Length, "Query.WithComponent counts it");

        light.Intensity = 3.5f;
        GameAssert.Near(3.5f, lamp.GetComponent<Light>().Intensity, 1e-4f, "wrapper round trip");
        GameAssert.Near(3.5f, lamp.GetField<float>("Light", "Intensity"), 1e-4f, "reflected field path");
        GameAssert.True(lamp.SetField("Light", "Intensity", 1.25f), "SetField by name");
        GameAssert.Near(1.25f, light.Intensity, 1e-4f, "SetField reaches the wrapper");
        GameAssert.True(!lamp.SetField("Light", "NoSuchField", 1f), "a missing field is reported, not invented");

        // A component with no C# wrapper, by name.
        lamp.AddComponent("AudioSource");
        GameAssert.True(lamp.HasComponent("AudioSource"), "AddComponent by name");
        GameAssert.True(lamp.TryGetComponent(out Light again) && again == light, "TryGetComponent and wrapper equality");

        lamp.Destroy();
        await Async.NextFrame();
        GameAssert.Equal(lightsBefore, Query.WithComponent("Light").Length, "destroyed components leave the query");
        GameAssert.True(!light.Exists, "a wrapper of a destroyed entity does not Exist");
    }

    [GameTest(Scene)]
    public static async Task Hierarchy_parents_children_and_world_positions()
    {
        Entity parent = World.CreateEntity("Ecs Parent");
        Entity child = World.CreateEntity("Ecs Child");
        Entity grandchild = World.CreateEntity("Ecs Grandchild");
        parent.Transform.Position = new Vector3(1f, 2f, 3f);
        child.Transform.Parent = parent;
        grandchild.Transform.Parent = child;
        child.Transform.Position = new Vector3(1f, 0f, 0f);
        grandchild.Transform.Position = new Vector3(0f, 1f, 0f);

        GameAssert.Equal(parent, child.Transform.Parent, "Parent reads back");
        GameAssert.Equal(1, parent.Children.Length, "one direct child");
        GameAssert.Equal(child, parent.Children[0], "the child");
        GameAssert.Near(new Vector3(2f, 2f, 3f), child.Transform.WorldPosition, 1e-3f, "child world position");
        GameAssert.Near(new Vector3(2f, 3f, 3f), grandchild.Transform.WorldPosition, 1e-3f, "grandchild world position");

        // Moving the parent moves the whole subtree; the locals stay.
        parent.Transform.Position = new Vector3(-1f, 0f, 0f);
        GameAssert.Near(new Vector3(0f, 1f, 0f), grandchild.Transform.WorldPosition, 1e-3f, "subtree follows the parent");
        GameAssert.Near(new Vector3(1f, 0f, 0f), child.Transform.Position, 1e-5f, "local position unchanged");

        // Reparenting (to the scene root here) keeps the world pose, like the editor does.
        Vector3 before = child.Transform.WorldPosition;
        child.Transform.Parent = Entity.Null;
        GameAssert.True(child.Transform.Parent != parent, "detached from the parent");
        GameAssert.Equal(0, parent.Children.Length, "parent has no children left");
        GameAssert.Near(before, child.Transform.WorldPosition, 1e-3f, "world pose kept across the reparent");
        GameAssert.Near(before, child.Transform.Position, 1e-3f, "so the local position became the world one");

        // Destroying a parent destroys its descendants.
        grandchild.Transform.Parent = child;
        child.Destroy();
        await Async.NextFrame();
        GameAssert.True(!child.IsAlive && !grandchild.IsAlive, "descendants die with the parent");
        GameAssert.True(parent.IsAlive, "unrelated entities survive");
        parent.Destroy();
    }

    [GameTest(Scene)]
    public static async Task Activity_layers_and_guids()
    {
        Entity a = World.CreateEntity("Ecs A");
        Entity b = World.CreateEntity("Ecs B");
        GameAssert.True(a.Active, "entities start active");
        a.Active = false;
        GameAssert.True(!a.Active, "deactivated");
        a.Active = true;
        GameAssert.True(a.Active, "reactivated");

        a.Layer = 5;
        GameAssert.Equal(5, a.Layer, "layer round trip");
        GameAssert.Equal(0, b.Layer, "layers are per entity");

        GameAssert.Equal(16, a.Guid.Length, "GUIDs are 16 hex digits");
        GameAssert.True(a.Guid != b.Guid, "GUIDs are unique");
        GameAssert.Equal(a.Guid, World.Find("Ecs A").Guid, "the GUID identifies the entity");

        a.Destroy();
        b.Destroy();
        await Async.NextFrame();
        GameAssert.True(!a.IsAlive && !b.IsAlive, "cleanup");
    }

    [GameTest(Scene)]
    public static async Task Scene_entities_are_reachable_and_prefab_free_cleanup_is_exact()
    {
        Entity camera = World.Find("Main Camera");
        GameAssert.True(camera.IsAlive, "the scene's camera exists");
        GameAssert.True(camera.HasComponent<Camera>(), "and has a Camera");
        GameAssert.True(camera.HasComponent<Transform>(), "and a Transform");

        int named = Query.Named("Ecs Bulk").Length;
        for (int i = 0; i < 50; ++i)
        {
            World.CreateEntity("Ecs Bulk");
        }
        GameAssert.Equal(named + 50, Query.Named("Ecs Bulk").Length, "fifty entities created");
        foreach (Entity bulk in Query.Named("Ecs Bulk"))
        {
            bulk.Destroy();
        }
        await Async.NextFrame();
        GameAssert.Equal(0, Query.Named("Ecs Bulk").Length, "all fifty destroyed");
    }
}
