using ScriptCore;

public readonly record struct ProbePing(int Value);

// Drives EventTest.lvl / EventFlows.edscript (CS-8). The Sender publishes a ping both probes hear,
// destroys the other probe (its subscription goes with it), pings again, then loads an additive
// scene and hears the engine's AdditiveSceneChanged.
public class EventProbe : Script
{
    public bool Sender = false;

    private int frame;

    public override void OnStart()
    {
        On<ProbePing>(OnPing);
        On<AdditiveSceneChanged>(OnAdditive);
    }

    public override void OnUpdate(float deltaTime)
    {
        if (!Sender) return;
        frame++;
        if (frame == 2)
        {
            EventBus.Publish(new ProbePing(42));
        }
        else if (frame == 4)
        {
            World.Find("Doomed").Destroy();
        }
        else if (frame == 8)
        {
            Debug.Log($"EventProbe: {EventBus.SubscriberCount<ProbePing>()} ping subscriber(s) left");
            EventBus.Publish(new ProbePing(7));
            World.LoadSceneAdditive("Assets/Scenes/Tests/EventAdditive.lvl");
        }
    }

    private void OnPing(ProbePing ping) => Debug.Log($"EventProbe {(Sender ? "Sender" : "Doomed")}: ping {ping.Value}");

    private void OnAdditive(AdditiveSceneChanged change) =>
        Debug.Log($"EventProbe {(Sender ? "Sender" : "Doomed")}: additive {change.Path} {(change.Loaded ? "loaded" : "unloaded")}");
}
