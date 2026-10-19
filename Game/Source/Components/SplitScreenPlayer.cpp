#include "SplitScreenPlayer.h"

ME_REFLECT_BEGIN( SplitScreenPlayer )
    ME_FIELD( PlayerIndex ).Display( "Player Index" ).Range( 0, 1 ).Tooltip( "0 = WASD, left half; 1 = IJKL, right half" );
    ME_FIELD( TurnSpeed ).Display( "Turn Speed (deg/s)" ).Range( 1.f, 720.f );
ME_REFLECT_END()


SplitScreenPlayer::SplitScreenPlayer()
    : Component( "SplitScreenPlayer" )
{
}


void SplitScreenPlayer::OnSerialize( json& outJson )
{
    Reflection::ToJson( StaticType(), this, outJson );
}


void SplitScreenPlayer::OnDeserialize( const json& inJson )
{
    Reflection::FromJson( StaticType(), this, inJson );
}
