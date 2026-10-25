using ScriptCore;

// Drives UIModelTest.lvl / UIModelFlows.edscript (UI-3): owns the "probe" view model that
// Assets/UI/Tests/UIModel.rml binds (data-model="probe"). The engine stores the values, so a
// C# hot reload keeps the rendered state; Count is a script field, so the instance swap
// restores it too, and the flow proves the reloaded logic runs.
public class UIProbe : Script
{
    public int Count = 0;
    public int Delta = 1;

    public override void OnStart()
    {
        var model = UI.Model("probe");
        model.Set("title", "Model online");
        model.On("increment");
        Push(model);
    }

    public override void OnUpdate(float deltaTime)
    {
        var model = UI.Model("probe");
        for (string e; (e = model.PollEvent()) != "";)
        {
            if (e == "increment")
            {
                Count += Delta;
                Push(model);
            }
        }
    }

    private void Push(UIModel model)
    {
        model.Set("score", Count.ToString());
        Debug.Log($"UIProbe: score {Count}");
    }
}
