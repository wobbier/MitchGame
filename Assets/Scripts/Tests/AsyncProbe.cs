using System.Collections;
using System.Threading;
using System.Threading.Tasks;
using ScriptCore;

// Drives AsyncTest.lvl / AsyncFlows.edscript (CS-6) at a fixed 0.02 s frame: an awaited 0.5 s
// lands on frame 25, a 0.4 s tween ends on frame 20 at its target, a coroutine's 0.2 s wait ends
// on frame 11 (counting from the frame after it yielded), and a wall-clock Task.Delay resumes on
// the main thread.
public class AsyncProbe : Script
{
    private long start;
    private int mainThread;
    private float value;

    private long Frames => Async.Frame - start;

    public override void OnStart()
    {
        // OnStart runs before this frame's tick, so the first tick is frame 1.
        start = Async.Frame;
        mainThread = Thread.CurrentThread.ManagedThreadId;
        Delay();
        Tweening();
        WallClock();
        StartCoroutine(Blink());
    }

    private async void Delay()
    {
        await Async.Seconds(0.5f, this);
        Debug.Log($"AsyncProbe: delay landed on frame {Frames}");
        await Async.Frames(3, this);
        Debug.Log($"AsyncProbe: three frames later it is frame {Frames}");
    }

    private async void Tweening()
    {
        await Tween.Float(0f, 10f, 0.4f, v => value = v, Ease.Linear, this).Task;
        Debug.Log($"AsyncProbe: tween ended on frame {Frames} at {value:F2}");
    }

    private async void WallClock()
    {
        await Task.Delay(30);
        Debug.Log($"AsyncProbe: Task.Delay resumed on the main thread: {Thread.CurrentThread.ManagedThreadId == mainThread}");
    }

    private IEnumerator Blink()
    {
        yield return new WaitForSeconds(0.2f);
        Debug.Log($"AsyncProbe: coroutine waited until frame {Frames}");
        yield return null;
        Debug.Log($"AsyncProbe: coroutine resumed on frame {Frames}");
    }
}
