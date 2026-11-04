#include "Character.h"

ME_REFLECT_BEGIN( Character )
    ME_FIELD( WalkSpeed ).Category( "Movement" ).Display( "Walk Speed (m/s)" ).Range( 0.f, 50.f );
    ME_FIELD( SprintMultiplier ).Category( "Movement" ).Range( 1.f, 5.f );
    ME_FIELD( CrouchMultiplier ).Category( "Movement" ).Range( 0.1f, 1.f );
    ME_FIELD( LookSensitivity ).Category( "Look" ).Range( 0.01f, 10.f ).Tooltip( "Degrees per Look unit from the mouse" );
    ME_FIELD( StickLookSpeed ).Category( "Look" ).Display( "Stick Look Speed (deg/s)" ).Range( 10.f, 720.f );
    ME_FIELD( LookSmoothing ).Category( "Look" ).Display( "Look Smoothing (s)" ).Range( 0.f, 0.5f ).Tooltip( "0 = raw input" );
    ME_FIELD( MaxPitch ).Category( "Look" ).Range( 0.f, 89.f );
    ME_FIELD( InvertY ).Category( "Look" );
    ME_FIELD( StandingEyeHeight ).Category( "Camera" ).Range( -2.f, 5.f ).Tooltip( "Metres above the capsule centre" );
    ME_FIELD( CrouchEyeHeight ).Category( "Camera" ).Range( -2.f, 5.f );
    ME_FIELD( CrouchTransitionSeconds ).Category( "Camera" ).Range( 0.f, 2.f );
    ME_FIELD( SprintFovBoost ).Category( "Camera" ).Range( 0.f, 40.f );
    ME_FIELD( FovTransitionSeconds ).Category( "Camera" ).Range( 0.f, 2.f );
ME_REFLECT_END()


Character::Character()
    : Component( "Character" )
{
}


void Character::OnSerialize( json& outJson )
{
    Reflection::ToJson( StaticType(), this, outJson );
}


void Character::OnDeserialize( const json& inJson )
{
    Reflection::FromJson( StaticType(), this, inJson );
}
