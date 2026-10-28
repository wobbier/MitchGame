using ScriptCore;

// Wreck the car (VehicleController.Crashes) and the world freezes at the point of impact while a
// hand of blackjack decides whether you live. H (or the button) hits, S stands; the dealer stands
// on 17. Win or push and the windshield holds: you walk it off and the car backs off the wall.
// Bust or lose and time resumes in slow motion as the glass shatters and the driver goes through
// it: a ragdoll flies on at the speed of the crash, then you're WASTED and the car is back at the
// spawn. The camera leaves the cockpit to circle the frozen car and chases the body if it flies.
// The table is Assets/UI/Drive/Blackjack.rml, bound to the "blackjack" view model this script fills.
public class CarCrash : Script
{
    public string CameraName = "Main Camera";
    public string GlassName = "SM_Veh_4x4_Car_Glass_01";
    public string RagdollPrefab = "Assets/Prefabs/Drive/Ragdoll.prefab";
    public string ShardPrefab = "Assets/Prefabs/Drive/GlassShard.prefab";
    // Where the ragdoll's pelvis starts in the car's frame (its head is already in the windshield).
    public Vector3 SeatPosition = new Vector3(-0.36f, 1.3f, -0.1f);
    public int ShardCount = 28;
    // A lost hand throws the body out at the car's impact velocity times LaunchScale (at least
    // MinLaunchSpeed), plus LaunchLift of that speed upward.
    public float LaunchScale = 1.0f;
    public float LaunchLift = 0.3f;
    public float MinLaunchSpeed = 16.0f;
    // Real seconds of ImpactSlowMo between the hit and the freeze, and again as the body bursts out.
    public float ImpactSlowMo = 0.15f;
    public float BurstTime = 0.4f;
    public float DealInterval = 0.4f;
    public float DealerInterval = 0.7f;
    // Real seconds the verdict of the hand stays up before time resumes.
    public float RevealTime = 1.8f;
    // Seconds of flight before WASTED, and of the verdict before the car comes back.
    public float FlightTime = 2.5f;
    public float RespawnDelay = 3.0f;
    public float OrbitDegreesPerSecond = 14.0f;
    public float CameraDistance = 6.5f;
    public float CameraHeight = 2.0f;
    // Automated captures: wreck the car on start at TestCrashSpeed, rig the deck (1 = win, 2 = lose)
    // and let the script play the hand (hit below 17).
    public bool TestCrash = false;
    public float TestCrashSpeed = 25.0f;
    public int TestOutcome = 0;
    public bool TestAutoPlay = false;

    private enum Phase { Idle, Burst, Deal, PlayerTurn, DealerTurn, Reveal, Eject, Flight, Verdict }

    private static readonly string[] Ranks = { "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K" };
    private static readonly string[] Lives = { "Walked it off.", "Seatbelts are for cowards.", "Doctors are calling it a miracle.", "Not even a crack in the glass." };
    private static readonly string[] Deaths = { "The house always wins.", "Should have stood.", "The dealer had it the whole time.", "Organ donor: yes." };

    private UIModel table;
    private VehicleController car;
    private Entity camera;
    private Entity glass;
    private readonly System.Random random = new System.Random();
    private Phase phase = Phase.Idle;
    private int crashesSeen;
    private float timer;
    private float age;
    private float flashLeft;
    private bool hitPressed;
    private bool standPressed;

    private readonly System.Collections.Generic.List<int> deck = new System.Collections.Generic.List<int>();
    private readonly System.Collections.Generic.List<int> player = new System.Collections.Generic.List<int>();
    private readonly System.Collections.Generic.List<int> dealer = new System.Collections.Generic.List<int>();
    private bool holeHidden;
    private bool survived;
    private int dealt;

    private Entity ragdoll;
    private Entity chest;
    private readonly System.Collections.Generic.List<Entity> shards = new System.Collections.Generic.List<Entity>();
    private Vector3 cameraLocalPosition;
    private Vector3 cameraLocalRotation;
    private Entity cameraParent;
    private Vector3 focus;
    private float orbit;
    private float savedSaturation = 1f;
    private bool desaturated;

    public override void OnStart()
    {
        car = VehicleController.Active;
        camera = World.Find(CameraName);
        glass = World.Find(GlassName);
        crashesSeen = car != null ? car.Crashes : 0;
        table = UI.Model("blackjack");
        table.On("hit");
        table.On("stand");
        if (phase == Phase.Idle)
        {
            // Every value the document binds, so it finds them all when the model first appears.
            foreach (string key in new[] { "show", "survived", "wasted", "flash", "act", "hole" })
            {
                table.Set(key, false);
            }
            foreach (string key in new[] { "impact", "result", "epitaph" })
            {
                table.Set(key, "");
            }
            table.Set("outcome", 0);
            player.Clear();
            dealer.Clear();
            SyncHands();
        }
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnDestroy()
    {
        if (phase != Phase.Idle)
        {
            Time.TimeScale = 1f;
            CockpitCamera.Suspended = false;
        }
    }

    public override void OnUpdate(float deltaTime)
    {
        float real = Time.UnscaledDeltaTime;
        age += real;
        car ??= VehicleController.Active;
        if (car == null)
        {
            return;
        }
        if (TestCrash && age > 1.5f && phase == Phase.Idle)
        {
            TestCrash = false;
            Vector3 heading = car.Entity.Transform.Forward;
            car.Wreck(heading * TestCrashSpeed, car.Entity.Transform.WorldPosition + heading * car.BumperLength, -heading);
        }
        if (phase == Phase.Idle && car.Crashes != crashesSeen)
        {
            Impact();
        }
        crashesSeen = car.Crashes;
        if (phase == Phase.Idle)
        {
            return;
        }

        if (flashLeft > 0f && (flashLeft -= real) <= 0f)
        {
            table.Set("flash", false);
        }
        // Clicks queue up in the model; only the player's turn acts on them.
        hitPressed = Input.WasKeyPressed(KeyCode.H) || Input.WasActionPressed("Submit");
        standPressed = Input.WasKeyPressed(KeyCode.S) || Input.WasActionPressed("Back");
        for (string e; (e = table.PollEvent()) != "";)
        {
            hitPressed |= e == "hit";
            standPressed |= e == "stand";
        }
        timer -= real;
        switch (phase)
        {
            case Phase.Burst:
                if (timer <= 0f)
                {
                    Time.TimeScale = 0f;
                    StartHand();
                }
                break;
            case Phase.Deal:
                if (timer <= 0f)
                {
                    DealNext();
                }
                break;
            case Phase.PlayerTurn:
                PlayerTurn();
                break;
            case Phase.DealerTurn:
                if (timer <= 0f)
                {
                    DealerStep();
                }
                break;
            case Phase.Reveal:
                if (timer <= 0f)
                {
                    table.Set("show", false);
                    if (survived)
                    {
                        Time.TimeScale = 1f;
                        ShowVerdict();
                    }
                    else
                    {
                        Eject();
                    }
                }
                break;
            case Phase.Eject:
                if (timer <= 0f)
                {
                    Time.TimeScale = 1f;
                    phase = Phase.Flight;
                    timer = FlightTime;
                }
                break;
            case Phase.Flight:
                if (timer <= 0f)
                {
                    ShowVerdict();
                }
                break;
            case Phase.Verdict:
                if (timer <= 0f)
                {
                    Recover();
                }
                break;
        }
        UpdateCamera(real);
    }

    // The hit: freeze the moment and take the camera; the hand decides what happens next.
    private void Impact()
    {
        Transform carTransform = car.Entity.Transform;
        Vector3 forward = carTransform.Forward;
        Vector3 right = carTransform.Right;
        focus = carTransform.WorldPosition + Vector3.Up * 1.4f + forward * 0.4f;

        if (camera)
        {
            cameraParent = camera.Transform.Parent;
            cameraLocalPosition = camera.Transform.Position;
            cameraLocalRotation = camera.Transform.Rotation;
            camera.Transform.Parent = Entity.Null;
            // Start beside the car, a little ahead of the windshield, looking at the driver.
            Vector3 offset = right * 0.8f + forward * 0.6f;
            orbit = Mathf.Atan2(offset.x, offset.z) * Mathf.Rad2Deg;
        }
        CockpitCamera.Suspended = true;

        int kmh = (int)(car.ImpactVelocity.Length() * 3.6f + 0.5f);
        table.Set("impact", kmh.ToString());
        table.Set("show", false);
        table.Set("survived", false);
        table.Set("wasted", false);
        table.Set("flash", true);
        flashLeft = 0.4f;
        Time.TimeScale = ImpactSlowMo;
        phase = Phase.Burst;
        timer = BurstTime;
    }

    // A lost hand: the glass shatters and the driver goes through it at the speed of the crash,
    // in slow motion for the first BurstTime.
    private void Eject()
    {
        Transform carTransform = car.Entity.Transform;
        Vector3 forward = carTransform.Forward;
        Vector3 right = carTransform.Right;
        Vector3 origin = carTransform.WorldPosition;
        Vector3 impact = car.ImpactVelocity;
        float impactSpeed = impact.Length();
        Vector3 heading = impactSpeed > 1f ? impact / impactSpeed : forward;
        float launchSpeed = Mathf.Max(impactSpeed * LaunchScale, MinLaunchSpeed);
        Vector3 launch = heading * launchSpeed + Vector3.Up * (launchSpeed * LaunchLift);
        // The car is a ghost while the driver leaves it.
        car.Entity.SetField("BoxCollider", "IsTrigger", true);

        if (glass)
        {
            glass.Active = false;
        }
        for (int i = 0; i < ShardCount; ++i)
        {
            Entity shard = World.Instantiate(ShardPrefab);
            if (!shard)
            {
                break;
            }
            Vector3 local = new Vector3(Rand(-0.85f, 0.85f), Rand(1.25f, 1.7f), Rand(0.35f, 0.75f));
            shard.Transform.WorldPosition = origin + right * local.x + Vector3.Up * local.y + forward * local.z;
            shard.Transform.Rotation = new Vector3(Rand(0f, 360f), Rand(0f, 360f), Rand(0f, 360f));
            float size = Rand(0.025f, 0.07f);
            shard.Transform.Scale = new Vector3(size, 0.006f, size * Rand(0.5f, 1.5f));
            Rigidbody body = shard.GetComponent<Rigidbody>();
            if (body != null)
            {
                body.Velocity = launch * Rand(0.6f, 1.05f) + new Vector3(Rand(-3f, 3f), Rand(-1f, 4f), Rand(-3f, 3f));
            }
            shards.Add(shard);
        }

        ragdoll = World.Instantiate(RagdollPrefab);
        if (ragdoll)
        {
            ragdoll.Transform.WorldPosition = origin + right * SeatPosition.x + Vector3.Up * SeatPosition.y + forward * SeatPosition.z;
            ragdoll.Transform.Rotation = new Vector3(0f, Mathf.Atan2(forward.x, forward.z) * Mathf.Rad2Deg, 0f);
            chest = World.Find("Ragdoll Chest");
            string[] parts = { "Pelvis", "Chest", "Head", "UpperArmL", "LowerArmL", "UpperArmR", "LowerArmR", "UpperLegL", "LowerLegL", "UpperLegR", "LowerLegR" };
            foreach (string name in parts)
            {
                Entity part = World.Find("Ragdoll " + name);
                Rigidbody body = part ? part.GetComponent<Rigidbody>() : null;
                if (body == null)
                {
                    continue;
                }
                // The head and arms lead and the legs trail, so the body pitches over as it flies.
                float lead = name == "Head" ? 2.5f : name.Contains("Arm") ? 1.5f : name.Contains("Leg") ? -1.5f : 0f;
                body.Velocity = launch + Vector3.Up * lead + new Vector3(Rand(-0.6f, 0.6f), 0f, Rand(-0.6f, 0.6f));
            }
        }
        table.Set("flash", true);
        flashLeft = 0.25f;
        Time.TimeScale = ImpactSlowMo;
        phase = Phase.Eject;
        timer = BurstTime;
    }

    private void StartHand()
    {
        BuildDeck();
        player.Clear();
        dealer.Clear();
        holeHidden = true;
        dealt = 0;
        table.Set("act", false);
        table.Set("outcome", 0);
        table.Set("result", "");
        SyncHands();
        table.Set("show", true);
        Input.MouseCaptured = false;
        phase = Phase.Deal;
        timer = DealInterval;
    }

    // A shuffled shoe, or a rigged one for captures (the first cards go player, dealer, player, dealer).
    private void BuildDeck()
    {
        deck.Clear();
        for (int i = 0; i < 52; ++i)
        {
            deck.Add(i);
        }
        for (int i = deck.Count - 1; i > 0; --i)
        {
            int j = random.Next(i + 1);
            (deck[i], deck[j]) = (deck[j], deck[i]);
        }
        int[] rig = TestOutcome == 1 ? new[] { 0, 21, 12, 33 }      // A♠ vs 9♥, K♠ vs 8♦: blackjack
                  : TestOutcome == 2 ? new[] { 9, 22, 44, 35, 25 }  // 10♠ vs 10♥, 6♣ vs 10♦, then K♥: bust
                  : new int[0];
        for (int i = rig.Length - 1; i >= 0; --i)
        {
            deck.Remove(rig[i]);
            deck.Insert(0, rig[i]);
        }
    }

    private int Draw()
    {
        int card = deck[0];
        deck.RemoveAt(0);
        return card;
    }

    private void DealNext()
    {
        (dealt % 2 == 0 ? player : dealer).Add(Draw());
        ++dealt;
        SyncHands();
        if (dealt < 4)
        {
            timer = DealInterval;
            return;
        }
        if (Total(player) == 21)
        {
            // A natural: the dealer turns the hole card and can only push it.
            holeHidden = false;
            SyncHands();
            Finish(Total(dealer) == 21 && dealer.Count == 2 ? "Both blackjack. PUSH. You'll live." : "BLACKJACK! Not a scratch.", true);
            return;
        }
        phase = Phase.PlayerTurn;
        table.Set("act", true);
        timer = 0.6f;
    }

    private void PlayerTurn()
    {
        bool hit = hitPressed;
        bool stand = standPressed && !hit;
        if (TestAutoPlay && timer <= 0f)
        {
            hit = Total(player) < 17;
            stand = !hit;
            timer = DealInterval;
        }
        if (hit)
        {
            player.Add(Draw());
            SyncHands();
            int total = Total(player);
            if (total > 21)
            {
                holeHidden = false;
                SyncHands();
                Finish($"BUST with {total}.", false);
            }
            else if (total == 21)
            {
                StartDealer();
            }
        }
        else if (stand)
        {
            StartDealer();
        }
    }

    private void StartDealer()
    {
        table.Set("act", false);
        holeHidden = false;
        SyncHands();
        phase = Phase.DealerTurn;
        timer = DealerInterval;
    }

    // The dealer draws to 17, one card at a time.
    private void DealerStep()
    {
        int dealerTotal = Total(dealer);
        if (dealerTotal < 17)
        {
            dealer.Add(Draw());
            SyncHands();
            timer = DealerInterval;
            return;
        }
        int playerTotal = Total(player);
        if (dealerTotal > 21)
        {
            Finish($"Dealer busts with {dealerTotal}. You live!", true);
        }
        else if (playerTotal > dealerTotal)
        {
            Finish($"{playerTotal} beats {dealerTotal}. You live!", true);
        }
        else if (playerTotal == dealerTotal)
        {
            Finish($"PUSH at {playerTotal}. Barely alive.", true);
        }
        else
        {
            Finish($"Dealer's {dealerTotal} beats your {playerTotal}.", false);
        }
    }

    private void Finish(string text, bool win)
    {
        survived = win;
        table.Set("act", false);
        table.Set("result", text);
        table.Set("outcome", win ? 1 : 2);
        phase = Phase.Reveal;
        timer = RevealTime;
    }

    private void ShowVerdict()
    {
        table.Set("epitaph", survived ? Lives[random.Next(Lives.Length)] : Deaths[random.Next(Deaths.Length)]);
        table.Set(survived ? "survived" : "wasted", true);
        if (!survived && camera)
        {
            savedSaturation = camera.GetField("PostProcess", "Saturation", 1f);
            desaturated = camera.SetField("PostProcess", "Saturation", 0.05f);
        }
        phase = Phase.Verdict;
        timer = RespawnDelay;
    }

    // Clean up the wreck and put the driver back in the seat.
    private void Recover()
    {
        table.Set("survived", false);
        table.Set("wasted", false);
        if (ragdoll)
        {
            ragdoll.Destroy();
        }
        ragdoll = Entity.Null;
        chest = Entity.Null;
        foreach (Entity shard in shards)
        {
            if (shard)
            {
                shard.Destroy();
            }
        }
        shards.Clear();
        if (glass)
        {
            glass.Active = true;
        }
        if (desaturated && camera)
        {
            camera.SetField("PostProcess", "Saturation", savedSaturation);
            desaturated = false;
        }
        if (!survived)
        {
            car.Entity.SetField("BoxCollider", "IsTrigger", false);
        }
        if (survived)
        {
            // Back off the wall, still facing it.
            Transform carTransform = car.Entity.Transform;
            Vector3 forward = carTransform.Forward;
            car.ResetTo(carTransform.WorldPosition - new Vector3(forward.x, 0f, forward.z) * 3f, Mathf.Atan2(forward.x, forward.z) * Mathf.Rad2Deg);
        }
        else
        {
            car.Respawn();
        }
        crashesSeen = car.Crashes;
        if (camera)
        {
            camera.Transform.Parent = cameraParent;
            camera.Transform.Position = cameraLocalPosition;
            camera.Transform.Rotation = cameraLocalRotation;
        }
        CockpitCamera.Suspended = false;
        Input.MouseCaptured = true;
        Time.TimeScale = 1f;
        phase = Phase.Idle;
    }

    // Circle the frozen car (through the verdict if you lived), or chase the body from wherever
    // the camera ended up once it's thrown.
    private void UpdateCamera(float real)
    {
        if (!camera)
        {
            return;
        }
        if (chest)
        {
            Vector3 target = chest.Transform.WorldPosition;
            focus = phase <= Phase.Eject ? target : Mathf.Damp(focus, target, 0.12f, real);
        }
        Vector3 position;
        bool circling = phase <= Phase.Reveal || survived && phase == Phase.Verdict;
        if (circling)
        {
            orbit += OrbitDegreesPerSecond * real;
            float a = orbit * Mathf.Deg2Rad;
            position = focus + new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)) * CameraDistance + Vector3.Up * CameraHeight;
        }
        else
        {
            Vector3 away = camera.Transform.WorldPosition - focus;
            away = new Vector3(away.x, 0f, away.z);
            away = away.LengthSquared() > 0.01f ? away.Normalized() : Vector3.Forward;
            Vector3 wanted = focus + away * CameraDistance + Vector3.Up * CameraHeight;
            position = Mathf.Damp(camera.Transform.WorldPosition, wanted, 0.25f, real);
        }
        // Keep the camera out of hills and walls between it and the body.
        Vector3 toCamera = position - focus;
        float distance = toCamera.Length();
        if (distance > 0.01f && Physics.Raycast(focus, toCamera / distance, distance, out var hit) && !hit.Entity.HasComponent<Rigidbody>())
        {
            position = focus + toCamera / distance * Mathf.Max(hit.Distance - 0.3f, 0.5f);
        }
        camera.Transform.WorldPosition = position;
        camera.Transform.LookAt(focus);
    }

    private void SyncHands()
    {
        SyncHand("p", player);
        SyncHand("d", dealer);
        table.Set("hole", holeHidden);
        int shown = holeHidden && dealer.Count > 0 ? CardValue(dealer[0]) : Total(dealer);
        table.Set("ptotal", player.Count > 0 ? Total(player).ToString() : "");
        table.Set("dtotal", dealer.Count > 0 ? (holeHidden && dealer.Count > 1 ? shown + " + ?" : shown.ToString()) : "");
    }

    private void SyncHand(string prefix, System.Collections.Generic.List<int> hand)
    {
        table.Set(prefix + "n", System.Math.Min(hand.Count, 7));
        for (int i = 0; i < 7; ++i)
        {
            table.Set(prefix + i, i < hand.Count ? Ranks[hand[i] % 13] : "");
            table.Set(prefix + i + "s", i < hand.Count ? hand[i] / 13 : 0);
        }
    }

    private static int CardValue(int card)
    {
        int rank = card % 13;
        return rank == 0 ? 11 : System.Math.Min(rank + 1, 10);
    }

    // Best blackjack total: aces count 11 until that would bust.
    private static int Total(System.Collections.Generic.List<int> hand)
    {
        int total = 0, aces = 0;
        foreach (int card in hand)
        {
            total += CardValue(card);
            aces += card % 13 == 0 ? 1 : 0;
        }
        for (; total > 21 && aces > 0; --aces)
        {
            total -= 10;
        }
        return total;
    }

    private float Rand(float min, float max) => min + (float)random.NextDouble() * (max - min);
}
