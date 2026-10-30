using ScriptCore;

// NetTest.lvl (NET-5): turns a networked entity every fixed step, so the server has a change to
// replicate on every tick and the smoke test can check the snapshot rate against the tick rate.
public class NetSpin : Script
{
    public float DegreesPerTick = 3.0f;

    public override void OnFixedUpdate(float deltaTime)
    {
        transform.Rotate(new Vector3(0, DegreesPerTick, 0));
    }
}
