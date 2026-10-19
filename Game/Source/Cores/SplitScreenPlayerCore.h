#pragma once
#include "ECS/Core.h"

// Two local players, each with a CharacterController and a child camera named "Camera". Player 0
// moves with WASD and sees the left half of the screen, player 1 IJKL and the right half.
class SplitScreenPlayerCore final
    : public Core<SplitScreenPlayerCore>
{
public:
    SplitScreenPlayerCore();

    void OnEntityAdded( Entity& InEntity ) final;
    void Update( const UpdateContext& InContext ) final;
};

ME_REGISTER_CORE( SplitScreenPlayerCore )
