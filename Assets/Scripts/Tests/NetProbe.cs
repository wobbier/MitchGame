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
    // How many clients the server has (RunNetSmoke --observer waits for the second before dashing).
    [Replicated] public int Peers;

    [ServerRpc] partial void Ping(int value);
    [ClientRpc(NetTarget.Owner)] partial void Pong(int value);

    // ME-291: the dash's predicted event (an FX in a real game) must present exactly once per peer.
    private const int DashFx = 1;
    private int dashFxShown;

    private int expectedPeers = -1;
    private int pressedAt = -1;
    private int observedFrames;
    private bool observerReported;

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
            Net.PredictedEvent(this, DashFx, Dashes);
            Shoot();
        }

        character ??= GetComponent<CharacterController>();
        character?.SetMoveInput(DashCooldown > 1.75f ? new Vector3(0f, 0f, 1f) : Vector3.Zero);
    }

    // NET-15: the dash also fires a shot at "NetProbe Target", 3 m off to the side, along the aim
    // the owner sends with its commands (Net.SetAim). The server judges it at the view the
    // owner's command was sent from; the owner predicts it (once, not when resimulating), as a
    // game would for impact FX. Both log the command's yaw, so they can be compared.
    private void Shoot()
    {
        if (Net.IsResimulating)
        {
            return;
        }
        var target = World.Find("NetProbe Target (off camera)");
        var command = Net.Command(Entity);
        var origin = GetComponent<Transform>().WorldPosition + new Vector3(0f, 0.5f, 0f);
        var direction = command.HasAim ? command.AimDirection : new Vector3(0f, 0f, 1f);
        var hit = Net.LagCompensatedRaycast(Entity, origin, direction, 50f);
        bool onTarget = hit.Hit && hit.Entity == target;
        string aim = command.HasAim ? $"aim yaw {command.Yaw:0.000}" : "no aim";
        if (Net.IsServer)
        {
            Debug.Log(onTarget && hit.Rewound && !hit.Rejected ? $"NetProbe: lag-compensated hit ({aim}, view tick {command.ViewTick:0.0}, server tick {Net.Tick})"
                : $"NetProbe: lag-compensated shot FAILED ({hit}, {aim}, view tick {command.ViewTick})");
        }
        else if (Net.IsClient)
        {
            Debug.Log(onTarget && !hit.Rewound ? $"NetProbe: predicted hit ({aim}, rtt {Net.RoundTripMs:0} ms, predict impacts {Net.PredictImpacts})"
                : $"NetProbe: predicted shot FAILED ({hit}, {aim})");
        }
    }

    // The owner's view looks at the target (a mouse-look game sets it from its camera).
    private void AimAtTarget()
    {
        var target = World.Find("NetProbe Target (off camera)");
        var to = target.GetComponent<Transform>().WorldPosition - GetComponent<Transform>().WorldPosition;
        Net.SetAim(MathF.Atan2(to.x, to.z) * (180f / MathF.PI), 0f);
    }

    public override void OnNetEvent(int eventId, int value)
    {
        if (eventId == DashFx)
        {
            ++dashFxShown;
            if (Net.IsServer)
            {
                Debug.Log($"NetProbe: server dash fx #{value}");
            }
        }
    }

    // Presentation: ownership on the server, the scripted test on the owning client.
    public override void OnUpdate(float deltaTime)
    {
        if (Net.IsServer)
        {
            Span<int> clients = stackalloc int[16];
            int count = Net.GetClients(clients);
            Peers = count;
            if (Net.GetOwner(Entity) == 0 && count > 0)
            {
                Net.SetOwner(Entity, clients[0]);
                Debug.Log($"NetProbe: owner -> client #{clients[0]}");
            }
            return;
        }
        if (Net.IsClient && !Net.IsPredicted(Entity))
        {
            // A client that doesn't own the pawn (RunNetSmoke --observer): the dash's event
            // reaches it once, from the server.
            if (++observedFrames == 400 && !observerReported)
            {
                observerReported = true;
                Debug.Log(dashFxShown == 1 ? "NetProbe: observer dash fx once" : $"NetProbe: observer dash fx FAILED (shown {dashFxShown} times)");
            }
            return;
        }
        if (!Net.IsClient)
        {
            return;
        }

        ++predictedFrames;
        AimAtTarget();
        if (expectedPeers < 0)
        {
            // RunNetSmoke --observer sets Game.NetProbePeers = 2 for this client.
            expectedPeers = Settings.GetInt("NetProbePeers", 1);
        }
        if (pressedAt < 0 && predictedFrames >= 60 && Peers >= expectedPeers)
        {
            pressedAt = predictedFrames;
            Net.Press("Dash", true);
        }
        else if (pressedAt >= 0 && predictedFrames == pressedAt + 6)
        {
            Net.Press("Dash", false);
        }
        else if (pressedAt >= 0 && predictedFrames == pressedAt + 30)
        {
            Ping(42);
        }

        if (Pings >= 1 && !replicatedLogged)
        {
            replicatedLogged = true;
            Debug.Log("NetProbe: Replicated ok");
        }
        if (pressedAt >= 0 && predictedFrames >= pressedAt + 240 && !reported)
        {
            reported = true;
            if (Dashes == 1)
            {
                Debug.Log($"NetProbe: dash: {Net.Corrections} corrections");
                Debug.Log(dashFxShown == 1 ? "NetProbe: dash fx once" : $"NetProbe: dash fx FAILED (shown {dashFxShown} times)");
            }
            else
            {
                Debug.Log($"NetProbe: dash FAILED (Dashes={Dashes}, corrections={Net.Corrections})");
            }
        }
    }
}
