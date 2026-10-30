using ScriptCore;

// RagdollTest (GAME-5): a second in, the waving tube goes limp (Ragdoll.Simulating), falls onto the
// floor, then recovers: the tip must have dropped, and after the blend be back up where the
// animation holds it.
public class RagdollProbe : Script
{
    private float _time;
    private int _stage;
    private float _standing;
    private float _fallen;

    private float TipHeight() => World.Find("Tip").GetComponent<Transform>().WorldPosition.y;

    public override void OnUpdate(float deltaTime)
    {
        _time += deltaTime;
        var ragdoll = GetComponent<Ragdoll>();
        if (_stage == 0 && _time >= 1f)
        {
            _standing = TipHeight();
            ragdoll.Simulating = true;
            _stage = 1;
        }
        else if (_stage == 1 && _time >= 3f)
        {
            _fallen = TipHeight();
            ragdoll.Simulating = false;
            _stage = 2;
        }
        else if (_stage == 2 && _time >= 4f)
        {
            float recovered = TipHeight();
            bool fell = _fallen < _standing - 0.5f;
            bool stood = Mathf.Abs(recovered - _standing) < 0.6f && !ragdoll.Simulating;
            Debug.Log(fell && stood ? "RagdollProbe: PASS"
                : $"RagdollProbe: FAIL standing={_standing:0.00} fallen={_fallen:0.00} recovered={recovered:0.00}");
            _stage = 3;
        }
    }
}
