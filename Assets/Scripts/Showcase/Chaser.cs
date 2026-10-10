using ScriptCore;

// A NavMeshAgent that keeps re-pathing to its target (the player by default).
public class Chaser : Script
{
    public string Target = "Player";
    public float RepathInterval = 0.3f;

    private NavMeshAgent agent;
    private Entity target;
    private float untilRepath;

    public override void OnStart()
    {
        agent = GetComponent<NavMeshAgent>();
        target = World.Find(Target);
        untilRepath = 0f;
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnUpdate(float deltaTime)
    {
        if (agent == null || !target)
        {
            return;
        }
        untilRepath -= deltaTime;
        if (untilRepath <= 0f)
        {
            untilRepath = RepathInterval;
            agent.SetDestination(target.Transform.WorldPosition);
        }
    }
}
