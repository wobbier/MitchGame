using System.Collections.Generic;
using ScriptCore;

// A tarot deck on the dashboard: DrawCard (Q) draws the top card, which lifts off the stack and
// flies at the driver, then flips face up on screen. Each of the 22 Major Arcana (TarotCards)
// is drawn once per shuffle and is a weapon (takes over Fire from MissileLauncher until another
// weapon is drawn), a blessing or a curse (timed). The stack shrinks as it's dealt and reshuffles
// once every card has been seen.
// Timed effects scale the car's (VehicleController), the launcher's and the camera's settings from
// the values they had before the first card. The deck, the running effects and those values are
// kept in the view model too (engine-side), so a hot reload carries them over.
// Most cards throw the loose physics props around: Juggernaut flings what the car touches, the
// Lovers pull everything nearby at the car, the Hanged Man floats it all, the Sun's flare and the
// High Priestess's black hole blow it apart. Justice's airstrikes, Death and the Tower can wreck
// the car, which deals a hand of blackjack (CarCrash).
// The cards are Assets/UI/Drive/Tarot.rml, bound to the "tarot" view model this script fills.
public class TarotDeck : Script
{
    public string CameraName = "Main Camera";
    public string LauncherName = "Missile Launcher";
    public string CrashName = "Car Crash";
    public string StackName = "Tarot Stack";
    public string CardName = "Tarot Card";
    public string MissilePrefab = "Assets/Prefabs/Drive/Missile.prefab";
    public string RocketPrefab = "Assets/Prefabs/Drive/Rocket.prefab";
    public string NukePrefab = "Assets/Prefabs/Drive/Nuke.prefab";
    public string ExplosionPrefab = "Assets/Prefabs/Drive/Explosion.prefab";
    public string SmallExplosionPrefab = "Assets/Prefabs/Drive/SmallExplosion.prefab";
    public string SingularityPrefab = "Assets/Prefabs/Drive/Singularity.prefab";
    public string BeamPrefab = "Assets/Prefabs/Drive/LanternBeam.prefab";
    public string SirenClip = "Assets/Sounds/LaunchNight/Alarm.wav";
    // Real seconds between draws, how long a drawn card stays on screen and how long the dash card flies.
    public float DrawCooldown = 2.5f;
    public float RevealTime = 4.0f;
    public float FlyTime = 0.7f;
    // Half the height of the full stack (the stack is a cube spanning -1..1).
    public float StackHalfHeight = 0.018f;
    // The Fool: the launch (up and along the heading, m/s) and the time scale near the top.
    public float FoolLift = 24.0f;
    public float FoolForward = 8.0f;
    public float ApexTimeScale = 0.3f;
    // The Hanged Man: how high the car is hoisted, and how far round it everything floats.
    public float HangHeight = 6.0f;
    public float FloatRadius = 45.0f;
    // The Lovers: how far the pull reaches and how fast things come.
    public float AttractRadius = 45.0f;
    public float AttractSpeed = 24.0f;
    // Juggernaut: how far round the bumper things are flung.
    public float RamRadius = 3.8f;
    // Brood: seconds between missiles.
    public float BroodInterval = 0.45f;
    // The Star: the jump (m/s up).
    public float StarJump = 11.0f;
    // The Sun's flare.
    public float FlareRadius = 40.0f;
    public float FlareSpeed = 32.0f;
    // Justice: seconds between strikes, how close to one wrecks the car, and how far it leads the car.
    public float StrikeInterval = 1.0f;
    public float StrikeRadius = 5.0f;
    public float StrikeLead = 1.6f;
    // The Tower: drop height of the nuke on the car, and how close to ground zero wrecks it.
    public float TowerDropHeight = 130.0f;
    public float TowerKillRadius = 28.0f;
    // Weapons: Divine Decree's spawn height, Final Judgement's charges, the black hole's reach and
    // life, and how fast the Lantern's beam chases the aim.
    public float DecreeHeight = 70.0f;
    public int JudgementCharges = 3;
    public float SingularityRadius = 32.0f;
    public float SingularityLife = 2.8f;
    public float BeamSpeed = 45.0f;
    public float BulletTimeScale = 0.35f;
    // The Light on this entity: its resting colour and intensity (it breathes while a card is ready).
    public Vector3 GlowColor = new Vector3(0.6f, 0.3f, 1f);
    public float GlowIntensity = 0.05f;
    // Automated captures: draw these cards (names of Arcana, comma separated) TestInterval apart,
    // starting after TestDelay, and hold Fire with TestFire.
    public string TestCards = "";
    public float TestDelay = 1.5f;
    public float TestInterval = 2.0f;
    public bool TestFire = false;

    private sealed class Effect
    {
        public Arcana Id;
        public float Left;
        public float Total;
    }

    // A black hole: where it is and how long it has been pulling.
    private sealed class Singularity
    {
        public Entity Entity;
        public Vector3 Center;
        public float Age;
    }

    // A Justice airstrike: the missile, where it's aimed and where it was last seen.
    private sealed class Strike
    {
        public Entity Missile;
        public Vector3 Target;
        public Vector3 Last;
    }

    // The settings the effects scale, as they were before any card.
    private sealed class Baseline
    {
        public float MaxSpeed, Acceleration, Gravity, Steer, CrashSpeed, Throttle;
        public float Cooldown;
        public float FogDensity, Temperature, Bloom, Exposure, SkyTime, MoonPhase, MoonBrightness;
        public Vector3 FogColor;
        public bool Captured;
    }

    // The Wheel of Fortune's odds: mostly rockets, now and then a black hole or a nuke.
    private static readonly Arcana[] Wheel =
    {
        Arcana.Magician, Arcana.Magician, Arcana.Hierophant, Arcana.Hierophant, Arcana.Chariot,
        Arcana.Chariot, Arcana.Chariot, Arcana.Chariot, Arcana.HighPriestess, Arcana.Judgement,
    };

    private static readonly Vector3[] KindColors =
    {
        new Vector3(1f, 0.35f, 0.12f), new Vector3(1f, 0.8f, 0.3f), new Vector3(0.6f, 0.2f, 1f),
    };

    private readonly System.Random random = new System.Random();
    private readonly List<int> deck = new List<int>();
    private readonly List<Effect> effects = new List<Effect>();
    private readonly List<Singularity> singularities = new List<Singularity>();
    private readonly List<Strike> strikes = new List<Strike>();
    private readonly List<Rigidbody> loose = new List<Rigidbody>();
    private readonly List<Vector3> loosePositions = new List<Vector3>();
    private readonly Dictionary<string, object> shown = new Dictionary<string, object>();
    private Baseline baseline = new Baseline();
    private UIModel ui;
    private VehicleController car;
    private Entity camera;
    private Entity launcher;
    private Entity stack;
    private Entity card;
    private Vector3 glowWritten;
    private float glowIntensityWritten = -1f;

    private int weapon = -1;
    private int charges;
    private float weaponReload;
    private float drawCooldown;
    private float age;
    // The card in flight from the dash (-1: none) and the one on screen.
    private int flying = -1;
    private float flyTime;
    private Vector3 cardRestPosition;
    private int revealed = -1;
    private float revealLeft;
    private bool revealRestart;
    private string toast = "";
    private float toastLeft;
    private bool modded;
    private bool timeSlowed;
    private float timeWritten = 1f;
    private float broodTimer;
    private float strikeTimer;
    // The Lantern's beam while Fire is held, and the next burn along it.
    private Entity beam;
    private Vector3 beamPoint;
    private float beamBurn;
    // Hours the sky has been wound forward (The Moon winds it to midnight and on round to morning).
    private float skyOffset;
    private float skyWritten = -1f;
    private bool moonWritten;
    private float fogWritten = -1f, temperatureWritten = -1f, bloomWritten = -1f, exposureWritten = -1f;
    private float fog, temperature, bloom, exposure;
    private Vector3 fogColor;
    // The Hanged Man's hoist, Death's delayed wreck and the Tower's falling nuke.
    private float hangTime = -1f;
    private Vector3 hangOrigin;
    private float hangYaw;
    private float deathTimer = -1f;
    private float respawnTimer = -1f;
    private Entity towerNuke;
    private Vector3 towerTarget;
    private string[] testCards = new string[0];
    private int testIndex;
    private float testTimer;

    public override void OnStart()
    {
        FindParts();
        InitUI();
        Shuffle();
        CaptureBaseline();
        testCards = TestCards.Length > 0 ? TestCards.Split(',') : new string[0];
        testTimer = TestDelay;
        Save();
        SyncUI();
    }

    public override void OnReload()
    {
        FindParts();
        InitUI();
        if (Restore())
        {
            Debug.Log($"Tarot: reloaded with {deck.Count} cards in the deck, {effects.Count} effect(s) running");
        }
        else
        {
            Shuffle();
            CaptureBaseline();
        }
        SyncUI();
    }

    public override void OnDestroy()
    {
        MissileLauncher.FireTaken = false;
        if (timeSlowed)
        {
            Time.TimeScale = 1f;
        }
        StopBeam();
        foreach (Singularity hole in singularities)
        {
            if (hole.Entity)
            {
                hole.Entity.Destroy();
            }
        }
        singularities.Clear();
    }

    private void FindParts()
    {
        car = VehicleController.Active;
        camera = World.Find(CameraName);
        launcher = World.Find(LauncherName);
        stack = World.Find(StackName);
        card = World.Find(CardName);
        if (stack)
        {
            // The stack's bottom stays put as it shrinks; the top card rests just above its top.
            Vector3 p = stack.Transform.Position;
            cardRestPosition = new Vector3(p.x, p.y - stack.Transform.Scale.y + StackHalfHeight * 2f + 0.002f, p.z);
        }
    }

    public override void OnUpdate(float deltaTime)
    {
        float real = Time.UnscaledDeltaTime;
        age += real;
        car = VehicleController.Active;
        bool crashed = car != null && car.Crashed;
        bool driving = car != null && !crashed && !CockpitCamera.Suspended;

        if (respawnTimer >= 0f && (respawnTimer -= real) < 0f && car != null)
        {
            car.Respawn();
        }
        if (!crashed)
        {
            TickEffects(real);
            UpdateLeap();
            if (driving && drawCooldown <= 0f && flying < 0 && WantsDraw(real))
            {
                Draw();
            }
        }
        drawCooldown -= real;
        toastLeft -= real;
        if (revealLeft > 0f && (revealLeft -= real) <= 0f)
        {
            revealed = -1;
        }

        UpdateDeath(real);
        UpdateTower();
        UpdateStrikes(deltaTime, driving);
        UpdateWeapon(deltaTime, driving);
        UpdateSingularities(deltaTime);
        UpdateForces(deltaTime, driving);
        ApplyModifiers(real, crashed);
        AnimateCard(real);
        AnimateGlow();
        SyncUI();
    }

    // The Hanged Man holds the car up after VehicleController has moved it this frame.
    public override void OnLateUpdate(float deltaTime)
    {
        if (hangTime < 0f || car == null)
        {
            return;
        }
        if (car.Crashed || !Has(Arcana.HangedMan))
        {
            hangTime = -1f;
            return;
        }
        hangTime += Time.UnscaledDeltaTime;
        float rise = Mathf.Clamp01(hangTime / 1.2f);
        float height = HangHeight * rise * rise * (3f - 2f * rise) + Mathf.Sin(hangTime * 2.2f) * 0.25f * rise;
        Vector3 sway = new Vector3(Mathf.Sin(hangTime * 1.7f), 0f, Mathf.Cos(hangTime * 1.3f)) * 0.35f * rise;
        car.ResetTo(hangOrigin + Vector3.Up * height + sway, hangYaw + Mathf.Sin(hangTime * 0.9f) * 25f * rise);
    }

    private bool WantsDraw(float real)
    {
        if (Input.WasActionPressed("DrawCard"))
        {
            return true;
        }
        if (testIndex < testCards.Length && (testTimer -= real) <= 0f)
        {
            testTimer = TestInterval;
            return true;
        }
        return false;
    }

    // ---- The deck --------------------------------------------------------------------------------

    private void Shuffle()
    {
        deck.Clear();
        for (int i = 0; i < TarotCards.Count; ++i)
        {
            deck.Add(i);
        }
        for (int i = deck.Count - 1; i > 0; --i)
        {
            int j = random.Next(i + 1);
            (deck[i], deck[j]) = (deck[j], deck[i]);
        }
    }

    // Takes the top card (the end of the list); automated captures stack the deck with TestCards.
    private void Draw()
    {
        // Only a card still in the deck can be rigged to the top; anything else draws the top card.
        if (testIndex < testCards.Length && System.Enum.TryParse(testCards[testIndex++].Trim(), out Arcana rigged) && deck.Remove((int)rigged))
        {
            deck.Add((int)rigged);
        }
        if (deck.Count == 0)
        {
            Shuffle();
        }
        int id = deck[deck.Count - 1];
        deck.RemoveAt(deck.Count - 1);
        drawCooldown = DrawCooldown;
        flying = id;
        flyTime = 0f;
        if (deck.Count == 0)
        {
            Shuffle();
            Toast("Every card has been seen. The deck is reshuffled.");
        }
        Activate(TarotCards.All[id]);
        Save();
    }

    private void Activate(TarotCard drawn)
    {
        Debug.Log($"Tarot: drew {drawn.Name} ({drawn.Title})");
        if (drawn.Kind == ArcanaKind.Weapon)
        {
            weapon = (int)drawn.Id;
            charges = drawn.Id == Arcana.Judgement ? JudgementCharges : 0;
            weaponReload = 0.3f;
            return;
        }
        switch (drawn.Id)
        {
            case Arcana.Fool:
                ThrowCar();
                break;
            case Arcana.Death:
                // The card gets a moment on screen before the wreck.
                deathTimer = 1.2f;
                return;
            case Arcana.Tower:
                DropTowerNuke();
                return;
            case Arcana.Sun:
                Cleanse();
                if (car != null)
                {
                    Shockwave(car.transform.WorldPosition, FlareRadius, FlareSpeed);
                }
                // A white-out that eases back to the golden look.
                exposure += 3f;
                break;
            case Arcana.Justice:
                strikeTimer = 0.6f;
                break;
            case Arcana.Empress:
            case Arcana.World:
                broodTimer = 0f;
                break;
            case Arcana.HangedMan:
                if (car != null)
                {
                    hangTime = 0f;
                    hangOrigin = car.transform.WorldPosition;
                    Vector3 heading = car.transform.Forward;
                    hangYaw = Mathf.Atan2(heading.x, heading.z) * Mathf.Rad2Deg;
                }
                break;
        }
        Effect effect = Find(drawn.Id);
        if (effect == null)
        {
            effect = new Effect { Id = drawn.Id };
            effects.Add(effect);
        }
        effect.Left = effect.Total = drawn.Duration;
    }

    private void TickEffects(float real)
    {
        bool changed = false;
        for (int i = effects.Count - 1; i >= 0; --i)
        {
            if ((effects[i].Left -= real) <= 0f)
            {
                Debug.Log($"Tarot: {TarotCards.Get(effects[i].Id).Title} wore off");
                effects.RemoveAt(i);
                changed = true;
            }
        }
        if (changed)
        {
            Save();
        }
    }

    private Effect Find(Arcana id)
    {
        foreach (Effect e in effects)
        {
            if (e.Id == id)
            {
                return e;
            }
        }
        return null;
    }

    private bool Has(Arcana id) => Find(id) != null;

    // The Sun: every curse in effect ends, and the Tower's nuke and Justice's strikes burn up on
    // the way down.
    private void Cleanse()
    {
        effects.RemoveAll(e => TarotCards.Get(e.Id).Kind == ArcanaKind.Curse);
        hangTime = -1f;
        deathTimer = -1f;
        if (towerNuke)
        {
            towerNuke.Destroy();
            towerNuke = Entity.Null;
        }
        foreach (Strike strike in strikes)
        {
            if (strike.Missile)
            {
                strike.Missile.Destroy();
            }
        }
        strikes.Clear();
    }

    private void Toast(string text)
    {
        toast = text;
        toastLeft = 3f;
    }

    // ---- Instant cards -----------------------------------------------------------------------------

    // The Fool: the car is launched up and on along its heading; time slows near the top of the
    // arc (ApplyModifiers) and the card ends when it lands.
    private void ThrowCar()
    {
        if (car == null)
        {
            return;
        }
        Vector3 forward = car.transform.Forward;
        forward = new Vector3(forward.x, 0f, forward.z).Normalized();
        car.Launch(Vector3.Up * FoolLift + forward * FoolForward);
    }

    private bool AtApex => Has(Arcana.Fool) && car != null && !car.Grounded && Mathf.Abs(car.Velocity.y) < 7f;

    private void UpdateLeap()
    {
        Effect leap = Find(Arcana.Fool);
        if (leap != null && leap.Total - leap.Left > 0.5f && car != null && car.Grounded)
        {
            effects.Remove(leap);
            Toast("Stuck the landing.");
            Save();
        }
    }

    private bool Invulnerable => Has(Arcana.Emperor) || Has(Arcana.World);

    private void UpdateDeath(float real)
    {
        if (deathTimer < 0f || (deathTimer -= real) >= 0f || car == null || car.Crashed)
        {
            return;
        }
        if (Invulnerable)
        {
            Toast("Iron Will cheats Death.");
            return;
        }
        Wreck(car.Velocity.Length() > 15f ? car.Velocity : car.transform.Forward * 18f);
    }

    // Wrecks the car where it is; CarCrash plays it out (or it's back at the spawn after a moment).
    private void Wreck(Vector3 impactVelocity)
    {
        Vector3 forward = car.transform.Forward;
        car.Wreck(impactVelocity, car.transform.WorldPosition + forward * car.BumperLength + Vector3.Up, -forward);
        if (!World.Find(CrashName))
        {
            respawnTimer = 2f;
        }
    }

    // The Tower: a nuke dropped on the car's position; it wrecks the car if it's still close when it lands.
    private void DropTowerNuke()
    {
        if (car == null)
        {
            return;
        }
        towerTarget = car.transform.WorldPosition;
        towerNuke = World.Instantiate(NukePrefab);
        if (towerNuke)
        {
            towerNuke.Transform.WorldPosition = towerTarget + Vector3.Up * TowerDropHeight;
            towerNuke.Transform.LookAt(towerNuke.Transform.WorldPosition - Vector3.Up);
        }
        if (SirenClip.Length > 0)
        {
            Audio.PlayOneShot(SirenClip, 0.6f);
        }
    }

    private void UpdateTower()
    {
        if (towerNuke == Entity.Null)
        {
            return;
        }
        if (towerNuke)
        {
            Debug.DrawSphere(towerTarget, TowerKillRadius, new Vector3(1f, 0.1f, 0.05f));
            return;
        }
        towerNuke = Entity.Null;
        if (car == null || car.Crashed)
        {
            return;
        }
        Vector3 away = car.transform.WorldPosition - towerTarget;
        away = new Vector3(away.x, 0f, away.z);
        if (away.Length() > TowerKillRadius)
        {
            Toast("You got clear. The Tower stands alone.");
        }
        else if (Invulnerable)
        {
            Toast("Iron Will holds. Not a scratch.");
        }
        else
        {
            Vector3 direction = away.LengthSquared() > 0.01f ? away.Normalized() : car.transform.Forward;
            Wreck(direction * 30f + Vector3.Up * 8f);
        }
    }

    // ---- Weapons -----------------------------------------------------------------------------------

    private void UpdateWeapon(float deltaTime, bool driving)
    {
        MissileLauncher.FireTaken = weapon >= 0;
        bool fire = weapon >= 0 && driving && ((CockpitCamera.Aiming && Input.IsActionPressed("Fire")) || TestFire);
        if (weapon == (int)Arcana.Hermit && fire)
        {
            UpdateBeam(deltaTime);
            return;
        }
        StopBeam();
        if (weapon < 0)
        {
            return;
        }
        weaponReload -= deltaTime;
        if (!fire || weaponReload > 0f)
        {
            return;
        }
        Arcana shot = (Arcana)weapon;
        if (shot == Arcana.WheelOfFortune)
        {
            shot = Wheel[random.Next(Wheel.Length)];
        }
        weaponReload = Fire(shot) * (Has(Arcana.Devil) ? 0.2f : 1f);
        if (weapon == (int)Arcana.Judgement && --charges <= 0)
        {
            weapon = -1;
            Toast("Judgement is spent. Back to missiles.");
            Save();
        }
    }

    // Fires one shot of a card weapon and returns its reload time.
    private float Fire(Arcana shot)
    {
        Vector3 start = launcher ? launcher.Transform.WorldPosition : car != null ? car.transform.WorldPosition + Vector3.Up * 2.3f : transform.WorldPosition;
        Vector3 aim = MissileLauncher.AimPoint;
        Vector3 toAim = (aim - start).Normalized();
        Vector3 side = Vector3.Cross(Vector3.Up, toAim);
        side = side.LengthSquared() > 0.01f ? side.Normalized() : Vector3.Right;
        switch (shot)
        {
            case Arcana.Magician:
                for (int i = -2; i <= 2; ++i)
                {
                    Launch(RocketPrefab, start, toAim + side * (i * 0.45f) + Vector3.Up * 0.25f);
                }
                return 0.6f;
            case Arcana.Hierophant:
            {
                Vector3 ground = GroundTarget();
                for (int i = 0; i < 3; ++i)
                {
                    float angle = i * 2.0944f + Rand(0f, 1f);
                    Vector3 from = ground + Vector3.Up * (DecreeHeight + i * 8f) + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * 6f;
                    Entity missile = Launch(MissilePrefab, from, ground - from);
                    if (missile)
                    {
                        Missile.Targets[missile] = ground;
                    }
                }
                return 1.1f;
            }
            case Arcana.Chariot:
                Launch(RocketPrefab, start, toAim + new Vector3(Rand(-0.08f, 0.08f), Rand(0f, 0.1f), Rand(-0.08f, 0.08f)));
                return 0.07f;
            case Arcana.Judgement:
                Entity nuke = World.Instantiate(NukePrefab);
                if (nuke)
                {
                    nuke.Transform.WorldPosition = GroundTarget() + Vector3.Up * 140f;
                    nuke.Transform.LookAt(nuke.Transform.WorldPosition - Vector3.Up);
                }
                return 1.5f;
            case Arcana.HighPriestess:
                OpenSingularity(GroundTarget() + Vector3.Up * 5f);
                return 1.2f;
        }
        return 0.5f;
    }

    // ---- The High Priestess's black holes -----------------------------------------------------

    private void OpenSingularity(Vector3 center)
    {
        if (singularities.Count >= 3)
        {
            return;
        }
        Entity hole = World.Instantiate(SingularityPrefab);
        if (hole)
        {
            hole.Transform.WorldPosition = center;
        }
        singularities.Add(new Singularity { Entity = hole, Center = center });
    }

    // Each hole drags everything loose into a spinning knot, then bursts and flings it all out.
    private void UpdateSingularities(float deltaTime)
    {
        if (deltaTime <= 0f)
        {
            return;
        }
        for (int i = singularities.Count - 1; i >= 0; --i)
        {
            Singularity hole = singularities[i];
            hole.Age += deltaTime;
            if (hole.Age >= SingularityLife)
            {
                if (hole.Entity)
                {
                    hole.Entity.Destroy();
                }
                singularities.RemoveAt(i);
                Shockwave(hole.Center, SingularityRadius, 38f);
                for (int k = 0; k < 3; ++k)
                {
                    Spawn(k == 0 ? ExplosionPrefab : SmallExplosionPrefab, hole.Center + new Vector3(Rand(-2f, 2f), Rand(-1f, 2f), Rand(-2f, 2f)));
                }
                continue;
            }
            float grow = Mathf.Clamp01(hole.Age / 0.4f);
            float size = grow * (1f + 0.15f * Mathf.Sin(hole.Age * 25f) + hole.Age * 0.25f);
            if (hole.Entity)
            {
                hole.Entity.Transform.Scale = new Vector3(size, size, size);
            }
            GatherLoose(hole.Center, SingularityRadius);
            for (int k = 0; k < loose.Count; ++k)
            {
                Vector3 to = hole.Center - loosePositions[k];
                float distance = to.Length();
                if (distance < 0.01f)
                {
                    continue;
                }
                Vector3 inward = to / distance;
                Vector3 swirl = Vector3.Cross(Vector3.Up, inward);
                Vector3 wanted = inward * Mathf.Min(30f, distance * 2.5f) + swirl * Mathf.Min(14f, distance * 1.2f);
                loose[k].Velocity = Mathf.Damp(loose[k].Velocity, wanted * grow, 0.25f, deltaTime);
            }
        }
    }

    // ---- The Hermit's Lantern -------------------------------------------------------------------

    // The beam walks toward the aim point and burns everything along its way.
    private void UpdateBeam(float deltaTime)
    {
        Vector3 target = GroundTarget();
        if (!beam)
        {
            beam = World.Instantiate(BeamPrefab);
            beamPoint = target;
            beamBurn = 0f;
        }
        Vector3 to = target - beamPoint;
        float step = BeamSpeed * deltaTime;
        beamPoint = to.Length() <= step ? target : beamPoint + to.Normalized() * step;
        if (Physics.Raycast(beamPoint + Vector3.Up * 60f, -Vector3.Up, 160f, out var ground) && (car == null || ground.Entity != car.Entity))
        {
            beamPoint = new Vector3(beamPoint.x, ground.Point.y, beamPoint.z);
        }
        if (beam)
        {
            beam.Transform.WorldPosition = beamPoint;
        }
        if ((beamBurn -= deltaTime) <= 0f)
        {
            beamBurn = Has(Arcana.Devil) ? 0.05f : 0.12f;
            Spawn(SmallExplosionPrefab, beamPoint + Vector3.Up * 0.3f);
            Shockwave(beamPoint, 6f, 16f);
        }
    }

    private void StopBeam()
    {
        if (beam)
        {
            beam.Destroy();
        }
        beam = Entity.Null;
    }

    // ---- Justice's airstrikes -------------------------------------------------------------------

    // One strike a second on where the car is heading; a hit close enough to the car wrecks it.
    private void UpdateStrikes(float deltaTime, bool driving)
    {
        if (Has(Arcana.Justice) && driving && (strikeTimer -= deltaTime) <= 0f)
        {
            strikeTimer = StrikeInterval;
            CallStrike();
        }
        for (int i = strikes.Count - 1; i >= 0; --i)
        {
            Strike strike = strikes[i];
            if (strike.Missile)
            {
                strike.Last = strike.Missile.Transform.WorldPosition;
                Debug.DrawSphere(strike.Target, StrikeRadius, new Vector3(1f, 0.1f, 0.05f));
                continue;
            }
            strikes.RemoveAt(i);
            if (car == null || car.Crashed)
            {
                continue;
            }
            Vector3 away = car.transform.WorldPosition - strike.Last;
            away = new Vector3(away.x, 0f, away.z);
            if (away.Length() < StrikeRadius && !Invulnerable)
            {
                Toast("Sentence carried out.");
                Vector3 direction = away.LengthSquared() > 0.01f ? away.Normalized() : car.transform.Forward;
                Wreck(direction * 20f + Vector3.Up * 6f);
            }
        }
    }

    private void CallStrike()
    {
        if (car == null)
        {
            return;
        }
        Vector3 lead = car.Velocity * StrikeLead;
        Vector3 target = car.transform.WorldPosition + new Vector3(lead.x, 0f, lead.z) + new Vector3(Rand(-3f, 3f), 0f, Rand(-3f, 3f));
        if (Physics.Raycast(target + Vector3.Up * 100f, -Vector3.Up, 200f, out var ground) && ground.Entity != car.Entity)
        {
            target = ground.Point;
        }
        float angle = Rand(0f, 6.2831853f);
        Vector3 from = target + Vector3.Up * 85f + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * 15f;
        Entity missile = Launch(MissilePrefab, from, target - from);
        if (missile)
        {
            Missile.Targets[missile] = target;
            strikes.Add(new Strike { Missile = missile, Target = target, Last = target });
        }
    }

    // ---- Forces on the loose props ---------------------------------------------------------------

    // Every loose body (a rigidbody that isn't the car) within radius, into loose / loosePositions.
    private void GatherLoose(Vector3 center, float radius)
    {
        loose.Clear();
        loosePositions.Clear();
        foreach (Entity e in Physics.OverlapSphere(center, radius, 1024))
        {
            if ((car != null && e == car.Entity) || !e.TryGetComponent<Rigidbody>(out var body))
            {
                continue;
            }
            loose.Add(body);
            loosePositions.Add(e.Transform.WorldPosition);
        }
    }

    // Blasts everything loose within radius outward (and up), harder near the middle.
    private void Shockwave(Vector3 center, float radius, float speed)
    {
        GatherLoose(center, radius);
        for (int k = 0; k < loose.Count; ++k)
        {
            Vector3 away = loosePositions[k] - center;
            float distance = away.Length();
            Vector3 flat = new Vector3(away.x, 0f, away.z);
            Vector3 direction = flat.LengthSquared() > 0.01f ? flat.Normalized() : Vector3.Up;
            float falloff = Mathf.Max(1f - distance / radius, 0.25f);
            loose[k].AddForce((direction + Vector3.Up * 0.5f) * speed * falloff, ForceMode.VelocityChange);
        }
    }

    // The running cards that push props around every frame: the Lovers pull, the Hanged Man floats,
    // Juggernaut flings and Brood hunts.
    private void UpdateForces(float deltaTime, bool driving)
    {
        if (car == null || !driving || deltaTime <= 0f)
        {
            return;
        }
        Vector3 position = car.transform.WorldPosition;
        Vector3 forward = car.transform.Forward;
        if (Has(Arcana.Lovers))
        {
            Vector3 heart = position + Vector3.Up * 2.5f;
            GatherLoose(position, AttractRadius);
            for (int k = 0; k < loose.Count; ++k)
            {
                Vector3 to = heart - loosePositions[k];
                float distance = to.Length();
                if (distance < 0.01f)
                {
                    continue;
                }
                Vector3 wanted = to / distance * Mathf.Min(AttractSpeed, 4f + distance * 0.8f) + car.Velocity * 0.5f;
                loose[k].Velocity = Mathf.Damp(loose[k].Velocity, wanted, 0.5f, deltaTime);
            }
        }
        if (Has(Arcana.HangedMan))
        {
            GatherLoose(hangTime >= 0f ? hangOrigin : position, FloatRadius);
            for (int k = 0; k < loose.Count; ++k)
            {
                Vector3 p = loosePositions[k];
                Vector3 drift = new Vector3(Mathf.Sin(p.z * 0.3f + age), 2.2f + Mathf.Sin(p.x * 0.5f + age * 1.3f) * 0.6f, Mathf.Cos(p.x * 0.3f + age));
                loose[k].Velocity = Mathf.Damp(loose[k].Velocity, drift, 0.6f, deltaTime);
            }
        }
        if (Has(Arcana.Emperor) || Has(Arcana.World))
        {
            // Whatever the bumper meets leaves at the car's speed and then some, up and to the side.
            GatherLoose(position + forward * 1.2f + Vector3.Up * 1.0f, RamRadius);
            for (int k = 0; k < loose.Count; ++k)
            {
                Vector3 away = loosePositions[k] - position;
                away = new Vector3(away.x, 0f, away.z);
                away = away.LengthSquared() > 0.01f ? away.Normalized() : forward;
                if (Vector3.Dot(loose[k].Velocity - car.Velocity, away) < 6f)
                {
                    loose[k].Velocity = car.Velocity * 1.2f + away * 8f + Vector3.Up * (10f + Rand(0f, 6f));
                }
            }
        }
        if ((Has(Arcana.Empress) || Has(Arcana.World)) && (broodTimer -= deltaTime) <= 0f)
        {
            broodTimer = BroodInterval;
            LaunchBrood(position, forward);
        }
    }

    // A missile up off the roof at something loose ahead (or the ground out there).
    private void LaunchBrood(Vector3 position, Vector3 forward)
    {
        Vector3 target = Vector3.Zero;
        bool found = false;
        GatherLoose(position + forward * 35f, 35f);
        for (int tries = 0; tries < 6 && loose.Count > 0 && !found; ++tries)
        {
            Vector3 candidate = loosePositions[random.Next(loose.Count)];
            Vector3 to = candidate - position;
            found = to.Length() > 8f && Vector3.Dot(to.Normalized(), forward) > 0.3f;
            target = candidate;
        }
        if (!found)
        {
            Vector3 right = Vector3.Cross(Vector3.Up, forward);
            target = position + forward * Rand(25f, 60f) + right * Rand(-20f, 20f);
            if (Physics.Raycast(target + Vector3.Up * 100f, -Vector3.Up, 200f, out var ground))
            {
                target = ground.Point;
            }
        }
        Vector3 start = launcher ? launcher.Transform.WorldPosition : position + Vector3.Up * 2.3f;
        Vector3 side = Vector3.Cross(Vector3.Up, forward) * Rand(-0.6f, 0.6f);
        Entity missile = Launch(MissilePrefab, start, Vector3.Up + forward * 0.4f + side);
        if (missile)
        {
            Missile.Targets[missile] = target;
        }
    }

    private void Spawn(string prefab, Vector3 position)
    {
        Entity spawned = World.Instantiate(prefab);
        if (spawned)
        {
            spawned.Transform.WorldPosition = position;
        }
    }

    private Entity Launch(string prefab, Vector3 from, Vector3 direction)
    {
        Entity shot = World.Instantiate(prefab);
        if (shot)
        {
            direction = direction.Normalized();
            shot.Transform.WorldPosition = from + direction * 0.4f;
            shot.Transform.LookAt(from + direction * 2f);
        }
        return shot;
    }

    // Where the crosshair meets the world, or the ground 120 m ahead when it's on the sky.
    private Vector3 GroundTarget()
    {
        Vector3 aim = MissileLauncher.AimPoint;
        if (camera)
        {
            Vector3 origin = camera.Transform.WorldPosition;
            Vector3 forward = camera.Transform.Forward;
            if (Physics.Raycast(origin, forward, 400f, out var hit) && hit.Entity != MissileLauncher.Shooter)
            {
                return hit.Point;
            }
            aim = origin + new Vector3(forward.x, 0f, forward.z).Normalized() * 120f;
        }
        if (Physics.Raycast(aim + Vector3.Up * 300f, -Vector3.Up, 600f, out var ground))
        {
            return ground.Point;
        }
        return aim;
    }

    // ---- Effects on the car, launcher and camera ----------------------------------------------------

    private void CaptureBaseline()
    {
        Baseline b = new Baseline();
        if (car != null)
        {
            b.MaxSpeed = car.MaxSpeed;
            b.Acceleration = car.Acceleration;
            b.Gravity = car.Gravity;
            b.Steer = car.SteerDegreesPerSecond;
            b.CrashSpeed = car.CrashSpeed;
            b.Throttle = car.TestThrottle;
        }
        MissileLauncher gun = MissileLauncher.Active;
        if (gun != null)
        {
            b.Cooldown = gun.Cooldown;
        }
        if (camera)
        {
            b.FogDensity = camera.GetField("PostProcess", "FogDensity", 0.008f);
            b.FogColor = camera.GetField("PostProcess", "FogColor", new Vector3(0.55f, 0.62f, 0.72f));
            b.Temperature = camera.GetField("PostProcess", "Temperature", 0f);
            b.Bloom = camera.GetField("PostProcess", "BloomIntensity", 0.06f);
            b.Exposure = camera.GetField("PostProcess", "ExposureCompensation", 0f);
            b.SkyTime = camera.GetField("Camera", "ProceduralSky.Time", 10f);
            b.MoonPhase = camera.GetField("Camera", "ProceduralSky.MoonPhase", 0.4f);
            b.MoonBrightness = camera.GetField("Camera", "ProceduralSky.MoonBrightness", 1f);
        }
        b.Captured = car != null && gun != null && camera;
        baseline = b;
        fog = fogWritten = b.FogDensity;
        fogColor = b.FogColor;
        temperature = temperatureWritten = b.Temperature;
        bloom = bloomWritten = b.Bloom;
        exposure = exposureWritten = b.Exposure;
        skyWritten = 0f;
    }

    private void ApplyModifiers(float real, bool crashed)
    {
        if (!baseline.Captured)
        {
            // The car, launcher or camera wasn't there yet at start.
            FindParts();
            CaptureBaseline();
            if (!baseline.Captured)
            {
                return;
            }
        }
        Baseline b = baseline;
        bool overdrive = Has(Arcana.Strength) || Has(Arcana.World);
        bool devil = Has(Arcana.Devil);
        bool any = effects.Count > 0;

        if ((any || modded) && car != null)
        {
            float speed = overdrive ? 1.8f : 1f;
            if (Has(Arcana.Sun))
            {
                speed *= 1.15f;
            }
            car.MaxSpeed = b.MaxSpeed * speed;
            car.Acceleration = b.Acceleration * (overdrive ? 2.5f : 1f);
            car.Gravity = b.Gravity * (Has(Arcana.Star) ? 0.3f : 1f);
            car.SteerDegreesPerSecond = b.Steer * (devil ? 1.4f : 1f);
            car.CrashSpeed = Invulnerable ? 1e6f : b.CrashSpeed;
            car.TestThrottle = devil ? 1f : b.Throttle;
        }
        MissileLauncher gun = MissileLauncher.Active;
        if ((any || modded) && gun != null)
        {
            gun.Cooldown = devil ? 0.08f : b.Cooldown;
        }
        modded = any;

        // The Star's jump.
        if (Has(Arcana.Star) && car != null && car.Grounded && !crashed && !CockpitCamera.Suspended && Input.WasActionPressed("Jump"))
        {
            car.Launch(Vector3.Up * StarJump);
        }

        // Bullet time, and the slow top of the Fool's leap, unless something else (a crash, the
        // slots) has taken the time scale since it was written.
        float wanted = crashed ? 1f : Has(Arcana.Temperance) ? BulletTimeScale : AtApex ? ApexTimeScale : 1f;
        bool slow = wanted < 1f;
        if (slow || timeSlowed)
        {
            if (!timeSlowed || Mathf.Abs(Time.TimeScale - timeWritten) < 0.001f)
            {
                Time.TimeScale = wanted;
                timeWritten = wanted;
            }
            if (slow != timeSlowed)
            {
                timeSlowed = slow;
                Save();
            }
        }

        if (!camera)
        {
            return;
        }
        // The camera eases toward each effect's look.
        bool moon = Has(Arcana.Moon);
        bool sun = Has(Arcana.Sun);
        bool rose = Has(Arcana.Lovers);
        float targetFog = moon ? 0.01f : b.FogDensity;
        Vector3 targetFogColor = moon ? new Vector3(0.1f, 0.13f, 0.22f) : b.FogColor;
        float targetTemperature = b.Temperature + (sun ? 0.35f : 0f) + (rose ? 0.25f : 0f);
        float targetBloom = b.Bloom + (sun ? 0.15f : 0f) + (rose ? 0.25f : 0f);
        float targetExposure = b.Exposure + (sun ? 0.5f : 0f) + (moon ? 2.4f : 0f);
        fog = Mathf.Damp(fog, targetFog, 0.4f, real);
        fogColor = Mathf.Damp(fogColor, targetFogColor, 0.4f, real);
        temperature = Mathf.Damp(temperature, targetTemperature, 0.3f, real);
        bloom = Mathf.Damp(bloom, targetBloom, 0.3f, real);
        exposure = Mathf.Damp(exposure, targetExposure, 0.4f, real);
        if (Mathf.Abs(fog - fogWritten) > 1e-5f || Mathf.Abs(fog - targetFog) > 1e-5f)
        {
            camera.SetField("PostProcess", "FogDensity", fog);
            camera.SetField("PostProcess", "FogColor", fogColor);
            fogWritten = fog;
        }
        WriteIfChanged("Temperature", temperature, ref temperatureWritten);
        WriteIfChanged("BloomIntensity", bloom, ref bloomWritten);
        WriteIfChanged("ExposureCompensation", exposure, ref exposureWritten);

        // The Moon winds the sky forward to past midnight; afterwards it runs on round to the morning.
        float night = ((24.5f - b.SkyTime) % 24f + 24f) % 24f;
        float target = moon ? (skyOffset > night + 0.01f ? night + 24f : night) : skyOffset > 0f ? 24f : 0f;
        skyOffset = Mathf.Min(skyOffset + 7f * real, target);
        if (skyOffset >= 24f)
        {
            // A full turn of the clock is the same sky.
            skyOffset -= 24f;
        }
        // A full, bright moon lights the night so the road stays (barely) drivable.
        if (moon != moonWritten)
        {
            camera.SetField("Camera", "ProceduralSky.MoonPhase", moon ? 0.5f : b.MoonPhase);
            camera.SetField("Camera", "ProceduralSky.MoonBrightness", moon ? b.MoonBrightness * 4f : b.MoonBrightness);
            moonWritten = moon;
        }
        if (Mathf.Abs(skyOffset - skyWritten) > 1e-4f)
        {
            camera.SetField("Camera", "ProceduralSky.Time", (b.SkyTime + skyOffset) % 24f);
            skyWritten = skyOffset;
            if (skyOffset == target || skyOffset == 0f)
            {
                Save();
            }
        }
    }

    private void WriteIfChanged(string field, float value, ref float written)
    {
        if (Mathf.Abs(value - written) > 1e-4f)
        {
            camera.SetField("PostProcess", field, value);
            written = value;
        }
    }

    // ---- The deck on the dash ------------------------------------------------------------------------

    // The top card lifts off and flies at the driver; then the next one is on top.
    private void AnimateCard(float real)
    {
        if (stack)
        {
            float frac = Mathf.Max(deck.Count / (float)TarotCards.Count, 0.06f);
            Vector3 p = stack.Transform.Position;
            float bottom = p.y - stack.Transform.Scale.y;
            Vector3 s = stack.Transform.Scale;
            stack.Transform.Scale = new Vector3(s.x, StackHalfHeight * frac, s.z);
            stack.Transform.Position = new Vector3(p.x, bottom + StackHalfHeight * frac, p.z);
            cardRestPosition = new Vector3(p.x, bottom + StackHalfHeight * frac * 2f + 0.002f, p.z);
        }
        if (!card)
        {
            if (flying >= 0)
            {
                StartReveal();
            }
            return;
        }
        // The card matches the stack's footprint.
        Vector3 cardScale = stack ? new Vector3(stack.Transform.Scale.x, 0.0015f, stack.Transform.Scale.z) : card.Transform.Scale;
        if (flying < 0)
        {
            card.Transform.Position = cardRestPosition;
            card.Transform.Rotation = Vector3.Zero;
            card.Transform.Scale = cardScale;
            return;
        }
        float before = flyTime;
        flyTime += real;
        float t = flyTime / FlyTime;
        if (before < FlyTime * 0.6f && t >= 0.6f)
        {
            StartReveal();
        }
        if (t >= 1f)
        {
            flying = -1;
            card.Transform.Position = cardRestPosition;
            card.Transform.Rotation = Vector3.Zero;
            card.Transform.Scale = cardScale;
            return;
        }
        // Lift off the stack and wobble over the first half, then fly at the camera (the screen's card
        // flips it face up).
        float lift = Mathf.Clamp01(t * 2f);
        Vector3 local = cardRestPosition + Vector3.Up * (0.1f * (1f - (1f - lift) * (1f - lift)));
        card.Transform.Position = local;
        card.Transform.Rotation = new Vector3(-25f * lift, 0f, Mathf.Sin(lift * 6.2831853f) * 12f);
        if (t > 0.5f && camera)
        {
            // Turn face-on to the driver and shrink away toward the screen's card at the top right.
            float fly = (t - 0.5f) * 2f;
            fly = fly * fly * (3f - 2f * fly);
            Transform view = camera.Transform;
            Vector3 from = card.Transform.WorldPosition;
            Vector3 to = view.WorldPosition + view.Forward * 0.45f + view.Right * 0.16f + view.Up * 0.08f;
            Vector3 position = Vector3.Lerp(from, to, fly);
            card.Transform.WorldPosition = position;
            Vector3 toCamera = (view.WorldPosition - position).Normalized();
            card.Transform.LookDirection(Vector3.Lerp(card.Transform.Forward, view.Up, fly).Normalized(), Vector3.Lerp(card.Transform.Up, toCamera, fly).Normalized());
            card.Transform.Scale = cardScale * (1f - Mathf.Clamp01((t - 0.8f) / 0.2f));
        }
    }

    private void StartReveal()
    {
        revealed = flying;
        revealLeft = RevealTime;
        revealRestart = true;
    }

    // The deck's light breathes while a card is ready and flares in the drawn card's colour.
    private void AnimateGlow()
    {
        float flare = revealed >= 0 ? Mathf.Clamp01(revealLeft - (RevealTime - 1.5f)) : 0f;
        Vector3 color = GlowColor;
        float intensity;
        if (flare > 0f)
        {
            color = Vector3.Lerp(GlowColor, KindColors[(int)TarotCards.All[revealed].Kind], flare);
            intensity = GlowIntensity * (1f + 3f * flare);
        }
        else if (drawCooldown <= 0f && flying < 0)
        {
            intensity = GlowIntensity * (0.75f + 0.25f * Mathf.Sin(age * 3f));
        }
        else
        {
            intensity = GlowIntensity * 0.4f;
        }
        if (Has(Arcana.Moon))
        {
            // Volumetric fog scatters even a faint light into a halo at night.
            intensity = 0f;
        }
        if ((color - glowWritten).LengthSquared() > 1e-6f)
        {
            Entity.SetField("Light", "Color", color);
            glowWritten = color;
        }
        if (Mathf.Abs(intensity - glowIntensityWritten) > 1e-3f)
        {
            Entity.SetField("Light", "Intensity", intensity);
            glowIntensityWritten = intensity;
        }
    }

    // ---- UI ----------------------------------------------------------------------------------------

    private void Set(string key, object value)
    {
        if (shown.TryGetValue(key, out object old) && old.Equals(value))
        {
            return;
        }
        shown[key] = value;
        switch (value)
        {
            case bool flag: ui.Set(key, flag); break;
            case string text: ui.Set(key, text); break;
            case int number: ui.Set(key, number); break;
            case float number: ui.Set(key, number); break;
        }
    }

    // Every value the document binds has to exist when it first binds to the model.
    private void InitUI()
    {
        ui = UI.Model("tarot");
        shown.Clear();
        foreach (string key in new[] { "hud", "ready", "wkind", "reveal", "rfade", "warn", "warnsafe" })
        {
            Set(key, false);
        }
        foreach (string key in new[] { "cool", "weapon", "charges", "toast", "rkindname", "rnum", "rname", "rtitle", "rtext", "warntitle", "warntext" })
        {
            Set(key, "");
        }
        Set("left", 0);
        Set("rkind", 0);
        Set("ricon", "Tarot/Back.png");
        for (int i = 0; i < 6; ++i)
        {
            Set("e" + i, false);
            Set("e" + i + "n", "");
            Set("e" + i + "k", 0);
            Set("e" + i + "w", "0%");
            Set("e" + i + "t", "");
        }
    }

    private void SyncUI()
    {
        bool crashed = car != null && car.Crashed;
        bool hud = !crashed && !CockpitCamera.Suspended;
        Set("hud", hud);
        Set("left", deck.Count);
        Set("ready", drawCooldown <= 0f && flying < 0);
        Set("cool", $"{(int)(100f * Mathf.Clamp01(1f - drawCooldown / DrawCooldown))}%");
        Set("weapon", weapon >= 0 ? TarotCards.All[weapon].Title : "Missiles");
        Set("charges", weapon == (int)Arcana.Judgement ? $"{charges} left" : "");
        Set("wkind", weapon >= 0);
        Set("toast", toastLeft > 0f ? toast : "");

        // Force the reveal off for a frame so its entrance animation plays again for a new card.
        bool reveal = hud && revealed >= 0 && !revealRestart;
        revealRestart = false;
        Set("reveal", reveal);
        if (revealed >= 0)
        {
            TarotCard shownCard = TarotCards.All[revealed];
            Set("rkind", (int)shownCard.Kind);
            Set("rkindname", shownCard.KindName);
            Set("rnum", shownCard.Numeral);
            Set("rname", shownCard.Name.ToUpperInvariant());
            Set("rtitle", shownCard.Title);
            Set("rtext", shownCard.Text);
            Set("ricon", shownCard.Icon);
            Set("rfade", revealLeft < 0.5f);
        }

        // Up to six running effects, in the order they were drawn.
        for (int i = 0; i < 6; ++i)
        {
            Effect e = i < effects.Count ? effects[i] : null;
            Set("e" + i, e != null && hud);
            if (e != null)
            {
                TarotCard c = TarotCards.Get(e.Id);
                Set("e" + i + "n", c.Title);
                Set("e" + i + "k", (int)c.Kind);
                Set("e" + i + "w", $"{(int)(100f * Mathf.Clamp01(e.Left / e.Total))}%");
                Set("e" + i + "t", $"{(int)System.Math.Ceiling(e.Left)}s");
            }
        }

        bool tower = towerNuke != Entity.Null && towerNuke;
        bool warn = hud && (tower || strikes.Count > 0);
        Set("warn", warn);
        if (warn && car != null && tower)
        {
            Vector3 away = car.transform.WorldPosition - towerTarget;
            float distance = new Vector3(away.x, 0f, away.z).Length();
            Set("warntitle", "THE TOWER FALLS");
            Set("warntext", distance > TowerKillRadius ? "CLEAR OF THE BLAST" : $"GET CLEAR! {(int)(TowerKillRadius - distance) + 1} m to safety");
            Set("warnsafe", distance > TowerKillRadius);
        }
        else if (warn && car != null)
        {
            // The closest incoming strike.
            float closest = float.MaxValue;
            foreach (Strike strike in strikes)
            {
                Vector3 away = car.transform.WorldPosition - strike.Target;
                closest = Mathf.Min(closest, new Vector3(away.x, 0f, away.z).Length());
            }
            Set("warntitle", "AIRSTRIKE INBOUND");
            Set("warntext", closest > StrikeRadius ? $"{strikes.Count} incoming. Keep moving!" : "YOU'RE IN THE BLAST. MOVE!");
            Set("warnsafe", closest > StrikeRadius);
        }
    }

    // ---- Hot reload ------------------------------------------------------------------------------

    // The state a hot reload would lose, as comma-separated numbers in the view model (which lives
    // engine-side): the deck, the running effects (id, left, total), the flags and the baseline.
    private void Save()
    {
        var inv = System.Globalization.CultureInfo.InvariantCulture;
        var effectValues = new List<string>();
        foreach (Effect e in effects)
        {
            effectValues.Add(string.Format(inv, "{0},{1:0.###},{2:0.###}", (int)e.Id, e.Left, e.Total));
        }
        Baseline b = baseline;
        float[] values =
        {
            b.MaxSpeed, b.Acceleration, b.Gravity, b.Steer, b.CrashSpeed, b.Throttle,
            b.Cooldown,
            b.FogDensity, b.Temperature, b.Bloom, b.Exposure, b.SkyTime, b.FogColor.x, b.FogColor.y, b.FogColor.z,
            b.MoonPhase, b.MoonBrightness,
        };
        Set("state_deck", string.Join(",", deck));
        Set("state_effects", string.Join(",", effectValues));
        Set("state_flags", string.Format(inv, "{0},{1},{2:0.###},{3}", weapon, charges, skyOffset, timeSlowed ? 1 : 0));
        Set("state_base", b.Captured ? string.Join(",", System.Array.ConvertAll(values, v => v.ToString("R", inv))) : "");
    }

    private bool Restore()
    {
        string[] parts = { ui.GetString("state_deck"), ui.GetString("state_effects"), ui.GetString("state_flags"), ui.GetString("state_base") };
        if (parts[2].Length == 0 || parts[3].Length == 0)
        {
            return false;
        }
        var inv = System.Globalization.CultureInfo.InvariantCulture;
        float[] Numbers(string text) => text.Length == 0 ? new float[0] : System.Array.ConvertAll(text.Split(','), v => float.Parse(v, inv));
        float[] cards, running, flags, v;
        try
        {
            cards = Numbers(parts[0]);
            running = Numbers(parts[1]);
            flags = Numbers(parts[2]);
            v = Numbers(parts[3]);
        }
        catch (System.FormatException)
        {
            return false;
        }
        if (flags.Length != 4 || v.Length != 17)
        {
            return false;
        }
        deck.Clear();
        foreach (float c in cards)
        {
            deck.Add((int)c);
        }
        effects.Clear();
        for (int i = 0; i + 2 < running.Length; i += 3)
        {
            effects.Add(new Effect { Id = (Arcana)(int)running[i], Left = running[i + 1], Total = running[i + 2] });
        }
        weapon = (int)flags[0];
        charges = (int)flags[1];
        skyOffset = flags[2];
        timeSlowed = flags[3] != 0f;
        timeWritten = Time.TimeScale;
        baseline = new Baseline
        {
            MaxSpeed = v[0], Acceleration = v[1], Gravity = v[2], Steer = v[3], CrashSpeed = v[4], Throttle = v[5],
            Cooldown = v[6],
            FogDensity = v[7], Temperature = v[8], Bloom = v[9], Exposure = v[10], SkyTime = v[11], FogColor = new Vector3(v[12], v[13], v[14]),
            MoonPhase = v[15], MoonBrightness = v[16], Captured = true,
        };
        // The camera's current look is wherever the effects had eased it to.
        if (camera)
        {
            fog = fogWritten = camera.GetField("PostProcess", "FogDensity", baseline.FogDensity);
            fogColor = camera.GetField("PostProcess", "FogColor", baseline.FogColor);
            temperature = temperatureWritten = camera.GetField("PostProcess", "Temperature", baseline.Temperature);
            bloom = bloomWritten = camera.GetField("PostProcess", "BloomIntensity", baseline.Bloom);
            exposure = exposureWritten = camera.GetField("PostProcess", "ExposureCompensation", baseline.Exposure);
        }
        skyWritten = skyOffset;
        moonWritten = Has(Arcana.Moon);
        modded = true;
        return true;
    }

    private float Rand(float min, float max) => min + (float)random.NextDouble() * (max - min);
}
