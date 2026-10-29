using ScriptCore;

// Drives AnimatorTest.lvl / AnimatorFlows.edscript (CS-5 a): reads the Blender's state machine,
// jumps it to another state from C#, and hears the state change.
public class AnimatorProbe : Script
{
    public override void OnStart() => Run();

    private async void Run()
    {
        var animator = World.Find("Blender").GetComponent<Animator>();
        await Async.Frames(3, this);
        Debug.Log($"AnimatorProbe: playing {animator.IsPlaying} in {animator.GetState()}");
        animator.Play("Wave");
        await Async.Frames(3, this);
        Debug.Log($"AnimatorProbe: after Play in {animator.GetState()} at {(animator.GetNormalizedTime() >= 0f ? "a valid time" : "no time")}");
    }
}
