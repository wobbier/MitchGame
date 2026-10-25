using ScriptCore;

// A roadside slot machine: drive into its trigger sphere (a SphereCollider with IsTrigger on this
// entity) and press Interact (E) to spin. Three radiation symbols
// is the max win, which drops a nuke on the map a little way ahead of the car.
// The reels are Assets/UI/Drive/Slots.rml, bound to the "slots" view model this script fills.
public class SlotMachine : Script
{
    public string VehicleName = "Vehicle";
    public string NukePrefab = "Assets/Prefabs/Drive/Nuke.prefab";
    public float SpinTime = 2.4f;
    public int Credits = 100;
    public int Bet = 10;
    // Chance of the max win per spin, and of any other three-of-a-kind / pair.
    public float JackpotChance = 0.1f;
    public float TripleChance = 0.12f;
    public float PairChance = 0.3f;
    public float NukeDistance = 70.0f;
    public float NukeDropHeight = 180.0f;
    // Automated captures: spin once on start (forcing the max win when TestJackpot is set).
    public bool TestSpin = false;
    public bool TestJackpot = false;

    private const int Nuke = 4;
    private const int SymbolCount = 5;
    private const float ReelTick = 0.06f;
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
    private readonly bool[] reelStopped = new bool[3];

    public override void OnStart()
    {
        vehicle = World.Find(VehicleName);
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
        if (TestJackpot || roll < JackpotChance)
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
        spinElapsed = 0f;
        reelTimer = 0f;
        for (int i = 0; i < 3; ++i)
        {
            reelStopped[i] = false;
            slots.Set("s" + i, true);
        }
        spinLeft = SpinTime + 0.1f;
        SyncUI();
    }

    // Reel i stops on its final symbol at SpinTime * (0.45 + 0.275 * i); until then it flickers.
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
            if (spinElapsed >= SpinTime * (0.45f + 0.275f * i))
            {
                reelStopped[i] = true;
                slots.Set("r" + i, result[i]);
                slots.Set("s" + i, false);
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
        if (a == Nuke && b == Nuke && c == Nuke)
        {
            SetResult("MAX WIN! NUCLEAR LAUNCH DETECTED", true);
            DropNuke();
        }
        else if (a == b && b == c)
        {
            int win = Bet * Payouts[a];
            Credits += win;
            SetResult($"WIN {win}!", false);
        }
        else if (a == b || b == c || a == c)
        {
            Credits += Bet * 2;
            SetResult($"Pair - won {Bet * 2}", false);
        }
        else
        {
            SetResult("No luck", false);
        }
        SyncUI();
    }

    private void SetResult(string text, bool jackpot)
    {
        resultText = text;
        resultJackpot = jackpot;
    }

    private void SyncUI()
    {
        slots.Set("credits", Credits);
        slots.Set("machine", machineShown);
        slots.Set("prompt", nearby && spinLeft < 0f);
        slots.Set("result", spinLeft < 0f ? resultText : "");
        slots.Set("jackpot", spinLeft < 0f && resultJackpot);
    }

    private void DropNuke()
    {
        Vector3 origin = vehicle ? vehicle.Transform.WorldPosition : transform.WorldPosition;
        Vector3 forward = vehicle ? vehicle.Transform.Forward : transform.Forward;
        Vector3 target = origin + forward * NukeDistance;
        Entity nuke = World.Instantiate(NukePrefab);
        if (nuke)
        {
            nuke.Transform.WorldPosition = new Vector3(target.x, origin.y + NukeDropHeight, target.z);
            nuke.Transform.LookAt(nuke.Transform.WorldPosition - Vector3.Up);
        }
    }
}
