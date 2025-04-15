#pragma once
#include "imgui.h"
#include "misc/cpp/imgui_stdlib.h"
#include "Engine/Engine.h"
#include "ECS/EntityHandle.h"
#include "Engine/World.h"
#include "Components/Graphics/Model.h"

class SyntyUnityImporter
    : public Component<SyntyUnityImporter>
{
public:
    SyntyUnityImporter()
        : Component( "SyntyUnityImporter" )
    {

    }

#if USING( ME_EDITOR )

    void CreateChildRecursive(json& inJson, EntityHandle& inParent)
    {
        std::string name = inJson["meshName"];
        std::string objectName = inJson["objectName"];

        Vector3 pos = Vector3( (float)inJson["position"]["x"], (float)inJson["position"]["y"], (float)inJson["position"]["z"]);
        Vector3 rot = Vector3( (float)inJson["rotation"]["x"], (float)inJson["rotation"]["y"], (float)inJson["rotation"]["z"] );
        Vector3 scale = Vector3( (float)inJson["scale"]["x"], (float)inJson["scale"]["y"], (float)inJson["scale"]["z"] );

        SharedPtr<World> gameWorld = GetEngine().GetWorld().lock();
        EntityHandle handle = gameWorld->CreateEntity();
        Transform& trans = handle->AddComponent<Transform>();
        trans.SetName( objectName );
        trans.SetParent( inParent->GetComponent<Transform>() );
        trans.SetPosition( pos );
        trans.SetRotation( rot );
        trans.SetScale( scale );

        if( !name.empty() )
        {
            std::string modelPath = ModelDirectory + "/" + name + ".fbx";
            handle->AddComponent<Model>( modelPath );
        }


        json& children = inJson["children"];
        for (json& c : children)
        {
            CreateChildRecursive( c, handle );
        }
    }

    virtual void OnEditorInspect() final
    {
        if( ImGui::Button( "Import" ) )
        {
            Path filePath = Path( ImportPath );
            if( !filePath.Exists )
            {
                return;
            }

            File exportFile( filePath );
            json exportJson = json::parse(exportFile.Read());
            json& objects = exportJson["rootNodes"];
            for (json& j : objects )
            {
                CreateChildRecursive( j, Parent );
            }
        }

        ImGui::InputText( "Import File", &ImportPath );
        ImGui::InputText( "Model Directory", &ModelDirectory );
    }
#endif

    virtual void Init() final
    {
    }

private:
    void OnSerialize( json& outJson ) final
    {
        outJson["ImportPath"] = ImportPath;
        outJson["ModelDirectory"] = ModelDirectory;
    }

    void OnDeserialize( const json& inJson ) final
    {
        if( inJson.contains( "ImportPath" ) )
        {
            ImportPath = inJson["ImportPath"];
        }

        if( inJson.contains( "ModelDirectory" ) )
        {
            ModelDirectory = inJson["ModelDirectory"];
        }
    }

    std::string ImportPath;
    std::string ModelDirectory;
};

ME_REGISTER_COMPONENT( SyntyUnityImporter )
