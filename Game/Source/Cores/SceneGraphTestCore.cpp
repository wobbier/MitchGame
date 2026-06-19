#include "SceneGraphTestCore.h"
#include "Components/Transform.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Mathf.h"
#include "optick.h"
#include "Work/Burst.h"
#include "Core/JobSystem.h"
#include "Work/SimpleJobSystem.h"
#include "Components/Graphics/Mesh.h"
#include "Graphics/Material.h"

#if USING( ME_EDITOR )
#include "imgui.h"
#endif

namespace
{
    Vector3 LevelColor( int level, float time )
    {
        float p = time + (float)level * 1.2f;
        return Vector3(
            sinf( p ) * 0.5f + 0.5f,
            sinf( p + 2.094f ) * 0.5f + 0.5f,
            sinf( p + 4.188f ) * 0.5f + 0.5f );
    }
}


SceneGraphTestObject::SceneGraphTestObject()
    : Component( "SceneGraphTestObject" )
{
}


void SceneGraphTestObject::Init()
{
}


void SceneGraphTestObject::OnSerialize( json& outJson )
{
}


void SceneGraphTestObject::OnDeserialize( const json& inJson )
{
}


SceneGraphTestCore::SceneGraphTestCore()
    : Base( ComponentFilter().Requires<Transform>().Requires<SceneGraphTestObject>() )
{

}


void SceneGraphTestCore::OnEntityAdded( Entity& NewEntity )
{
}


void SceneGraphTestCore::OnEntityRemoved( Entity& InEntity )
{
}


#if USING( ME_EDITOR )
void SceneGraphTestCore::OnEditorInspect()
{
    Base::OnEditorInspect();

    ImGui::Checkbox( "Animate (rotate transforms)", &m_animate );
    ImGui::Checkbox( "Animate Color (per level)", &m_animateColor );
    ImGui::Text( "Entities: %zu", GetEntities().size() );
}
#endif


void SceneGraphTestCore::Update( const UpdateContext& inUpdateContext )
{
    OPTICK_CATEGORY( "SceneGraphTestCore::Update", Optick::Category::GameLogic );

    if( !m_animate && !m_animateColor )
    {
        return;
    }

    auto& Entities = GetEntities();

    SimpleJobSystem& jobSystem = inUpdateContext.GetSystem<Engine>()->GetJobSystem();

    std::vector<std::pair<int, int>> batches;
    Burst::GenerateChunks( Entities.size(), jobSystem.GetNumWorkers()*2, batches );

    const float dt = inUpdateContext.GetDeltaTime();
    const float time = inUpdateContext.GetTotalTime();

    constexpr int kMaxLevels = 5;
    Vector3 levelColors[kMaxLevels];
    for( int lvl = 0; lvl < kMaxLevels; ++lvl )
    {
        levelColors[lvl] = LevelColor( lvl, time );
    }

    const bool rotate = m_animate;
    const bool recolor = m_animateColor;
    for( auto& batch : batches )
    {
        OPTICK_CATEGORY( "Burst::BatchAdd", Optick::Category::Debug );
        int batchBegin = batch.first;
        int batchEnd = batch.second;
        auto job = [dt, &Entities, batchBegin, batchEnd, rotate, recolor, &levelColors]()
            {
                OPTICK_CATEGORY( "B::Job", Optick::Category::Debug );

                for( int entIndex = batchBegin; entIndex < batchEnd; ++entIndex )
                {
                    auto& InEntity = Entities[entIndex];

                    if( rotate )
                    {
                        Transform& transform = InEntity.GetComponent<Transform>();
                        transform.Rotate( { 0.f, 1.0f * dt, 0.f }, TransformSpace::Self );
                    }

                    if( recolor && InEntity.HasComponent<Mesh>() )
                    {
                        Mesh& mesh = InEntity.GetComponent<Mesh>();
                        if( mesh.MeshMaterial )
                        {
                            int lvl = InEntity.GetComponent<SceneGraphTestObject>().Level;
                            lvl = ( lvl < 0 ) ? 0 : ( lvl >= kMaxLevels ? kMaxLevels - 1 : lvl );
                            mesh.MeshMaterial->DiffuseColor = levelColors[lvl];
                        }
                    }
                }
            };

        jobSystem.submit( job );
    }
    jobSystem.waitForAllJobs();
}


void SceneGraphTestCore::OnEntityDestroyed( Entity& InEntity )
{
}


void SceneGraphTestCore::Init()
{
}


void SceneGraphTestCore::OnStart()
{
    auto world = GetEngine().GetWorld().lock();

    constexpr int kLevel1Count = 16;
    constexpr int kLevel2Count = 16;
    constexpr int kLevel3Count = 15;
    constexpr int kLevel4Count = 14;

    auto rowOffset = []( int index, int count )
        {
            return ( (float)index - ( (float)count - 1.f ) * 0.5f ) * 2.f;
        };

    EntityHandle rootEnt = world->CreateFromPrefab( std::string( kPrefabName ) );
    Transform& rootTransform = rootEnt->GetComponent<Transform>();
    rootEnt->GetComponent<SceneGraphTestObject>().Level = 0;

    for( int i = 0; i < kLevel1Count; ++i )
    {
        EntityHandle subEnt = world->CreateFromPrefab( std::string( kPrefabName2 ), &rootTransform );
        Transform& transform = subEnt->GetComponent<Transform>();
        transform.SetPosition( Vector3( rowOffset( i, kLevel1Count ), -3.f, 0.f ) );
        transform.SetScale( 0.5f );
        subEnt->GetComponent<SceneGraphTestObject>().Level = 1;

        for( int j = 0; j < kLevel2Count; ++j )
        {
            EntityHandle sub2Ent = world->CreateFromPrefab( std::string( kPrefabName3 ), &transform );
            Transform& subTransform = sub2Ent->GetComponent<Transform>();
            subTransform.SetPosition( Vector3( rowOffset( j, kLevel2Count ), -3.f, 0.f ) );
            subTransform.SetScale( 0.5f );
            sub2Ent->GetComponent<SceneGraphTestObject>().Level = 2;

            for( int k = 0; k < kLevel3Count; ++k )
            {
                EntityHandle sub3Ent = world->CreateFromPrefab( std::string( kPrefabName4 ), &subTransform );
                Transform& sub3Transform = sub3Ent->GetComponent<Transform>();
                sub3Transform.SetPosition( Vector3( rowOffset( k, kLevel3Count ), -3.f, 0.f ) );
                sub3Transform.SetScale( 0.5f );
                sub3Ent->GetComponent<SceneGraphTestObject>().Level = 3;

                for( int l = 0; l < kLevel4Count; ++l )
                {
                    EntityHandle sub4Ent = world->CreateFromPrefab( std::string( kPrefabName4 ), &sub3Transform );
                    Transform& sub4Transform = sub4Ent->GetComponent<Transform>();
                    sub4Transform.SetPosition( Vector3( rowOffset( l, kLevel4Count ), -3.f, 0.f ) );
                    sub4Transform.SetScale( 0.5f );
                    sub4Ent->GetComponent<SceneGraphTestObject>().Level = 4;
                }
            }
        }
    }
}


void SceneGraphTestCore::OnStop()
{
}
