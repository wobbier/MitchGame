#pragma once
#include "Game.h"
#include "Pointers.h"
#include "Engine/Engine.h"

class MitchGame
	: public Game
{
public:
	MitchGame(class Engine* engine);
	~MitchGame();

	virtual void OnInitialize() override;

	virtual void OnStart() override;
	virtual void OnUpdate(float DeltaTime) override;
	virtual void OnEnd() override;

	virtual void PostRender() override;

	class FlyingCameraCore* FlyingCameraController = nullptr;
	class PhysicsCore* Physics = nullptr;

	WeakPtr<Entity> MainCamera;
	WeakPtr<Entity> SecondaryCamera;

	class Engine* m_engine;
};

extern "C"
{
	__declspec(dllexport) Game* CreateGame(const char* gameName, Engine* engine);
	__declspec(dllexport) void DestroyGame(Game* game);
}
