using ScriptCore;

// SequenceTest exercises the generated native/C# ABI as well as normal runtime playback.
public class SequenceClipProbe : Script
{
    public override void OnStart()
    {
        Sequence sequence = GetComponent<Sequence>();
        if (sequence == null || !sequence.HasClip("DollyZoom"))
        {
            Debug.Log("SequenceClipProbe: FAILED, named clip missing");
            return;
        }
        sequence.Bind("Camera", Entity);
        bool ok = sequence.Play("DollyZoom");
        sequence.Seek(1f);
        sequence.Pause();
        ok &= !sequence.IsPlaying && Mathf.Abs(sequence.Time - 1f) < 0.001f;
        ok &= sequence.Play("DollyZoom", false);
        ok &= sequence.IsPlaying && Mathf.Abs(sequence.Time - 1f) < 0.001f;
        ok &= !sequence.Play("MissingClip") && Mathf.Abs(sequence.Time - 1f) < 0.001f;
        ok &= sequence.PlayAsset("Assets/Animations/CameraDollyZoom.sequence");
        ok &= Mathf.Abs(sequence.Time) < 0.001f;
        sequence.Play();
        Debug.Log(ok ? "SequenceClipProbe: named playback, resume and binding passed"
                     : "SequenceClipProbe: FAILED, playback contract");
    }
}
