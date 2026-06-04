using System.IO;
using Sharpmake;

[module: Sharpmake.Include("Engine/Engine.sharpmake.cs")]

[Generate]
public class SharpGameProject : BaseGameProject
{
    public SharpGameProject()
        : base()
    {
        Name = "MitchGame";
    }
}

[Generate]
public class SharpGameSolution : BaseGameSolution
{
    public SharpGameSolution()
        : base()
    {
        Name = "MitchGame";

        Globals.FMOD_Win64_Dir = "C:/Program Files (x86)/FMOD SoundSystem/FMOD Studio API Windows/";
        Globals.FMOD_UWP_Dir = "C:/Program Files (x86)/FMOD SoundSystem/FMOD Studio API Universal Windows Platform/";
        Globals.DOTNET_Win64_Dir = "C:\\Program Files\\dotnet\\packs\\Microsoft.NETCore.App.Host.win-x64\\8.0.27\\runtimes\\win-x64\\native";
        Globals.IsUltralightEnabled = true;
        Globals.IsPhysicsEnabled3D = true;
        //Globals.ExeName = "MitchGame";
    }
}

[Generate]
public class UserGameScript : GameScript
{
    public UserGameScript() : base() { }

    public override void ConfigureAll(Configuration conf, CommonTarget target)
    {
        base.ConfigureAll(conf, target);
    }
}

[Generate]
public class UserSharpmakeProject : SharpmakeProjectBase
{
    public UserSharpmakeProject() : base() { }
}