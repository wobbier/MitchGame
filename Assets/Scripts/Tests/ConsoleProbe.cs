using ScriptCore;

// PLAY-10: console commands from C# (ConsoleFlows.edscript runs them through the console).
public static class ConsoleProbe
{
    [ConsoleCommand("greet", "Says hello to its arguments")]
    public static string Greet(string[] args) => "hello " + string.Join(" ", args);

    [ConsoleCommand("probe-count", "How many probes there are")]
    private static string Count() => World.Find("Probe") ? "1 probe" : "no probe";
}
