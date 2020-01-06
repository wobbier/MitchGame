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
#include "Components/Cameras/FlyingCamera.h"
#include "Cores/TestCore.h"
#include <memory>
#include "Engine/World.h"
#include "Path.h"
#include "Game.h"
#include "Cores/PhysicsCore.h"
#include "Cores/Cameras/FlyingCameraCore.h"

MitchGame::MitchGame()
	: Game()
{
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
	CameraPos.SetPosition(Vector3(0, 5, 20));
	Camera& cam = MainCamera.lock()->AddComponent<Camera>();
	MainCamera.lock()->AddComponent<FlyingCamera>();
	MainCamera.lock()->AddComponent<Light>();

	SecondaryCamera = GameWorld->CreateEntity();
	Transform& SecondaryPos = SecondaryCamera.lock()->AddComponent<Transform>("Secondary Camera");
	SecondaryPos.SetPosition(Vector3(0, 5, 20));
	SecondaryCamera.lock()->AddComponent<Camera>();
	SecondaryCamera.lock()->AddComponent<Light>();
	SecondaryCamera.lock()->AddComponent<FlyingCamera>();

	auto TestModel = GameWorld->CreateEntity();
	Transform& ModelTransform = TestModel.lock()->AddComponent<Transform>("Sponza");
	ModelTransform.SetPosition(Vector3(0.f, 0.f, 0.f));
	ModelTransform.SetScale(Vector3(.1f, .1f, .1f));
	//TestModel.lock()->AddComponent<Rigidbody>();
	//TestModel.lock()->AddComponent<Model>("Assets/ExampleAssets/Models/Hammer.fbx");
	TestModel.lock()->AddComponent<Model>("Assets/Craftsman/Craftsman.fbx");

	FlyingCameraController->SetCamera(&cam);
	GameWorld->AddCore<FlyingCameraCore>(*FlyingCameraController);
}

void MitchGame::OnUpdate(float DeltaTime)
{
	FlyingCameraController->Update(DeltaTime);

	Input& Instance = Input::GetInstance();
	if (Instance.GetKeyboardState().NumPad1)
	{
		MainCamera.lock()->GetComponent<Camera>().SetCurrent();
	}
	if (Instance.GetKeyboardState().NumPad2)
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