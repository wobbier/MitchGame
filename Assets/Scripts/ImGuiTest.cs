using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Threading;

class ImGuiTest : Entity
{
    public bool MyTestBool = false;
    float totalTime = 0.0f;
    public ImGuiTest()
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
        ImGui.Begin("C# Test Menu");
        ImGui.Text("This is my test c# text: " + dt.ToString());
        ImGui.Checkbox("Checkbox Value: " + MyTestBool.ToString(), ref MyTestBool);
        ImGui.End();
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
        totalTime += dt;
    }
}
