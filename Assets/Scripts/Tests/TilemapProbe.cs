using ScriptCore;

// Drives TilemapTest.lvl / TilemapFlows.edscript (LOOK-S5): the C# Tilemap sets a cell, reads it
// back and maps a world point to its cell.
public class TilemapProbe : Script
{
    public override void OnStart()
    {
        var tilemap = GetComponent<Tilemap>();
        tilemap.SetTile(-6, -2, 1);
        var (x, y) = tilemap.WorldToCell(new Vector3(0.75f, -2.5f, 0f));
        Debug.Log($"TilemapProbe: {tilemap.TileCount} tiles, (-6,-2) = {tilemap.GetTile(-6, -2)}, cell of (0.75, -2.5) is ({x}, {y})");
    }
}
