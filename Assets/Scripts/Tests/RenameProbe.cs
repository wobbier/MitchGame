using ScriptCore;

// ScriptTest.lvl saves this script under its old class name and its field under its old key;
// [FormerName] keeps both loading (saving the scene writes the new names).
[FormerName("RenameProbeOld")]
public class RenameProbe : Script
{
    [FormerName("oldValue")]
    public int Value = 0;

    public override void OnStart()
    {
        Debug.Log($"RenameProbe: started with Value {Value}");
    }
}
