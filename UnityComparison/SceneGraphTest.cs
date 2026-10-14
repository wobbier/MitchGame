using System.Collections.Generic;
using UnityEngine;

// Unity equivalent of MitchGame's SceneGraphTestCore.
//
// Builds the same deep cube hierarchy and rotates every transform around its
// local Y axis each frame:
//   root(1) -> 16 -> 16 -> 15 -> 14  =  1 + 16 + 256 + 3840 + 53760 = 57,873 transforms
//
// Drop this on an empty GameObject in an otherwise empty scene and press Play.
// For an apples-to-apples render comparison, see the notes at the bottom about
// GPU Instancing / the SRP Batcher.
public class SceneGraphTest : MonoBehaviour
{
    [Header("Hierarchy fan-out (matches the engine test)")]
    public int level1 = 16;
    public int level2 = 16;
    public int level3 = 15;
    public int level4 = 14;

    [Header("Animation")]
    public bool animate = true;

    [Tooltip("Degrees/sec around local Y. Engine uses transform.Rotate({0, 1*dt, 0}).")]
    public float rotationSpeed = 1f;

    [Tooltip("Optional shared material. If left null, one is created with GPU Instancing enabled so all cubes batch (matches the engine).")]
    public Material sharedMaterial;

    [Tooltip("Engine test has no shadows. Leave off for a fair comparison; turning on adds a shadow-caster draw per cube.")]
    public bool castShadows = false;

    private Transform[] _transforms;
    public int TransformCount => _transforms != null ? _transforms.Length : 0;

    void Start()
    {
        EnsureInstancedMaterial();

        var all = new List<Transform>(60000);

        Transform root = MakeCube("Root", transform, Vector3.zero, Vector3.one);
        all.Add(root);

        for (int i = 0; i < level1; i++)
        {
            Transform a = MakeCube($"L1_{i}", root, new Vector3((i - 4.5f) * 2f, -3f, 0f), Vector3.one * 0.5f);
            all.Add(a);

            for (int j = 0; j < level2; j++)
            {
                Transform b = MakeCube($"L2_{j}", a, new Vector3((j - 4.5f) * 2f, -3f, 0f), Vector3.one * 0.5f);
                all.Add(b);

                for (int k = 0; k < level3; k++)
                {
                    Transform c = MakeCube($"L3_{k}", b, new Vector3((k - 4.5f) * 2f, -3f, 0f), Vector3.one * 0.5f);
                    all.Add(c);

                    for (int l = 0; l < level4; l++)
                    {
                        Transform d = MakeCube($"L4_{l}", c, new Vector3((l - 4.5f) * 2f, -3f, 0f), Vector3.one * 0.5f);
                        all.Add(d);
                    }
                }
            }
        }

        _transforms = all.ToArray();
        Debug.Log($"SceneGraphTest spawned {_transforms.Length} transforms.");
    }

    void Update()
    {
        if (!animate || _transforms == null)
            return;

        Vector3 rot = Vector3.up * (rotationSpeed * Time.deltaTime);
        Transform[] arr = _transforms;
        for (int i = 0; i < arr.Length; i++)
        {
            arr[i].Rotate(rot, Space.Self);
        }
    }

    // Build a single shared material with GPU instancing on, so all cubes collapse
    // into instanced draws instead of one batch per cube.
    void EnsureInstancedMaterial()
    {
        if (sharedMaterial != null)
        {
            sharedMaterial.enableInstancing = true;
            return;
        }

        // Reuse whatever Lit shader this pipeline's default cube uses.
        var probe = GameObject.CreatePrimitive(PrimitiveType.Cube);
        Shader shader = probe.GetComponent<MeshRenderer>().sharedMaterial.shader;
        Destroy(probe);

        sharedMaterial = new Material(shader) { enableInstancing = true };
    }

    Transform MakeCube(string name, Transform parent, Vector3 localPos, Vector3 localScale)
    {
        var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
        go.name = name;

        // The engine test has no physics, so drop the auto-added collider.
        var col = go.GetComponent<Collider>();
        if (col != null)
            Destroy(col);

        var mr = go.GetComponent<MeshRenderer>();
        mr.sharedMaterial = sharedMaterial;
        // The engine test renders no shadows; don't pay for shadow-caster draws.
        mr.shadowCastingMode = castShadows
            ? UnityEngine.Rendering.ShadowCastingMode.On
            : UnityEngine.Rendering.ShadowCastingMode.Off;
        mr.receiveShadows = castShadows;

        Transform t = go.transform;
        t.SetParent(parent, false);
        t.localPosition = localPos;
        t.localScale = localScale;
        return t;
    }

    void OnGUI()
    {
        float fps = 1f / Mathf.Max(Time.smoothDeltaTime, 0.0001f);
        GUI.Label(new Rect(10, 10, 400, 20), $"Transforms: {TransformCount}   FPS: {fps:0.0}");
    }
}

// ---------------------------------------------------------------------------
// Notes for a fair comparison
//
// RENDERING:
//   - Built-in pipeline: assign a Material with "Enable GPU Instancing" checked
//     (the `sharedMaterial` field) so the cubes batch like the engine's instancing.
//   - URP/HDRP: the SRP Batcher handles this automatically; leave sharedMaterial
//     null and the default Lit material will batch.
//   - Watch the Stats overlay (Game view > Stats) for "Batches" / "SetPass calls"
//     and the Profiler's Rendering module.
//
// ROTATION:
//   - This rotates on the main thread, like a naive loop. The engine parallelizes
//     rotation across its job system, but in the engine that step is only ~0.5ms,
//     so it's not the thing to match. If you want the parallel comparison, port
//     this loop to IJobParallelForTransform + TransformAccessArray (Unity Jobs).
//
// CAMERAS:
//   - The engine renders this through two cameras (editor + game). To mirror that
//     cost, add a second Camera looking at the grid.
// ---------------------------------------------------------------------------
