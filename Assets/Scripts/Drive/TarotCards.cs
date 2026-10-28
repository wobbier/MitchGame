// The 22 Major Arcana of the dashboard tarot deck (TarotDeck): each card is drawn once per shuffle
// and does something no other card does. Weapons take over Fire until another weapon is drawn,
// blessings and curses run for Duration real seconds (0: instant).
public enum ArcanaKind { Weapon, Blessing, Curse }

public enum Arcana
{
    Fool, Magician, HighPriestess, Empress, Emperor, Hierophant, Lovers, Chariot, Strength, Hermit, WheelOfFortune,
    Justice, HangedMan, Death, Temperance, Devil, Tower, Star, Moon, Sun, Judgement, World,
}

public sealed class TarotCard
{
    public readonly Arcana Id;
    public readonly string Name;
    public readonly string Title;
    public readonly string Text;
    public readonly ArcanaKind Kind;
    public readonly float Duration;

    private static readonly string[] Numerals =
    {
        "0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
        "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI",
    };

    public TarotCard(Arcana id, string name, ArcanaKind kind, float duration, string title, string text)
    {
        Id = id;
        Name = name;
        Kind = kind;
        Duration = duration;
        Title = title;
        Text = text;
    }

    public string Numeral => Numerals[(int)Id];
    // The card's art, relative to Assets/UI/Drive/Tarot.rml.
    public string Icon => "Tarot/" + Id + ".png";
    public string KindName => Kind == ArcanaKind.Weapon ? "WEAPON" : Kind == ArcanaKind.Blessing ? "BLESSING" : "CURSE";
}

public static class TarotCards
{
    public const int Count = 22;

    public static readonly TarotCard[] All =
    {
        new TarotCard(Arcana.Fool, "The Fool", ArcanaKind.Blessing, 7f, "Leap of Faith",
            "The car is hurled into the sky and time slows at the top. Rain fire on everything below."),
        new TarotCard(Arcana.Magician, "The Magician", ArcanaKind.Weapon, 0f, "Sleight of Hand",
            "Fire throws a fan of five homing rockets."),
        new TarotCard(Arcana.HighPriestess, "The High Priestess", ArcanaKind.Weapon, 0f, "Singularity",
            "Fire opens a black hole at your aim. It swallows everything loose nearby, then spits it all back out."),
        new TarotCard(Arcana.Empress, "The Empress", ArcanaKind.Blessing, 20f, "Brood",
            "The roof launcher hunts on its own: a missile every half second at whatever's ahead."),
        new TarotCard(Arcana.Emperor, "The Emperor", ArcanaKind.Blessing, 20f, "Juggernaut",
            "Nothing can wreck the car, and everything it touches is sent flying."),
        new TarotCard(Arcana.Hierophant, "The Hierophant", ArcanaKind.Weapon, 0f, "Divine Decree",
            "Each shot calls three missiles down from the heavens onto your aim."),
        new TarotCard(Arcana.Lovers, "The Lovers", ArcanaKind.Curse, 12f, "Fatal Attraction",
            "Everything loose for 45 metres falls madly in love with your car. Here it comes."),
        new TarotCard(Arcana.Chariot, "The Chariot", ArcanaKind.Weapon, 0f, "War Engine",
            "Hold Fire: a rocket minigun."),
        new TarotCard(Arcana.Strength, "Strength", ArcanaKind.Blessing, 20f, "Overdrive",
            "80% more top speed and the acceleration of a dragster."),
        new TarotCard(Arcana.Hermit, "The Hermit", ArcanaKind.Weapon, 0f, "Lantern",
            "Hold Fire: a pillar of light from the heavens follows your aim and burns a trail of fire."),
        new TarotCard(Arcana.WheelOfFortune, "Wheel of Fortune", ArcanaKind.Weapon, 0f, "Roulette",
            "Every shot is a different card weapon. Feeling lucky?"),
        new TarotCard(Arcana.Justice, "Justice", ArcanaKind.Curse, 12f, "Sentenced",
            "Airstrikes are called on your position, one a second. Keep moving or meet the dealer."),
        new TarotCard(Arcana.HangedMan, "The Hanged Man", ArcanaKind.Curse, 6f, "Suspended",
            "Gravity lets go: the car and everything around it float off the ground. What goes up..."),
        new TarotCard(Arcana.Death, "Death", ArcanaKind.Curse, 0f, "The End",
            "The car wrecks on the spot. Play the hand you're dealt."),
        new TarotCard(Arcana.Temperance, "Temperance", ArcanaKind.Blessing, 6f, "Bullet Time",
            "Time slows to a crawl. Line up the perfect shot."),
        new TarotCard(Arcana.Devil, "The Devil", ArcanaKind.Curse, 12f, "Devil's Bargain",
            "The throttle jams wide open, but your weapons never need to reload."),
        new TarotCard(Arcana.Tower, "The Tower", ArcanaKind.Curse, 0f, "Downfall",
            "A nuke is falling on your position. Get clear!"),
        new TarotCard(Arcana.Star, "The Star", ArcanaKind.Blessing, 25f, "Starlight",
            "Gravity loosens its grip and Space jumps. Big air."),
        new TarotCard(Arcana.Moon, "The Moon", ArcanaKind.Curse, 30f, "Lunacy",
            "Night falls in an instant. Watch the road."),
        new TarotCard(Arcana.Sun, "The Sun", ArcanaKind.Blessing, 15f, "Radiance",
            "A solar flare blasts everything away from you, every curse burns off and the world turns golden."),
        new TarotCard(Arcana.Judgement, "Judgement", ArcanaKind.Weapon, 0f, "Final Judgement",
            "Three shots, each calling a nuke down onto your aim."),
        new TarotCard(Arcana.World, "The World", ArcanaKind.Blessing, 15f, "Triumph",
            "Overdrive, Juggernaut and Brood, all at once."),
    };

    public static TarotCard Get(Arcana id) => All[(int)id];
}
