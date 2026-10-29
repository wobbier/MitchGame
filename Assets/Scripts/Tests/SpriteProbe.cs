using ScriptCore;

// Drives SpriteScriptTest.lvl / SpriteScriptFlows.edscript (ME-276): the C# SpriteRenderer reads
// and changes a coin's sprite, flips, tint and sorting.
public class SpriteProbe : Script
{
    public override void OnStart() => Run();

    private async void Run()
    {
        var sprite = GetComponent<SpriteRenderer>();
        Debug.Log($"SpriteProbe: found {sprite != null}, showing {sprite?.Sprite}, layer {sprite?.SortingLayer}");
        await Async.Frames(2, this);
        sprite.Sprite = "Coins_2";
        sprite.FlipX = true;
        sprite.Color = new Color(1f, 0.5f, 0.25f, 0.75f);
        sprite.SortingLayer = 3;
        sprite.OrderInLayer = 7;
        await Async.Frames(2, this);
        var color = sprite.Color;
        Debug.Log($"SpriteProbe: now {sprite.Sprite} flipX {sprite.FlipX} flipY {sprite.FlipY} color {color.g:0.00} {color.a:0.00} sorting {sprite.SortingLayer}/{sprite.OrderInLayer}");
    }
}
