#include "CharacterCore.h"
#include "Components/Character.h"
#include "Components/Camera.h"
#include "Components/Physics/CharacterController.h"
#include "Components/Transform.h"
#include "ECS/EntityHandle.h"
#include "Engine/Engine.h"
#include "Engine/Input.h"
#include "Input/InputTypes.h"
#include "CLog.h"
#include "Mathf.h"
#include "Reflection/Reflection.h"
#include "JSON.h"
#include "optick.h"
#include <cmath>

namespace
{
    // Frame-rate independent exponential ease: covers ~63% of the gap every InSeconds.
    float Approach( float InCurrent, float InTarget, float InSeconds, float InDeltaTime )
    {
        if( InSeconds <= 0.f )
        {
            return InTarget;
        }
        return InCurrent + ( InTarget - InCurrent ) * ( 1.f - std::exp( -InDeltaTime / InSeconds ) );
    }


    // Finds the child entity named "Camera" and caches its Camera / Transform on the state.
    bool BindCamera( Entity& InEntity, Character& InCharacter )
    {
        Transform* cameraTransform = InEntity.GetComponent<Transform>().GetChildByName( "Camera" );
        if( !cameraTransform || !cameraTransform->Parent || !cameraTransform->Parent->HasComponent<Camera>() )
        {
            return false;
        }
        Character::State& state = InCharacter.Runtime;
        state.View = &cameraTransform->Parent->GetComponent<Camera>();
        state.CameraTransform = cameraTransform;
        state.Pitch = state.TargetPitch = Mathf::Clamp( -InCharacter.MaxPitch, InCharacter.MaxPitch, cameraTransform->GetRotationEuler().x );
        state.EyeHeight = cameraTransform->GetPosition().y;
        // The projection reads the camera's (private) field of view, not the hidden legacy Zoom field.
        state.BaseFov = state.Fov = state.View->GetFOV();
        return true;
    }


    Vector3 Flattened( Vector3 InDirection )
    {
        InDirection.y = 0.f;
        return InDirection.LengthSquared() > 1e-6f ? InDirection.Normalized() : Vector3();
    }
}


CharacterCore::CharacterCore()
    : Base( ComponentFilter().Requires<Transform>().Requires<Character>().Requires<CharacterController>() )
{
}


void CharacterCore::Init()
{
}


void CharacterCore::OnEntityAdded( Entity& NewEntity )
{
    Character& character = NewEntity.GetComponent<Character>();
    character.Runtime = Character::State();
    // The heading from the facing direction, not an Euler decomposition (which folds |yaw| > 90).
    const Vector3 front = NewEntity.GetComponent<Transform>().Front();
    character.Runtime.Yaw = character.Runtime.TargetYaw = Mathf::Degrees( std::atan2( front.x, front.z ) );
    if( !BindCamera( NewEntity, character ) )
    {
        YIKES( "Character '" + NewEntity.GetComponent<Transform>().GetName() + "' has no child entity named 'Camera' with a Camera; it will look for one each frame." );
    }
}


void CharacterCore::OnEntityRemoved( Entity& InEntity )
{
    if( InEntity.HasComponent<Character>() )
    {
        InEntity.GetComponent<Character>().Runtime = Character::State();
    }
}


void CharacterCore::OnStart()
{
    if( !GetEntities().empty() )
    {
        GetEngine().GetInput().SetMouseCapture( true );
    }
}


void CharacterCore::Update( const UpdateContext& inUpdateContext )
{
    OPTICK_EVENT( "CharacterCore::Update" );
    const float dt = inUpdateContext.GetDeltaTime();
    Input& input = GetEngine().GetInput();
    const Vector2 move = input.GetAction( "Move" ).GetVector2();
    const Vector2 look = input.GetAction( "Look" ).GetVector2();
    const bool jump = input.GetAction( "Jump" ).WasPressed();
    const bool sprint = input.GetAction( "Sprint" ).IsPressed();
    const bool crouch = input.GetAction( "Crouch" ).IsPressed();
    // A mouse delta is already "per frame"; a stick is a rate and needs the frame time.
    const bool stickLook = input.IsGamepadConnected() && input.GetGamepadStick( GamepadStick::Right ).Length() > 0.01f;

    for( Entity& entity : GetEntities() )
    {
        Character& character = entity.GetComponent<Character>();
        Character::State& state = character.Runtime;
        if( !state.View && !BindCamera( entity, character ) )
        {
            continue;
        }
        Transform& transform = entity.GetComponent<Transform>();
        CharacterController& controller = entity.GetComponent<CharacterController>();

        // Look: yaw on the body, pitch on the camera, both eased towards the raw target.
        Vector2 degrees = stickLook ? look * ( character.StickLookSpeed * dt ) : look * character.LookSensitivity;
        if( character.InvertY )
        {
            degrees.y = -degrees.y;
        }
        state.TargetYaw += degrees.x;
        state.TargetPitch = Mathf::Clamp( -character.MaxPitch, character.MaxPitch, state.TargetPitch - degrees.y );
        state.Yaw = Approach( state.Yaw, state.TargetYaw, character.LookSmoothing, dt );
        state.Pitch = Approach( state.Pitch, state.TargetPitch, character.LookSmoothing, dt );
        transform.SetRotation( Vector3( 0.f, state.Yaw, 0.f ) );

        // Movement relative to where the body faces; the controller owns acceleration and gravity.
        const Vector3 direction = Flattened( transform.Front() ) * move.y + Flattened( transform.Right() ) * move.x;
        const float magnitude = direction.Length();
        const Vector3 moveInput = magnitude > 1.f ? direction / magnitude : direction;
        state.Crouching = crouch;
        state.Sprinting = sprint && !crouch && move.y > 0.1f;
        const float speedScale = state.Sprinting ? character.SprintMultiplier : ( state.Crouching ? character.CrouchMultiplier : 1.f );
        controller.MaxSpeed = character.WalkSpeed * speedScale;
        controller.SetMoveInput( moveInput );
        if( jump && !state.Crouching )
        {
            DBG( "Character '" + transform.GetName() + "': jump requested (grounded " + std::string( controller.IsOnGround() ? "yes" : "no" ) + ")" );
            controller.Jump();
        }

        // Camera: eye height and FOV ease between their standing / crouching / sprinting values.
        state.EyeHeight = Approach( state.EyeHeight, state.Crouching ? character.CrouchEyeHeight : character.StandingEyeHeight, character.CrouchTransitionSeconds, dt );
        state.Fov = Approach( state.Fov, state.BaseFov + ( state.Sprinting ? character.SprintFovBoost : 0.f ), character.FovTransitionSeconds, dt );
        state.CameraTransform->SetPosition( Vector3( 0.f, state.EyeHeight, 0.f ) );
        state.CameraTransform->SetRotation( Vector3( state.Pitch, 0.f, 0.f ) );
        if( std::abs( state.View->GetFOV() - state.Fov ) > 1e-3f )
        {
            Reflection::SetPathJson( Camera::StaticType(), state.View, "FieldOfView", json( state.Fov ) );
        }
    }
}
