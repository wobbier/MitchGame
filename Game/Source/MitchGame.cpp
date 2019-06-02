#include "MitchGame.h"
#include "Engine/Engine.h"
#include "ECS/Component.h"
#include "Engine/Clock.h"
#include "Components/Transform.h"
#include "ECS/Entity.h"
#include <string>
#include "Engine/Input.h"
#include "Components/Animation.h"
#include "Components/Camera.h"
#include "Components/Physics/Rigidbody.h"
#include "Components/Graphics/Model.h"
#include "Components/Lighting/Light.h"
#include "Components/FlyingCamera.h"

#include <memory>
#include "Engine/World.h"
#include "FilePath.h"
#include "Game.h"
#include "Cores/PhysicsCore.h"
#include "Cores/Cameras/FlyingCameraCore.h"

MitchGame::MitchGame()
	: Game()
{
	Physics = new PhysicsCore();
	FlyingCameraController = new FlyingCameraCore();
}

MitchGame::~MitchGame()
{
}

void MitchGame::OnStart()
{
	GetEngine().LoadScene("Assets/Alley.lvl");
	auto GameWorld = GetEngine().GetWorld().lock();

	MainCamera = GameWorld->CreateEntity();
	Transform& CameraPos = MainCamera.lock()->AddComponent<Transform>("Main Camera");
	CameraPos.SetPosition(glm::vec3(0, 5, 20));
	MainCamera.lock()->AddComponent<Camera>();
	MainCamera.lock()->AddComponent<FlyingCamera>();
	MainCamera.lock()->AddComponent<Light>();

	SecondaryCamera = GameWorld->CreateEntity();
	Transform& SecondaryPos = SecondaryCamera.lock()->AddComponent<Transform>("Secondary Camera");
	SecondaryPos.SetPosition(glm::vec3(0, 5, 20));
	SecondaryCamera.lock()->AddComponent<Camera>();
	SecondaryCamera.lock()->AddComponent<Light>();
	SecondaryCamera.lock()->AddComponent<FlyingCamera>();

	auto TestModel = GameWorld->CreateEntity();
	Transform& ModelTransform = TestModel.lock()->AddComponent<Transform>("Sponza");
	ModelTransform.SetPosition(glm::vec3(0.f, 0.f, 0.f));
	ModelTransform.SetScale(glm::vec3(.1f, .1f, .1f));
	//TestModel.lock()->AddComponent<Rigidbody>();
	//TestModel.lock()->AddComponent<Model>("Assets/ExampleAssets/Models/Hammer.fbx");
	TestModel.lock()->AddComponent<Model>("Assets/Cube3.fbx");

	GameWorld->AddCore<FlyingCameraCore>(*FlyingCameraController);
	GameWorld->AddCore<PhysicsCore>(*Physics);
}

void MitchGame::OnUpdate(float DeltaTime)
{
	Physics->Update(DeltaTime);

	FlyingCameraController->Update(DeltaTime);

	Input& Instance = Input::GetInstance();
	if (Instance.IsKeyDown(KeyCode::Number1))
	{
		MainCamera.lock()->GetComponent<Camera>().SetCurrent();
	}
	if (Instance.IsKeyDown(KeyCode::Number2))
	{
		SecondaryCamera.lock()->GetComponent<Camera>().SetCurrent();
	}
}

void MitchGame::OnEnd()
{
}

void MitchGame::OnInitialize()
{
}

void MitchGame::PostRender()
{
}