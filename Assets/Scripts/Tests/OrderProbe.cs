using ScriptCore;

// ScriptTest.lvl lists OrderLate before OrderEarly; [ExecutionOrder] must still run OrderEarly
// first, in OnStart and every update, and OnLateUpdate must follow every script's OnUpdate.
[ExecutionOrder(-50)]
public class OrderProbeEarly : Script
{
    public static bool Started;
    public static int Updates;

    public override void OnStart()
    {
        Started = true;
    }

    public override void OnUpdate(float deltaTime)
    {
        ++Updates;
    }
}

public class OrderProbeLate : Script
{
    private const int FramesToCheck = 30;
    private int _updates;
    private int _lateUpdates;
    private string _failure = "";
    private bool _reported;

    public override void OnStart()
    {
        if (!OrderProbeEarly.Started)
        {
            _failure = "started before OrderProbeEarly";
        }
    }

    public override void OnUpdate(float deltaTime)
    {
        ++_updates;
        if (_failure.Length == 0 && OrderProbeEarly.Updates != _updates)
        {
            _failure = $"update {_updates} ran before OrderProbeEarly's ({OrderProbeEarly.Updates})";
        }
    }

    public override void OnLateUpdate(float deltaTime)
    {
        ++_lateUpdates;
        if (_failure.Length == 0 && _lateUpdates != _updates)
        {
            _failure = $"late update {_lateUpdates} didn't follow update {_updates}";
        }
        if (!_reported && _lateUpdates >= FramesToCheck)
        {
            _reported = true;
            Debug.Log(_failure.Length == 0
                ? $"OrderProbe: execution order and late update held for {FramesToCheck} frames"
                : $"OrderProbe: FAILED, {_failure}");
        }
    }
}
