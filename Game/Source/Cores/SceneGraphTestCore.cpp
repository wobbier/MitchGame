#include "SceneGraphTestCore.h"
#include "Components/Transform.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Mathf.h"
#include "optick.h"
#include "Work/Burst.h"

SceneGraphTestObject::SceneGraphTestObject()
	: Component("SceneGraphTestObject")
{
}

void SceneGraphTestObject::Init()
{
}

void SceneGraphTestObject::OnSerialize(json& outJson)
{
}

void SceneGraphTestObject::OnDeserialize(const json& inJson)
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
	Base::OnEditorInspect();
}
#endif

void SceneGraphTestCore::Update(float dt)
{
	OPTICK_CATEGORY("SceneGraphTestCore::Update", Optick::Category::GameLogic);

	auto& Entities = GetEntities();


	{
		{

			//Transform* CurrentTransform = GetRootTransform();
			//for (const SharedPtr<Transform>& Child : CurrentTransform->GetChildren())
			//{
			//	OPTICK_EVENT("SceneGraph::GetChildren");
			//	if (Child->IsDirty())
			//	{
			//		//Job* job = pool.CreateClosureJobAsChild([&Child, CurrentTransform](Job& job) {
			//		OPTICK_CATEGORY("Update Transform", Optick::Category::Scene);
			//		glm::mat4 model = glm::mat4(1.f);
			//		model = glm::translate(model, Child->GetPosition().InternalVector);
			//		model = glm::rotate(model, Child->GetWorldRotation().ToAngle(), Child->GetWorldRotation().ToAxis().InternalVector);
			//		model = glm::scale(model, Child->GetScale().InternalVector);

			//		Matrix4 xxx = model * CurrentTransform->WorldTransform.GetInternalMatrix();
			//		Child->SetWorldTransform(xxx);
			//		if (!Child->GetChildren().empty())
			//		{
			//			UpdateRecursively(Child.get(), true, nullptr, true);// *job);
			//		}
			//		//}, rootJob);
			//		//worker->Submit(job);
			//	}
			//}
		}

	}
	auto [worker, pool] = GetEngine().GetJobSystemNew();

	std::vector<std::pair<int, int>> batches;
	Burst::GenerateChunks(Entities.size(), 30, batches);

	Job* rootJob = worker->GetPool().CreateClosureJob([](Job& job) {
	});

	for (auto& batch : batches)
	{
		OPTICK_CATEGORY("Burst::BatchAdd", Optick::Category::Debug);
		int batchBegin = batch.first;
		int batchEnd = batch.second;
		int batchSize = batchEnd - batchBegin;

		Job* job = worker->GetPool().CreateClosureJobAsChild([this, &Entities, batchBegin, batchEnd, dt](Job& job) {
			OPTICK_CATEGORY("B::Job", Optick::Category::Debug);

			for (int entIndex = batchBegin; entIndex < batchEnd; ++entIndex)
			{
				auto& InEntity = Entities[entIndex];
				OPTICK_CATEGORY("Update Rotation", Optick::Category::Debug);
				Transform& transform = InEntity.GetComponent<Transform>();
				{
					OPTICK_CATEGORY("Update Rotation Vector", Optick::Category::Debug);
					transform.Rotate({0.f, 1.0f * dt, 0.f}, TransformSpace::Self);
				}
			}
		}, rootJob);
		worker->Submit(job);

	}
	worker->Submit(rootJob);
	worker->Wait(rootJob);

}

void SceneGraphTestCore::OnEntityDestroyed(Entity& InEntity)
{
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

		for (int j = 0; j < 10; ++j)
		{
			EntityHandle sub2Ent = world->CreateFromPrefab(std::string(kPrefabName3), &transform);
			Transform& subTransform = sub2Ent->GetComponent<Transform>();
			subTransform.SetPosition(Vector3(((float)j - 4.5f) * 2.f, -3.f, 0.f));
			subTransform.SetScale(0.5f);

			for (int k = 0; k < 10; ++k)
			{
				EntityHandle sub3Ent = world->CreateFromPrefab(std::string(kPrefabName4), &subTransform);
				Transform& sub3Transform = sub3Ent->GetComponent<Transform>();
				sub3Transform.SetPosition(Vector3(((float)k - 4.5f) * 2.f, -3.f, 0.f));
				sub3Transform.SetScale(0.5f);
			}
		}
	}
}

void SceneGraphTestCore::OnStop()
{
}
