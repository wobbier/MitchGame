using System;
using ScriptCore;
using ScriptCore.Kit;

// NEXT-8: BeatClockTest.lvl. A 120 bpm BeatClock follows the looping 2 s Hum on this entity's
// AudioSource: beats fire one after another (0 again when the track loops) and the clock stays
// with the mixer's position. BeatClockFlows waits for the report.
public class BeatProbe : Script
{
    private readonly BeatClock clock = new(120f);
    private int fired;
    private int lastBeat = -1;
    private int problems;
    private string firstProblem = "";
    private bool reported;

    public override void OnStart()
    {
        clock.OnBeat += (beat, bar, inBar) =>
        {
            if (beat != lastBeat + 1 && beat != 0)
            {
                Problem($"beat {beat} after {lastBeat}");
            }
            lastBeat = beat;
            ++fired;
        };
    }

    public override void OnUpdate(float deltaTime)
    {
        var source = GetComponent<AudioSource>();
        clock.Tick(source);
        double playback = source.PlaybackSeconds;
        if (playback >= 0.0 && Math.Abs(clock.SongTime - playback) > 0.1 && Math.Abs(clock.SongTime - playback) < 1.0)
        {
            Problem($"clock {clock.SongTime:0.000} s, mixer {playback:0.000} s");
        }
        if (!reported && fired >= 6)
        {
            reported = true;
            Debug.Log(problems == 0 ? $"BeatProbe: ok, {fired} beats, the track at {playback:0.00} s"
                : $"BeatProbe: FAILED, {problems} problems (first: {firstProblem})");
        }
    }

    private void Problem(string what)
    {
        if (problems++ == 0)
        {
            firstProblem = what;
        }
    }
}
