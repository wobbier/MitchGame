using ScriptCore;

// Drives SettingsTest.lvl / Settings01Write + Settings02Restart (PLAY-2). With Write on, the probe
// changes settings through the C# API, rebinds Jump to J and saves; the next launch (Write off)
// reads them back, and J jumps.
public class SettingsProbe : Script
{
    public bool Write = false;
    [ReadOnly] public string Quality = "";
    [ReadOnly] public float Music;
    [ReadOnly] public int Probe;
    [ReadOnly] public string JumpKey = "";
    [ReadOnly] public int Jumps;

    public override void OnStart()
    {
        if (Write)
        {
            Settings.Quality = "Low";
            Settings.SetVolume(AudioBus.Music, 0.25f);
            Settings.SetInt("Probe", 7);
            Settings.ReduceMotion = true;
            Settings.Rebind("Jump", 0, "Keyboard/J");
            Debug.Log($"SettingsProbe: saved = {Settings.Save()}");
        }
        Quality = Settings.Quality;
        Music = Settings.GetVolume(AudioBus.Music);
        Probe = Settings.GetInt("Probe");
        JumpKey = Settings.GetBindingDisplay("Jump");
        Debug.Log($"SettingsProbe: quality={Quality} music={Music.ToString(System.Globalization.CultureInfo.InvariantCulture)} probe={Probe} jump={JumpKey} reduce-motion={Settings.ReduceMotion} presets={string.Join(",", Settings.QualityPresets)}");
    }

    public override void OnUpdate(float deltaTime)
    {
        if (Input.WasActionPressed("Jump"))
        {
            Jumps++;
            Debug.Log($"SettingsProbe: jump {Jumps}");
        }
    }
}
