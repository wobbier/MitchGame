#pragma once
#include "ECS/Core.h"

// Drives every Character (Transform + Character + CharacterController) from the input actions:
// mouse / stick look with smoothing and a pitch clamp, action-relative movement through the
// controller's velocity model, jump, sprint (with an FOV push) and crouch (eye height), each
// transition eased over time. See Components/Character.h for the tunables.
class CharacterCore final
    : public Core<CharacterCore>
{
public:
    CharacterCore();
    ~CharacterCore() = default;

    virtual void Init() override;
    virtual void OnEntityAdded( Entity& NewEntity ) override;
    virtual void OnEntityRemoved( Entity& InEntity ) override;
    virtual void Update( const UpdateContext& inUpdateContext ) override;

private:
    virtual void OnStart() override;
};

ME_REGISTER_CORE( CharacterCore )
