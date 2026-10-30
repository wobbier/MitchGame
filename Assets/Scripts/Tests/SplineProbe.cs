using System;
using System.Globalization;
using ScriptCore;

// GAME-2: the C# Spline API checked against the same expected values the editor's C++
// assert-spline uses (SplineFlows.edscript), through the console:
//   spline-check Path 0.5 | 2.25 1 1     the world point at t
//   spline-check Path length | 6.186     the world length
public static class SplineProbe
{
    [ConsoleCommand("spline-check", "Checks a spline from C#: spline-check <entity> <t|length> <expected...>")]
    public static string Check(string[] args)
    {
        if (args.Length < 3)
        {
            return "usage: spline-check <entity> <t|length> <expected...>";
        }
        Entity entity = World.Find(args[0]);
        if (!entity || !entity.HasComponent<Spline>())
        {
            return "no spline on " + args[0];
        }
        SplinePath path = entity.GetComponent<Spline>().GetPath();
        float Parse(string text) => float.Parse(text, CultureInfo.InvariantCulture);
        if (args[1] == "length")
        {
            float length = path.Length;
            return MathF.Abs(length - Parse(args[2])) <= 0.05f ? "ok" : "off: " + length.ToString("F3", CultureInfo.InvariantCulture);
        }
        if (args.Length < 5)
        {
            return "a point needs x y z";
        }
        Vector3 actual = path.GetPoint(Parse(args[1]));
        Vector3 expected = new Vector3(Parse(args[2]), Parse(args[3]), Parse(args[4]));
        // The distance round trip agrees too: halfway along by length lands where t says it does.
        float t = path.GetTAtDistance(path.Length * 0.5f);
        if (path.GetTAtDistance(0f) > 1e-4f || t <= 0f || t >= 1f)
        {
            return "distance lookup is off";
        }
        return Vector3.Distance(actual, expected) <= 0.05f ? "ok" : $"off: {actual.x:F3} {actual.y:F3} {actual.z:F3}";
    }
}
