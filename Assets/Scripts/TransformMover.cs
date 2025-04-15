using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

public class TransformMover
    : Entity
{
    public bool MyTestBool = false;
    float totalTime = 0.0f;
    public TransformMover()
        : base()
    {
        OnUpdate(0.0f);
    }

    void OnCreate()
    {
        if (HasComponent<Transform>())
        {
            Console.WriteLine("FOUND TRANSFORM COMPONENT");
        }
    }

    void OnUpdate(float dt)
    {
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
        totalTime += dt;
    }
}