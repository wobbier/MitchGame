using ScriptCore;

// A roadside slot machine: drive into its trigger sphere (a SphereCollider with IsTrigger on this
// entity) and press Interact (E) to spin. Three radiation symbols is the max win: time slows and a
// nuke storm rains down around the road ahead of the car.
// While it spins the cabinet strobes, shakes and spins its sign; two radiation symbols on the first
// reels stall the last one for a tense near miss.
// The reels are Assets/UI/Drive/Slots.rml, bound to the "slots" view model this script fills.
public class SlotMachine : Script
{
    public string VehicleName = "Vehicle";
    public string NukePrefab = "Assets/Prefabs/Drive/Nuke.prefab";
    public float SpinTime = 2.4f;
    public int Credits = 100;
    public int Bet = 10;
    // Chance of the max win per spin, and of any other three-of-a-kind / pair.
    public float JackpotChance = 0.4f;
    // A max win is guaranteed after this many spins without one.
    public int MaxWinPity = 2;
    public float TripleChance = 0.12f;
    public float PairChance = 0.3f;
    public float NukeDistance = 70.0f;
    public float NukeDropHeight = 180.0f;
    // The max win drops this many nukes, one after another, scattered around the first.
    public int NukeStormMin = 3;
    public int NukeStormMax = 7;
    public float NukeStormRadius = 55.0f;
    public float NukeStormInterval = 0.35f;
    // Time scale and real-time length of the slow motion when the max win lands.
    public float JackpotSlowMo = 0.3f;
    public float SlowMoTime = 1.5f;
    // Extra seconds the last reel keeps spinning when the first two show radiation.
    public float NearMissStall = 1.6f;
    // Automated captures: spin once on start (forcing the max win when TestJackpot is set).
    public bool TestSpin = false;
    public bool TestJackpot = false;

    private const int Nuke = 4;
    private const int SymbolCount = 5;
    private const float ReelTick = 0.06f;
    private const float CelebrateTime = 6.0f;
    private static readonly int[] Payouts = { 50, 20, 10, 5 };

    private UIModel slots;
    private Entity vehicle;
    private readonly System.Random random = new System.Random();
    private bool nearby;
    private float spinLeft = -1f;
    private int[] result = new int[3];
    private float hideTimer;
    private bool machineShown;
    private string resultText = "";
    private bool resultJackpot;
    private float age;
    // The running spin: reels stop one after another, flickering random symbols until then.
    private float spinElapsed;
    private float reelTimer;
    private int spinsSinceMaxWin;
    private readonly bool[] reelStopped = new bool[3];
    private bool nearMiss;
    // The show around a spin: cabinet parts, the light's resting look and the celebration after a win.
    private Entity cabinet, screen, sign, leverArm, leverKnob, tray;
    private Vector3[] restPositions = new Vector3[0];
    private Vector3 baseLightColor = new Vector3(1f, 0.75f, 0.3f);
    private float baseLightIntensity = 25f;
    private float celebrate;
    private float winFlash;
    private float signSpin;
    private float lever;
    private int nukesLeft;
    private int nukesDropped;
    private bool lightAnimated;
    private float nukeTimer;
    private float slowMoLeft;

    public override void OnStart()
    {
        vehicle = World.Find(VehicleName);
        cabinet = World.Find("Slot Cabinet");
        screen = World.Find("Slot Screen");
        sign = World.Find("Slot Sign");
        leverArm = World.Find("Slot Lever Arm");
        leverKnob = World.Find("Slot Lever Knob");
        tray = World.Find("Slot Tray");
        if (spinLeft < 0f && celebrate <= 0f)
        {
            Entity[] shaken = Shaken();
            restPositions = new Vector3[shaken.Length];
            for (int i = 0; i < shaken.Length; ++i)
            {
                restPositions[i] = shaken[i] ? shaken[i].Transform.Position : Vector3.Zero;
            }
            baseLightColor = Entity.GetField("Light", "Color", baseLightColor);
            baseLightIntensity = Entity.GetField("Light", "Intensity", baseLightIntensity);
        }
        // Values live engine-side, so a hot reload (which calls OnStart again) keeps the screen.
        slots = UI.Model("slots");
        if (spinLeft < 0f)
        {
            for (int i = 0; i < 3; ++i)
            {
                slots.Set("r" + i, result[i]);
                slots.Set("s" + i, false);
            }
        }
        SyncUI();
    }

    public override void OnReload()
    {
        OnStart();
    }

    public override void OnDestroy()
    {
        if (slowMoLeft > 0f)
        {
            Time.TimeScale = 1f;
        }
    }

    public override void OnUpdate(float deltaTime)
    {
        age += deltaTime;
        if (machineShown && !nearby && spinLeft < 0f && (hideTimer += deltaTime) > 1.5f)
        {
            machineShown = false;
            SyncUI();
        }

        if (spinLeft < 0f && ((nearby && Input.WasActionPressed("Interact")) || (TestSpin && age > 2f)))
        {
            TestSpin = false;
            StartSpin();
        }
        if (spinLeft >= 0f)
        {
            AnimateReels(deltaTime);
            if ((spinLeft -= deltaTime) < 0f)
            {
                FinishSpin();
            }
        }

        if (slowMoLeft > 0f && (slowMoLeft -= Time.UnscaledDeltaTime) <= 0f)
        {
            Time.TimeScale = 1f;
        }
        for (nukeTimer -= deltaTime; nukesLeft > 0 && nukeTimer <= 0f; nukeTimer += NukeStormInterval)
        {
            --nukesLeft;
            DropNuke(nukesDropped++ == 0);
        }
        AnimateCabinet(deltaTime);
    }

    public override void OnTriggerEnter(Entity other)
    {
        if (other == vehicle)
        {
            nearby = true;
            machineShown = true;
            hideTimer = 0f;
            SyncUI();
        }
    }

    public override void OnTriggerExit(Entity other)
    {
        if (other == vehicle)
        {
            nearby = false;
            SyncUI();
        }
    }

    private void StartSpin()
    {
        if (Credits < Bet)
        {
            Credits = 100;
        }
        Credits -= Bet;
        machineShown = true;
        SetResult("", false);
        SyncUI();

        double roll = random.NextDouble();
        if (TestJackpot || roll < JackpotChance || spinsSinceMaxWin >= MaxWinPity)
        {
            result = new[] { Nuke, Nuke, Nuke };
        }
        else if (roll < JackpotChance + TripleChance)
        {
            int s = random.Next(0, Nuke);
            result = new[] { s, s, s };
        }
        else
        {
            // A pair or nothing, never three of a kind.
            int a = random.Next(0, Nuke + 1);
            int b = roll < JackpotChance + TripleChance + PairChance ? a : random.Next(0, Nuke + 1);
            int c;
            do { c = random.Next(0, Nuke + 1); } while (c == a && c == b);
            result = new[] { a, b, c };
            if (random.Next(2) == 0)
            {
                (result[1], result[2]) = (result[2], result[1]);
            }
        }
        nearMiss = result[0] == Nuke && result[1] == Nuke;
        spinElapsed = 0f;
        reelTimer = 0f;
        for (int i = 0; i < 3; ++i)
        {
            reelStopped[i] = false;
            slots.Set("s" + i, true);
        }
        spinLeft = ReelStopTime(2) + 0.1f;
        lever = 1f;
        celebrate = 0f;
        SyncUI();
    }

    // Reel i stops on its final symbol at SpinTime * (0.45 + 0.275 * i), the last one later on a near miss.
    private float ReelStopTime(int reel)
    {
        return SpinTime * (0.45f + 0.275f * reel) + (reel == 2 && nearMiss ? NearMissStall : 0f);
    }

    private void AnimateReels(float deltaTime)
    {
        spinElapsed += deltaTime;
        bool tick = (reelTimer -= deltaTime) <= 0f;
        if (tick)
        {
            reelTimer = ReelTick;
        }
        for (int i = 0; i < 3; ++i)
        {
            if (reelStopped[i])
            {
                continue;
            }
            if (spinElapsed >= ReelStopTime(i))
            {
                reelStopped[i] = true;
                slots.Set("r" + i, result[i]);
                slots.Set("s" + i, false);
                SyncUI();
            }
            else if (tick)
            {
                slots.Set("r" + i, random.Next(0, SymbolCount));
            }
        }
    }

    private void FinishSpin()
    {
        int a = result[0], b = result[1], c = result[2];
        ++spinsSinceMaxWin;
        if (a == Nuke && b == Nuke && c == Nuke)
        {
            spinsSinceMaxWin = 0;
            int count = random.Next(NukeStormMin, NukeStormMax + 1);
            Credits += Bet * 100;
            SetResult($"MAX WIN! {count} NUKES INBOUND", true);
            nukesLeft = count;
            nukesDropped = 0;
            nukeTimer = 0f;
            celebrate = CelebrateTime;
            Time.TimeScale = JackpotSlowMo;
            slowMoLeft = SlowMoTime;
        }
        else if (a == b && b == c)
        {
            int win = Bet * Payouts[a];
            Credits += win;
            SetResult($"WIN {win}!", false);
            winFlash = 1.5f;
        }
        else if (a == b || b == c || a == c)
        {
            Credits += Bet * 2;
            SetResult($"Pair - won {Bet * 2}", false);
            winFlash = 0.6f;
        }
        else
        {
            SetResult(nearMiss ? "SO CLOSE" : "No luck", false);
        }
        nearMiss = false;
        SyncUI();
    }

    private void SetResult(string text, bool jackpot)
    {
        resultText = text;
        resultJackpot = jackpot;
    }

    private void SyncUI()
    {
        bool spinning = spinLeft >= 0f;
        slots.Set("credits", Credits);
        slots.Set("machine", machineShown);
        slots.Set("prompt", nearby && !spinning);
        slots.Set("result", spinning ? "" : resultText);
        slots.Set("jackpot", !spinning && resultJackpot);
        slots.Set("spinning", spinning);
        slots.Set("tension", spinning && nearMiss && reelStopped[1]);
        slots.Set("fever", celebrate > 0f);
    }

    private Entity[] Shaken() => new[] { cabinet, screen, sign, leverArm, leverKnob, tray };

    // The light strobes through colours, the cabinet rattles, the sign spins and the lever yanks down.
    private void AnimateCabinet(float deltaTime)
    {
        bool spinning = spinLeft >= 0f;
        bool tension = spinning && nearMiss && reelStopped[1];
        bool wasCelebrating = celebrate > 0f;
        celebrate = Mathf.Max(celebrate - deltaTime, 0f);
        winFlash = Mathf.Max(winFlash - deltaTime, 0f);
        if (wasCelebrating && celebrate <= 0f)
        {
            SyncUI();
        }

        float shake;
        float spinSpeed;
        if (tension)
        {
            float pulse = (age * 14f) % 1f < 0.5f ? 1f : 0.15f;
            Entity.SetField("Light", "Color", new Vector3(1f, 0.08f, 0.04f));
            Entity.SetField("Light", "Intensity", baseLightIntensity * 6f * pulse);
            shake = 0.06f;
            spinSpeed = 1440f;
        }
        else if (celebrate > 0f)
        {
            float fade = Mathf.Min(celebrate / 1.5f, 1f);
            float strobe = (age * 18f) % 1f < 0.5f ? 1f : 0.3f;
            Entity.SetField("Light", "Color", Hue(age * 3f));
            Entity.SetField("Light", "Intensity", baseLightIntensity + baseLightIntensity * 10f * strobe * fade);
            shake = 0.09f * fade;
            spinSpeed = 2000f * fade;
        }
        else if (spinning)
        {
            float strobe = (age * 10f) % 1f < 0.5f ? 1f : 0.4f;
            Entity.SetField("Light", "Color", Hue(age * 1.5f));
            Entity.SetField("Light", "Intensity", baseLightIntensity * 3f * strobe);
            shake = 0.025f;
            spinSpeed = 720f;
        }
        else if (winFlash > 0f)
        {
            float strobe = (age * 12f) % 1f < 0.5f ? 1f : 0.3f;
            Entity.SetField("Light", "Color", new Vector3(1f, 0.85f, 0.2f));
            Entity.SetField("Light", "Intensity", baseLightIntensity * 4f * strobe);
            shake = 0.015f;
            spinSpeed = 540f;
        }
        else
        {
            if (lightAnimated)
            {
                Entity.SetField("Light", "Color", baseLightColor);
                Entity.SetField("Light", "Intensity", baseLightIntensity);
            }
            shake = 0f;
            spinSpeed = 0f;
        }

        lightAnimated = spinSpeed > 0f;

        Entity[] shaken = Shaken();
        for (int i = 0; i < shaken.Length && i < restPositions.Length; ++i)
        {
            if (!shaken[i])
            {
                continue;
            }
            Vector3 jitter = shake > 0f ? new Vector3(Rand(-shake, shake), Rand(-shake, shake), Rand(-shake, shake)) : Vector3.Zero;
            shaken[i].Transform.Position = restPositions[i] + jitter;
        }

        // The sign whirls while there's action and eases back to face the road afterwards.
        if (sign)
        {
            signSpin = spinSpeed > 0f ? (signSpin + spinSpeed * deltaTime) % 360f : Mathf.Damp(signSpin > 180f ? signSpin - 360f : signSpin, 0f, 0.15f, deltaTime);
            sign.Transform.Rotation = new Vector3(0f, signSpin, 0f);
        }

        // Lever: the knob drops to the arm's pivot and springs back; the arm shrinks to follow it.
        lever = Mathf.Max(lever - deltaTime * 2.5f, 0f);
        if (leverArm && leverKnob && restPositions.Length == 6)
        {
            Vector3 knobRest = restPositions[4];
            Vector3 armRest = restPositions[3];
            float pivot = armRest.y - 0.7f;
            float knobY = Mathf.Lerp(knobRest.y, pivot + 0.35f, Mathf.Min(lever * 1.6f, 1f));
            leverKnob.Transform.Position = new Vector3(knobRest.x, knobY, knobRest.z) + (leverKnob.Transform.Position - knobRest);
            float height = (knobY - (knobRest.y - armRest.y - 0.7f) - pivot) * 0.5f;
            leverArm.Transform.Position = new Vector3(armRest.x, pivot + height, armRest.z) + (leverArm.Transform.Position - armRest);
            leverArm.Transform.Scale = new Vector3(0.07f, height, 0.07f);
        }
    }

    private static Vector3 Hue(float h)
    {
        h = (h % 1f) * 6f;
        float x = 1f - Mathf.Abs(h % 2f - 1f);
        return h < 1f ? new Vector3(1f, x, 0f)
             : h < 2f ? new Vector3(x, 1f, 0f)
             : h < 3f ? new Vector3(0f, 1f, x)
             : h < 4f ? new Vector3(0f, x, 1f)
             : h < 5f ? new Vector3(x, 0f, 1f)
             : new Vector3(1f, 0f, x);
    }

    private float Rand(float min, float max) => min + (float)random.NextDouble() * (max - min);

    // The first bomb of a storm lands on the road ahead; the rest scatter around it.
    private void DropNuke(bool first)
    {
        Vector3 origin = vehicle ? vehicle.Transform.WorldPosition : transform.WorldPosition;
        Vector3 forward = vehicle ? vehicle.Transform.Forward : transform.Forward;
        Vector3 target = origin + forward * NukeDistance;
        if (!first)
        {
            float angle = Rand(0f, 6.2831853f);
            float distance = NukeStormRadius * Mathf.Sqrt(Rand(0.15f, 1f));
            target += new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * distance;
        }
        Entity nuke = World.Instantiate(NukePrefab);
        if (nuke)
        {
            nuke.Transform.WorldPosition = new Vector3(target.x, origin.y + NukeDropHeight + Rand(0f, 40f), target.z);
            nuke.Transform.LookAt(nuke.Transform.WorldPosition - Vector3.Up);
        }
    }
}
