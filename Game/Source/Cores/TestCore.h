#pragma once
#include "ECS/Core.h"
#include "Components/Transform.h"

class TestCore final
	: public Core<TestCore>
{
public:
	TestCore();
	~TestCore() {}

	virtual void OnEntityAdded(Entity& NewEntity) override;

	virtual void OnEntityRemoved(Entity& InEntity) override;

	virtual void OnEditorInspect() override;

	virtual void Update(float dt) override;

	virtual void Init() override;

};

ME_REGISTER_CORE(TestCore)