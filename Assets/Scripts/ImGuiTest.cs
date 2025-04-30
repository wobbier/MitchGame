using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Threading;

class ImGuiTest : Component
{
    public bool MyTestBool = false;
    float totalTime = 0.0f;
    public Vector3 blueAmount = new Vector3(255, 255, 255);

    void OnCreate()
    {
        Console.WriteLine("CREAT IMGUITEST");
        if (HasComponent<Transform>())
        {
            Console.WriteLine("FOUND TRANSFORM COMPONENT");
        }
    }

    public void OnUpdate(float dt)
    {
        ImGui.Begin("C# Test Menu");
        ImGui.Text("This is my test c# text: " + dt.ToString());
        ImGui.Checkbox("Checkbox Value: " + MyTestBool.ToString(), ref MyTestBool);
        ImGui.End();

        Transform cameraTransform = World.GetTransformByName("Main Camera");
        if (cameraTransform != null)
        {
            Camera cam = cameraTransform.Parent.GetComponent<Camera>();
            cam.ClearColor += new Vector3(0, 0.0001f, 0);

            BasicUIView UIView = cameraTransform.Parent.GetComponent<BasicUIView>();
            if (UIView != null)
            {
                UIView.ExecuteJS($"document.body.style.backgroundColor = 'rgba({blueAmount.x}, {blueAmount.y}, {blueAmount.z}, 1)'");
            }
            else
            {
                Debug.Log("no basic UI view");
            }
        }

        totalTime += dt;
    }
}
