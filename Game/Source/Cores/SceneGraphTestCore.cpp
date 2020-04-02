#include "SceneGraphTestCore.h"
#include "Components/Transform.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Mathf.h"

SceneGraphTestObject::SceneGraphTestObject()
	: Component("SceneGraphTestObject")
{
}

void SceneGraphTestObject::Init()
{
}

SceneGraphTestCore::SceneGraphTestCore()
	: Base(ComponentFilter().Requires<Transform>().Requires<SceneGraphTestObject>())
{

}

void SceneGraphTestCore::OnEntityAdded(Entity& NewEntity)
{
}

void SceneGraphTestCore::OnEntityRemoved(Entity& InEntity)
{
}

#if ME_EDITOR
void SceneGraphTestCore::OnEditorInspect()
{
}
#endif

void SceneGraphTestCore::Update(float dt)
{

	auto Entities = GetEntities();

	for (auto& ent : Entities)
	{
		Transform& transform = ent.GetComponent<Transform>();
		Vector3 rot = transform.GetRotation();
		rot.SetY(rot.Y() + (Mathf::Radians(10.0f * dt)));
		transform.SetRotation(rot);
	}
}

void SceneGraphTestCore::Init()
{
}

void SceneGraphTestCore::OnStart()
{
	auto world = GetEngine().GetWorld().lock();

	EntityHandle rootEnt = world->CreateFromPrefab(std::string(kPrefabName));
	Transform& rootTransform = rootEnt->GetComponent<Transform>();

	for (int i = 0; i < 10; ++i)
	{
		EntityHandle subEnt = world->CreateFromPrefab(std::string(kPrefabName2), &rootTransform);
		Transform& transform = subEnt->GetComponent<Transform>();
		transform.SetPosition(Vector3(((float)i - 4.5f) * 2.f, -3.f, 0.f));
		transform.SetScale(0.5f);

		for (int i = 0; i < 10; ++i)
		{
			EntityHandle sub2Ent = world->CreateFromPrefab(std::string(kPrefabName3), &transform);
			Transform& subTransform = sub2Ent->GetComponent<Transform>();
			subTransform.SetPosition(Vector3(((float)i - 4.5f) * 2.f, -3.f, 0.f));
			subTransform.SetScale(0.5f);

			for (int i = 0; i < 10; ++i)
			{
				EntityHandle sub3Ent = world->CreateFromPrefab(std::string(kPrefabName4), &subTransform);
				Transform& sub3Transform = sub3Ent->GetComponent<Transform>();
				sub3Transform.SetPosition(Vector3(((float)i - 4.5f) * 2.f, -3.f, 0.f));
				sub3Transform.SetScale(0.5f);
			}
		}
	}
}

void SceneGraphTestCore::OnStop()
{
}
