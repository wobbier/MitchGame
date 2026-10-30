using System;
using ScriptCore;

// NET-6 smoke test: a predicted dash, a replicated counter and a server / owner RPC round trip.
// The server hands the entity to the first client; that client presses Dash (a networked action)
// through Net.Press, predicts the dash locally, pings the server and reports how prediction went.
public partial class NetProbe : Script
{
    [Predicted] public float DashCooldown;
    [Predicted] public int Dashes;
    [Replicated] public int Pings;

    [ServerRpc] partial void Ping(int value);
    [ClientRpc(NetTarget.Owner)] partial void Pong(int value);

    private CharacterController character;
    private int predictedFrames;
    private bool replicatedLogged;
    private bool reported;

    private void OnPing(int value)
    {
        if (Net.IsServer && value == 42)
        {
            Pings++;
            Debug.Log("NetProbe: ServerRpc ok");
            Pong(7);
        }
    }

    private void OnPong(int value)
    {
        if (Net.IsClient && value == 7)
        {
            Debug.Log("NetProbe: ClientRpc ok");
        }
    }

    // Simulation: runs on the server and, predicted (and resimulated), on the owning client.
    public override void OnFixedUpdate(float deltaTime)
    {
        if (!Net.IsActive)
        {
            return;
        }
        var command = Net.Command(Entity);
        if (DashCooldown > 0f)
        {
            DashCooldown = Math.Max(0f, DashCooldown - deltaTime);
        }
        if (command.WasPressed("Dash") && DashCooldown <= 0f)
        {
            DashCooldown = 2f;
            Dashes++;
        }

        character ??= GetComponent<CharacterController>();
        character?.SetMoveInput(DashCooldown > 1.75f ? new Vector3(0f, 0f, 1f) : Vector3.Zero);
    }

    // Presentation: ownership on the server, the scripted test on the owning client.
    public override void OnUpdate(float deltaTime)
    {
        if (Net.IsServer)
        {
            if (Net.GetOwner(Entity) == 0)
            {
                Span<int> clients = stackalloc int[16];
                if (Net.GetClients(clients) > 0)
                {
                    Net.SetOwner(Entity, clients[0]);
                    Debug.Log($"NetProbe: owner -> client #{clients[0]}");
                }
            }
            return;
        }
        if (!Net.IsClient || !Net.IsPredicted(Entity))
        {
            return;
        }

        ++predictedFrames;
        if (predictedFrames == 60)
        {
            Net.Press("Dash", true);
        }
        else if (predictedFrames == 66)
        {
            Net.Press("Dash", false);
        }
        else if (predictedFrames == 90)
        {
            Ping(42);
        }

        if (Pings >= 1 && !replicatedLogged)
        {
            replicatedLogged = true;
            Debug.Log("NetProbe: Replicated ok");
        }
        if (predictedFrames >= 300 && !reported)
        {
            reported = true;
            if (Dashes == 1)
            {
                Debug.Log($"NetProbe: dash: {Net.Corrections} corrections");
            }
            else
            {
                Debug.Log($"NetProbe: dash FAILED (Dashes={Dashes}, corrections={Net.Corrections})");
            }
        }
    }
}
