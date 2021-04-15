#pragma once
#include "ECS/Core.h"

class PhysicsTestCore
	: public Core<PhysicsTestCore>
{
public:
	static constexpr const char* kPrefabName = "Assets/Scene Cube.prefab";
	static constexpr const char* kPrefabName2 = "Assets/Scene Cube 2.prefab";
	static constexpr const char* kPrefabName3 = "Assets/Scene Cube 3.prefab";
	static constexpr const char* kPrefabName4 = "Assets/Scene Cube 4.prefab";

	PhysicsTestCore();
	virtual void OnEntityAdded(Entity& NewEntity) override;


	virtual void OnEntityRemoved(Entity& InEntity) override;

#if ME_EDITOR
	virtual void OnEditorInspect() override;
#endif

	virtual void Update(float dt) override;


	void OnEntityDestroyed(Entity& InEntity) override;

private:
	virtual void Init() override;

	virtual void OnStart() override;

	virtual void OnStop() override;

};

ME_REGISTER_CORE(PhysicsTestCore);