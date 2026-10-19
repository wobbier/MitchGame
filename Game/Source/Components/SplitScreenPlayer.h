#pragma once
#include "ECS/Component.h"
#include "ECS/ComponentDetail.h"

// A local split screen player: SplitScreenPlayerCore drives its CharacterController from the keyboard
// (player 0: WASD, player 1: IJKL; forward/back and turn) and gives its child "Camera" this player's
// half of the screen.
class SplitScreenPlayer
    : public Component<SplitScreenPlayer>
{
    ME_REFLECTABLE( SplitScreenPlayer )
public:
    SplitScreenPlayer();

    int PlayerIndex = 0;
    float TurnSpeed = 120.f;    // degrees/s

private:
    void OnSerialize( json& outJson ) final;
    void OnDeserialize( const json& inJson ) final;
};
ME_REGISTER_COMPONENT( SplitScreenPlayer )
