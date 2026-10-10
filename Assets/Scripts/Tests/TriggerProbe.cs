using ScriptCore;

// ScriptTest.lvl: a trigger volume the Dropper falls through; logs entries and exits.
public class TriggerProbe : Script
{
    public int Entered = 0;

    public override void OnTriggerEnter(Entity other)
    {
        Entered++;
        Debug.Log($"TriggerProbe: {other.Name} entered");
    }

    public override void OnTriggerExit(Entity other)
    {
        Debug.Log($"TriggerProbe: {other.Name} left");
    }
}
