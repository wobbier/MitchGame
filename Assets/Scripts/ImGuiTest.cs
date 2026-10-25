using System;
using ScriptCore;

public class ImGuiTest : Script
{
    public bool MyTestBool = false;
    float totalTime = 0.0f;

    public override void OnStart()
    {
        if (HasComponent<Transform>())
            Engine.Log("ImGuiTest: found Transform");
    }

    public override void OnUpdate(float dt)
    {
        ImGui.Begin("C# Test Menu");
        ImGui.Text("This is my test c# text: " + dt.ToString());
        ImGui.Checkbox("Checkbox Value: " + MyTestBool.ToString(), ref MyTestBool);
        if (ImGui.Button("Create Entity"))
        {
            Entity newEntity = World.CreateEntity("C# Entity");
            Debug.Log(newEntity ? "Created new entity successfully" : "Failed to create new entity from C#");
        }
        ImGui.End();

        Transform cameraTransform = World.GetTransformByName("Main Camera");
        if (cameraTransform != null)
        {
            Camera cam = cameraTransform.Entity.GetComponent<Camera>();
            if (cam != null)
                cam.ClearColor += new Vector3(0, 0.0001f, 0);
        }

        totalTime += dt;
    }
}
