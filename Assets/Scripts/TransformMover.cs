using System;
using ScriptCore;

public class TransformMover : Script
{
    public bool MyTestBool = false;
    public float totalTime = 0.0f;

    public override void OnStart()
    {
        if (HasComponent<Transform>())
            Engine.Log("TransformMover: found Transform");
    }

    public override void OnUpdate(float dt)
    {
        var cameraT = World.GetTransformByName("Main Camera");
        if (cameraT != null)
        {
            var cam = cameraT.Entity.GetComponent<Camera>();
            if (cam != null)
                cam.ClearColor += new Vector3(0, 0.0001f, 0);
        }

        var testModel = World.GetTransformByName("POLYGON_Town_Demo-reex");
        if (testModel != null)
            testModel.Scale = new Vector3(1, (float)Math.Sin(totalTime), 1);

        totalTime += dt;
    }
}
