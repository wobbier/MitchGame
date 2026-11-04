using System;
using System.Collections.Generic;
using ScriptCore;

// A playable multiplayer pawn (issue board #9 / #30): two of these sit in Assets/Scenes/NetArena.lvl.
// The server hands each joining client the first pawn nobody owns (NetClientJoined, with a
// per-frame sweep as a safety net) and takes it back when the client leaves. Every peer simulates
// a pawn from the same command: the owner's networked Move / Jump / Sprint actions and the aim yaw
// it sends with Net.SetAim, so the owner predicts its own pawn and the others see the replicated
// pose. The owning client also drives the scene's camera as a third-person follow camera.
//
//   Engine/Tools/RunNetLocal.py --scene Assets/Scenes/NetArena.lvl --clients 2
//   Tools/TestNetArena.py          (headless smoke: a server and two autopiloted clients)
//
// Offline (the editor's Play, no session) Net.LocalCommand carries the same actions, so the pawn
// with Slot 1 is playable alone.
public partial class NetPawn : Script
{
    public int Slot = 1;                       // hands out pawns in this order
    public float WalkSpeed = 4f;               // m/s (the controller's MaxSpeed)
    public float SprintMultiplier = 1.6f;
    public float LookSensitivity = 0.15f;      // degrees per Look unit
    public float CameraDistance = 4.5f;
    public float CameraHeight = 1.8f;
    public string CameraName = "Main Camera";

    // Replicated so every peer can label the pawns (the owner itself travels in the engine's Owner message).
    [Replicated] public int OwnerClient;
    [Replicated] public int Jumps;

    private static readonly List<NetPawn> Pawns = new();

    private CharacterController character;
    private float yaw;
    private float pitch;
    private float simulatedYaw;
    private bool simulatedYawKnown;
    private Vector3 spawn;
    private int autopilot = -1;
    private float ownedSeconds;
    private bool movedLogged;
    private bool remoteLogged;
    private bool connectedLogged;

    public override void OnStart()
    {
        character = GetComponent<CharacterController>();
        spawn = transform.WorldPosition;
        yaw = transform.Rotation.y;
        Register();
        if (Net.IsServer)
        {
            On<NetClientJoined>(e => AssignPawns());
            On<NetClientLeft>(e => ReleasePawns(e.ClientId));
        }
    }

    public override void OnReload() => Register();

    public override void OnDestroy() => Pawns.Remove(this);

    private void Register()
    {
        if (!Pawns.Contains(this))
        {
            Pawns.Add(this);
            Pawns.Sort((a, b) => a.Slot.CompareTo(b.Slot));
        }
    }

    private bool IsCoordinator => Pawns.Count > 0 && Pawns[0] == this;

    // Server: every connected client gets the first pawn nobody owns.
    private static void AssignPawns()
    {
        Span<int> clients = stackalloc int[16];
        int count = Net.GetClients(clients);
        for (int i = 0; i < count; ++i)
        {
            int client = clients[i];
            bool hasPawn = false;
            foreach (NetPawn pawn in Pawns)
            {
                hasPawn |= Net.GetOwner(pawn.Entity) == client;
            }
            if (hasPawn)
            {
                continue;
            }
            foreach (NetPawn pawn in Pawns)
            {
                if (Net.GetOwner(pawn.Entity) == 0)
                {
                    Net.SetOwner(pawn.Entity, client);
                    pawn.OwnerClient = client;
                    Debug.Log($"NetPawn: pawn {pawn.Slot} -> client #{client}");
                    break;
                }
            }
        }
    }

    private static void ReleasePawns(int client)
    {
        foreach (NetPawn pawn in Pawns)
        {
            if (pawn.OwnerClient == client)
            {
                pawn.OwnerClient = 0;
                pawn.character?.SetMoveInput(Vector3.Zero);
                Debug.Log($"NetPawn: pawn {pawn.Slot} released by client #{client}");
            }
        }
    }

    // Simulation: the server for every pawn, the owner predicting its own, offline from the local command.
    public override void OnFixedUpdate(float deltaTime)
    {
        character ??= GetComponent<CharacterController>();
        if (character == null)
        {
            return;
        }
        NetCommand command = Net.IsActive ? Net.Command(Entity) : Net.LocalCommand;
        if (!command.Valid)
        {
            character.SetMoveInput(Vector3.Zero);
            return;
        }
        if (command.HasAim)
        {
            simulatedYaw = command.Yaw;
            simulatedYawKnown = true;
        }
        else if (!simulatedYawKnown)
        {
            simulatedYaw = transform.Rotation.y;
            simulatedYawKnown = true;
        }
        transform.Rotation = new Vector3(0f, simulatedYaw, 0f);

        Vector2 move = command.Vector2("Move");
        float radians = simulatedYaw * (MathF.PI / 180f);
        var forward = new Vector3(MathF.Sin(radians), 0f, MathF.Cos(radians));
        var right = new Vector3(forward.z, 0f, -forward.x);
        Vector3 direction = forward * move.y + right * move.x;
        float length = direction.Length();
        if (length > 1f)
        {
            direction /= length;
        }
        bool sprinting = command.IsDown("Sprint") && move.y > 0.1f;
        character.MaxSpeed = WalkSpeed * (sprinting ? SprintMultiplier : 1f);
        character.SetMoveInput(direction);
        if (command.WasPressed("Jump"))
        {
            character.Jump();
            if (!Net.IsResimulating)
            {
                Jumps++;
            }
        }
    }

    // Presentation.
    public override void OnUpdate(float deltaTime)
    {
        if (Net.IsServer)
        {
            if (IsCoordinator)
            {
                AssignPawns();
            }
            if (!movedLogged && OwnerClient != 0 && HorizontalDistance(transform.WorldPosition, spawn) > 2f)
            {
                movedLogged = true;
                Debug.Log($"NetPawn: pawn {Slot} moved {HorizontalDistance(transform.WorldPosition, spawn):0.0} m");
            }
            return;
        }

        bool mine = Net.IsActive ? Net.IsOwner(Entity) : Slot == 1;
        if (!mine)
        {
            if (Net.IsClient && !remoteLogged && HorizontalDistance(transform.WorldPosition, spawn) > 2f)
            {
                remoteLogged = true;
                Debug.Log($"NetPawn: remote pawn {Slot} moved {HorizontalDistance(transform.WorldPosition, spawn):0.0} m");
            }
            return;
        }
        if (!connectedLogged)
        {
            connectedLogged = true;
            Debug.Log($"NetPawn: pawn {Slot} is mine (client #{Net.LocalClientId})");
        }

        // Mouse / stick look: the aim rides in every command, so the server and the prediction turn the same way.
        Vector2 look = Input.GetActionVector2("Look");
        yaw += look.x * LookSensitivity;
        pitch = Math.Clamp(pitch - look.y * LookSensitivity, -60f, 70f);
        Net.SetAim(yaw, pitch);

        Autopilot(deltaTime);
    }

    // Camera after the pose is final for this frame.
    public override void OnLateUpdate(float deltaTime)
    {
        bool mine = Net.IsActive ? Net.IsClient && Net.IsOwner(Entity) : Slot == 1;
        if (!mine)
        {
            return;
        }
        Entity camera = World.Find(CameraName);
        if (!camera.IsAlive)
        {
            return;
        }
        float yawRadians = yaw * (MathF.PI / 180f);
        float pitchRadians = pitch * (MathF.PI / 180f);
        var back = new Vector3(-MathF.Sin(yawRadians) * MathF.Cos(pitchRadians), MathF.Sin(pitchRadians), -MathF.Cos(yawRadians) * MathF.Cos(pitchRadians));
        Vector3 focus = transform.WorldPosition + new Vector3(0f, CameraHeight * 0.8f, 0f);
        Transform view = camera.Transform;
        view.Position = focus + back * CameraDistance + new Vector3(0f, CameraHeight * 0.35f, 0f);
        view.LookAt(focus);
    }

    // Game.NetPawnAutoPilot = 1 (user://Settings.json) makes the owning client walk forward for 2.5 s of
    // game time and jump once, for the headless smoke (Tools/TestNetArena.py); it logs how far its pawn got.
    // Game time, not frames: a slow headless run clamps its frame delta to 0.25 s, so frame counts would
    // walk much further than a real 60 Hz run.
    private void Autopilot(float dt)
    {
        if (autopilot < 0)
        {
            autopilot = Settings.GetInt("NetPawnAutoPilot", 0);
        }
        if (autopilot == 0)
        {
            return;
        }
        float before = ownedSeconds;
        ownedSeconds += dt;
        if (before < 0.5f && ownedSeconds >= 0.5f)
        {
            Input.Simulate(KeyCode.W, true);
        }
        else if (before < 1.5f && ownedSeconds >= 1.5f)
        {
            Input.Simulate(KeyCode.Space, true);
        }
        else if (before < 1.7f && ownedSeconds >= 1.7f)
        {
            Input.Simulate(KeyCode.Space, false);
        }
        else if (before < 3.0f && ownedSeconds >= 3.0f)
        {
            Input.Simulate(KeyCode.W, false);
        }
        else if (before < 5.0f && ownedSeconds >= 5.0f)
        {
            float distance = HorizontalDistance(transform.WorldPosition, spawn);
            Debug.Log(distance > 2f && distance < 30f ? $"NetPawn: autopilot: own pawn moved {distance:0.0} m, jumps {Jumps}, corrections {Net.Corrections}"
                : $"NetPawn: autopilot FAILED (moved {distance:0.00} m)");
        }
    }

    private static float HorizontalDistance(Vector3 a, Vector3 b)
    {
        float dx = a.x - b.x, dz = a.z - b.z;
        return MathF.Sqrt(dx * dx + dz * dz);
    }
}
