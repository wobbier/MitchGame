using ScriptCore;

// ScriptTest.lvl: falls onto the Ground and logs the contact (with the normal, which points from
// this entity towards the other) so ScriptFlows.edscript can wait for it.
public class CollisionProbe : Script
{
    public string LastHit = "";

    public override void OnCollisionEnter(Collision collision)
    {
        LastHit = collision.Other.Name;
        Debug.Log($"CollisionProbe: hit {LastHit} (normal y {collision.Normal.y:0.0})");
    }
}
