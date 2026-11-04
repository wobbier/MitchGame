using System;
using System.Threading.Tasks;
using ScriptCore;

// Play-mode tests for the first-person character (issue board #8), on CharacterTest.lvl:
// CharacterCore drives the Player's CharacterController from the input actions. Run with
// "game-tests CharacterTests" (CharacterFlows.edscript does).
public static class CharacterTests
{
    private const string Scene = "Assets/Scenes/Tests/CharacterTest.lvl";

    private static Entity Player() => World.Find("Player");

    private static async Task Settle(Entity player)
    {
        var character = player.GetComponent<CharacterController>();
        await GameAssert.Eventually(() => character.IsGrounded && player.Transform.Position.y < 1.0f, 3f, "the player settles on the floor");
    }

    private static async Task<float> PeakHeight(Entity player, float seconds)
    {
        float peak = player.Transform.Position.y;
        float waited = 0f;
        while (waited < seconds)
        {
            waited += Time.DeltaTime;
            await Async.NextFrame();
            peak = MathF.Max(peak, player.Transform.Position.y);
        }
        return peak;
    }

    [GameTest(Scene)]
    public static async Task A_direct_jump_lifts_the_capsule()
    {
        Entity player = Player();
        await Settle(player);
        float rest = player.Transform.Position.y;
        player.GetComponent<CharacterController>().Jump();
        float peak = await PeakHeight(player, 1.5f);
        Debug.Log($"CharacterTests: direct jump rest {rest:0.00} peak {peak:0.00}");
        GameAssert.True(peak > rest + 0.8f, $"the capsule rose from {rest:0.00} to {peak:0.00}");
        await Settle(player);
    }

    [GameTest(Scene)]
    public static async Task Holding_Space_jumps_through_the_core()
    {
        Entity player = Player();
        await Settle(player);
        float rest = player.Transform.Position.y;
        Input.Simulate(KeyCode.Space, true);
        await Async.Frames(3);
        Input.Simulate(KeyCode.Space, false);
        float peak = await PeakHeight(player, 1.5f);
        Debug.Log($"CharacterTests: Space jump rest {rest:0.00} peak {peak:0.00}");
        GameAssert.True(peak > rest + 0.8f, $"the capsule rose from {rest:0.00} to {peak:0.00}");
        await Settle(player);
    }

    [GameTest(Scene)]
    public static async Task Holding_W_walks_forward_at_the_walk_speed()
    {
        Entity player = Player();
        await Settle(player);
        Vector3 start = player.Transform.Position;
        Input.Simulate(KeyCode.W, true);
        await Async.Seconds(1f);
        Input.Simulate(KeyCode.W, false);
        float moved = player.Transform.Position.z - start.z;
        Debug.Log($"CharacterTests: walked {moved:0.00} m in 1 s");
        GameAssert.True(moved > 2.0f && moved < 5.5f, $"walked {moved:0.00} m in a second at 4 m/s (minus the acceleration ramp)");
        GameAssert.Near(start.x, player.Transform.Position.x, 0.3f, "no sideways drift");
    }
}
