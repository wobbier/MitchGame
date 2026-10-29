using ScriptCore;

public class ProbeStats : DataAsset
{
    public float Damage = 10f;
    public int Ammo = 30;
    public string Label = "default";
}

// Drives DataAssetTest.lvl / DataAssetFlows.edscript (CS-7): reads a data asset through an
// AssetRef, and logs whenever its values change (the file edited while playing reloads in place).
public class DataAssetProbe : Script
{
    [AssetFilter("asset")] public AssetRef Stats;

    private ProbeStats? stats;
    private float lastDamage = -1f;

    public override void OnStart()
    {
        stats = Stats.Load<ProbeStats>();
        Debug.Log(stats == null ? $"DataAssetProbe: no stats at {Stats}" : $"DataAssetProbe: loaded {stats.AssetPath} damage {stats.Damage} ammo {stats.Ammo} label {stats.Label}");
        // Shared: a second load is the same instance.
        Debug.Log($"DataAssetProbe: shared {ReferenceEquals(stats, Stats.Load<ProbeStats>())}");
        if (stats != null) lastDamage = stats.Damage;
    }

    public override void OnUpdate(float deltaTime)
    {
        if (stats != null && stats.Damage != lastDamage)
        {
            lastDamage = stats.Damage;
            Debug.Log($"DataAssetProbe: damage is now {stats.Damage}");
        }
    }
}
