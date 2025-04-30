using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

public class TransformMover
    : Component
{
    public bool MyTestBool = false;
    public float totalTime = 0.0f;
    public TransformMover()
        : base()
    {
        Console.WriteLine("Created a new C# TransformMover Component");
        //Console.WriteLine($"TransformMover ctor: {GetHashCode()}");
    }

    void OnCreate()
    {
        Console.WriteLine("OnCreate C# TransformMover Component");
        if (HasComponent<Transform>())
        {
            Console.WriteLine("FOUND TRANSFORM COMPONENT");
        }
    }

    void OnUpdate(float dt)
    {
        Console.WriteLine($"TransformMover.OnUpdate — Hash: {GetHashCode()}, totalTime: {totalTime}");

        Transform camera = World.GetTransformByName("Main Camera");
        if (camera != null)
        {
            Camera cam = camera.Parent.GetComponent<Camera>();
            cam.ClearColor += new Vector3(0, 0.0001f, 0);
        }
        Transform testModel = World.GetTransformByName("POLYGON_Town_Demo-reex");
        if (testModel != null)
        {
            testModel.Scale = new Vector3(1, (float)Math.Sin(totalTime), 1);
        }
        //if(GetComponent<ImGuiTest>() != null)
        //{
        //}
        if(totalTime == 0.0f)
        {
            Console.WriteLine("OnUpdate C# TransformMover something happened");
        }
        totalTime += dt;
    }
}