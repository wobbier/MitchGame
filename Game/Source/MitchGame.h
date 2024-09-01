#pragma once
#include "Game.h"
#include "Pointers.h"
#include "ECS/EntityHandle.h"

class MitchGame
    : public Game
{
public:
    MitchGame( int argc, char** argv );
    ~MitchGame();

    virtual void OnInitialize() override;

    virtual void OnStart() override;
    virtual void OnUpdate( const UpdateContext& inUpdateContext ) override;
    virtual void OnEnd() override;

    virtual void PostRender() override;

    class FlyingCameraCore* FlyingCameraController = nullptr;

    EntityHandle MainCamera;
    EntityHandle SecondaryCamera;
};