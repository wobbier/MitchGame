#include "SplitScreenPlayerCore.h"
#include "Components/SplitScreenPlayer.h"
#include "Components/Transform.h"
#include "Components/Camera.h"
#include "Components/Physics/CharacterController.h"
#include "Engine/Engine.h"
#include "Engine/Input.h"
#include "ECS/EntityHandle.h"
#include <algorithm>

namespace
{
    struct PlayerKeys
    {
        KeyCode Forward, Back, Left, Right;
    };
    constexpr PlayerKeys kPlayerKeys[] = {
        { KeyCode::W, KeyCode::S, KeyCode::A, KeyCode::D },
        { KeyCode::I, KeyCode::K, KeyCode::J, KeyCode::L },
    };
    constexpr int kPlayerCount = static_cast<int>( std::size( kPlayerKeys ) );

    Camera* FindPlayerCamera( Entity& InPlayer )
    {
        Transform* cameraTransform = InPlayer.GetComponent<Transform>().GetChildByName( "Camera" );
        if( !cameraTransform || !cameraTransform->Parent || !cameraTransform->Parent->HasComponent<Camera>() )
        {
            return nullptr;
        }
        return &cameraTransform->Parent->GetComponent<Camera>();
    }
}


SplitScreenPlayerCore::SplitScreenPlayerCore()
    : Base( ComponentFilter().Requires<SplitScreenPlayer>().Requires<CharacterController>().Requires<Transform>() )
{
}


void SplitScreenPlayerCore::OnEntityAdded( Entity& InEntity )
{
    const int index = std::clamp( InEntity.GetComponent<SplitScreenPlayer>().PlayerIndex, 0, kPlayerCount - 1 );
    Camera* camera = FindPlayerCamera( InEntity );
    if( !camera )
    {
        return;
    }
    // Side by side: each player gets a vertical half of the screen. Player 0's camera is the main
    // one, so the other draws into its output.
    camera->Viewport = Vector4( index * 0.5f, 0.f, 0.5f, 1.f );
    if( index == 0 )
    {
        camera->SetCurrent();
    }
}


void SplitScreenPlayerCore::Update( const UpdateContext& InContext )
{
    Input& input = GetEngine().GetInput();
    const float dt = InContext.GetDeltaTime();
    for( Entity& entity : GetEntities() )
    {
        SplitScreenPlayer& player = entity.GetComponent<SplitScreenPlayer>();
        Transform& transform = entity.GetComponent<Transform>();
        CharacterController& controller = entity.GetComponent<CharacterController>();
        const PlayerKeys& keys = kPlayerKeys[std::clamp( player.PlayerIndex, 0, kPlayerCount - 1 )];

        const float turn = ( input.IsKeyDown( keys.Right ) ? 1.f : 0.f ) - ( input.IsKeyDown( keys.Left ) ? 1.f : 0.f );
        const float move = ( input.IsKeyDown( keys.Forward ) ? 1.f : 0.f ) - ( input.IsKeyDown( keys.Back ) ? 1.f : 0.f );
        if( turn != 0.f )
        {
            Vector3 euler = transform.GetRotationEuler();
            euler.y += turn * player.TurnSpeed * dt;
            transform.SetRotation( Vector3( 0.f, euler.y, 0.f ) );
        }
        Vector3 front = transform.Front();
        front.y = 0.f;
        controller.SetMoveInput( front.LengthSquared() > 0.f ? front.Normalized() * move : Vector3() );
    }
}
