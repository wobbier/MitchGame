using System;
using ScriptCore;

public class TransformTest : Script
{
    Transform transformComp;
    public float time = 0.0f;
    public float speed = 1.0f;
    public bool vBool;
    public char vChar;
    public short vShort;
    public int vInt;
    public long vLong;
    public double vDouble;
    public ushort vUShort;
    public uint vUInt;
    public ulong vULong;
    public float vFloat = 0;
    public Vector2 v2;
    public Vector3 v3 = new Vector3(0, 16, 0);

    public override void OnStart()
    {
        if (HasComponent<Transform>())
            Engine.Log("TransformTest: found Transform");

        transformComp = GetComponent<Transform>();
    }

    public override void OnUpdate(float dt)
    {
        if (transformComp == null)
            return;

        Vector3 newTranslation = transformComp.Position;

        bool isShiftHeld = Input.IsKeyDown(KeyCode.LeftShift);
        float speedMultiplier = isShiftHeld ? speed : 1.0f;
        time += dt * speedMultiplier;
        newTranslation.y = (float)Math.Sin(time);

        transformComp.Position = newTranslation;
    }
}


// Plain demo class (not an IGameScript) — ported off the old InternalCall test hooks.
public class TestScript
{
    public float MyPublicFloatVar = 5.0f;

    private string m_Name = "Hello";
    public string Name
    {
        get => m_Name;
        set
        {
            m_Name = value;
            MyPublicFloatVar += 5.0f;
        }
    }
    Vector3 Position = new Vector3(1, 2, 3);
    public float TestFloatProperty
    {
        get; set;
    }

    public void PrintFloatVar()
    {
        Engine.Log($"MyPublicFloatVar = {MyPublicFloatVar:F}");
        Engine.Log($"Position length = {Position.Length():F}");
    }

    private void IncrementFloatVar(float value)
    {
        MyPublicFloatVar += value;
    }
}
