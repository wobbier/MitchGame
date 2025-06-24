using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Threading;

class ImGuiTest : Component
{
    public bool MyTestBool = false;
    float totalTime = 0.0f;
    public Vector3 blueAmount = new Vector3(0, 0, 0);
    bool downloadComplete = false;
    string downloadContents = "";

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
        if (ImGui.Button("Download LMAO:"))
        {
            Entity newEntity = World.CreateEntity("UI Entity");
            if (newEntity.AddComponent<BasicUIView>() != null)
            {
                Console.WriteLine("Added UI View fo sho");
            }
            else
            {
                Console.WriteLine("DIDN'T Added UI View fo sho");
            }
            //string downloadTest = HTTP.DownloadFile("https://dlc.mitch.gg/30%20Seconds%20to%20Mars%20-%20The%20Kill/Track.mp3.meta",  "alsmdaiskfoasdgh.meta");
            //downloadComplete = downloadTest != null;
            //if( downloadTest != null )
            //{
            //    downloadContents = downloadTest;
            //}
        }
        if (ImGui.Button("Create Entity"))
        {
            Entity newEntity = World.CreateEntity("C# Entity");
            if (newEntity != null)
            {
                Console.WriteLine("Created new entity successfully");
            }
            else
            {
                Console.WriteLine("Failed to create new entity from C#");
            }
        }
        if (downloadContents != null)
        {
            ImGui.Text("This is my test c# text: " + downloadContents);
        }
        ImGui.End();

        Transform cameraTransform = World.GetTransformByName("Main Camera");
        if (cameraTransform != null)
        {
            Camera cam = cameraTransform.Parent.GetComponent<Camera>();
            cam.ClearColor += new Vector3(0, 0.0001f, 0);

        }

        BasicUIView UIView = GetComponent<BasicUIView>();
        if (UIView != null)
        {
            UIView.ExecuteJS($"document.body.style.backgroundColor = 'rgba({blueAmount.x}, {blueAmount.y}, {blueAmount.z}, 1)'");
        }
        else
        {
            Debug.Log("no basic UI view");
        }

        totalTime += dt;
    }
}
