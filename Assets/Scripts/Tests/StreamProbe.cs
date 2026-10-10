using ScriptCore;

// Streams Assets/Scenes/Tests/AdditiveChunk.lvl in on top of ScriptTest.lvl, finds its crate, then
// unloads it and checks the crate is gone.
public class StreamProbe : Script
{
    private int _scene;
    private bool _unloaded;
    private int _framesSinceUnload;

    public override void OnStart()
    {
        _scene = World.LoadSceneAdditive("Assets/Scenes/Tests/AdditiveChunk.lvl");
    }

    public override void OnUpdate(float deltaTime)
    {
        if (!_unloaded)
        {
            var state = World.GetSceneState(_scene);
            if (state == SceneState.Failed)
            {
                Debug.Log("StreamProbe: FAILED, the chunk didn't load");
                _unloaded = true;
            }
            else if (state == SceneState.Loaded && World.Find("Chunk Crate"))
            {
                Debug.Log("StreamProbe: chunk loaded");
                World.UnloadScene(_scene);
                _unloaded = true;
            }
            return;
        }
        // Destruction lands at the next sync point.
        if (++_framesSinceUnload == 2)
        {
            Debug.Log(World.Find("Chunk Crate") ? "StreamProbe: FAILED, the crate outlived its scene" : "StreamProbe: chunk unloaded");
        }
    }
}
