using System;
using ScriptCore;

namespace GameScripts;

public class EnemyAI : Script
{
    public float Aggression = 0.9f;
    public int PatrolRadius = 10;
    public string EnemyType = "Grunt";
    public bool test = false;
    public Vector3 testVec = new Vector3();

    private float _time;

    public override void OnStart()
    {
        var t = transform;                       // null if the entity has no Transform
        Engine.Log($"EnemyAI start on {Entity}: transform={(t != null ? t.Position.ToString() : "none")}");
        testVec.y = 30;
    }

    public override void OnUpdate(float dt)
    {
        if (!Entity) return;                     // implicit bool — false once destroyed

        var t = transform;
        if (t == null) return;                   // fake-null: no Transform component

        // gentle bob — proves get + set round-trip through the fn-ptr table
        _time += dt;
        var p = t.Position;
        p.y += (float)Math.Sin(_time) * dt;
        t.Position = p;

        ImGui.Begin("C# test");
        ImGui.Checkbox("Test Bool", ref test);
        if (test)
        {
            ImGui.Text($"Enemy Type: {EnemyType}");
        }
        ImGui.End();
    }

    public override void OnDestroy()
        => Engine.Log($"EnemyAI destroy on {Entity}: {EnemyType}");

    public override void OnEditorInspect()
    {
        if (ImGui.Button("TestButton"))
            Engine.Log($"Button Clicked: EnemyAI on {Entity}: type={EnemyType}, aggression={Aggression}, patrol={PatrolRadius}");
    }
}
