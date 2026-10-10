using ScriptCore;

// Drives NavTest.lvl / NavFlows.edscript: on play the agent walks to the entity named Target and
// logs when it arrives, so the editor script can wait for it.
public class NavProbe : Script
{
    public string Target = "";
    public bool Arrived = false;

    private NavMeshAgent agent;

    public override void OnStart()
    {
        agent = GetComponent<NavMeshAgent>();
        var target = World.Find(Target);
        if (!target)
        {
            Debug.Warning($"NavProbe: no entity named '{Target}'");
            return;
        }
        var destination = target.Transform.WorldPosition;
        if (Navigation.SamplePosition(destination, 3.0f, out var onMesh))
        {
            destination = onMesh;
        }
        agent.SetDestination(destination);
        var path = Navigation.FindPath(transform.WorldPosition, destination);
        Debug.Log($"NavProbe: {Entity.Name} heading to {Target} ({path.Length} corners)");
    }

    public override void OnReload()
    {
        agent = GetComponent<NavMeshAgent>();
    }

    public override void OnUpdate(float deltaTime)
    {
        if (!Arrived && agent != null && agent.HasArrived)
        {
            Arrived = true;
            Debug.Log($"NavProbe: {Entity.Name} arrived");
        }
    }
}
