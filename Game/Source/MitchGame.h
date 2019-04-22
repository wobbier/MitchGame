#pragma once
#include <DirectXMath.h>
#include "Game.h"
#include <glm.hpp>
#include "Cores/FlyingCameraCore.h"

class MitchGame
	: public Game
{
public:
	MitchGame();
	virtual ~MitchGame() override;

	virtual void OnStart() override;

	virtual void OnUpdate(float DeltaTime) override;

	virtual void OnEnd() override;

	FlyingCameraCore* FlyingCameraController;

	WeakPtr<Entity> MainCamera;
	WeakPtr<Entity> SecondaryCamera;
};
