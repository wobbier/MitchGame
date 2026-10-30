using System.Collections.Generic;
using System.Globalization;
using ScriptCore;

// SequenceEventsTest (GAME-4): the gate player and the door both log the sequence events they
// receive; the player also counts what reaches it through Sequence.OnEvent (the EventBus).
public class SequenceEventProbe : Script, ISequenceReceiver
{
    private static readonly List<string> Heard = new();
    private int _busEvents;

    public override void OnStart()
    {
        if (Entity.TryGetComponent(out Sequence sequence))
        {
            Heard.Clear();
            sequence.OnEvent(_ => _busEvents++);
        }
    }

    public void OnSequenceEvent(SequenceEvent e)
    {
        Heard.Add(e.Kind != SequenceEventKind.Marker ? e.Kind.ToString()
            : e.Payload.Length > 0 ? $"{e.Name}@{Entity.Name}({e.Payload},{e.Number.ToString("0.0", CultureInfo.InvariantCulture)})" : $"{e.Name}@{Entity.Name}");
        // The receiver hears Finished before the bus does, so the bus has the four before it.
        if (e.Kind == SequenceEventKind.Finished)
        {
            Debug.Log($"SequenceEventProbe: {string.Join(" ", Heard)} bus={_busEvents}");
        }
    }
}
