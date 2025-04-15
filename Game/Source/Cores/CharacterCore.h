#pragma once
#include "ECS/Core.h"
#include "Components/Transform.h"
#include "Math/Random.h"
#include "Math/Vector2.h"

class AudioSource;
class Camera;
class Transform;
class CharacterController;

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

#if USING( ME_EDITOR )
    virtual void OnEditorInspect() override;
#endif

private:
    void HandleMouseLook( float dt );
    void HandlePortalShots();
    bool FirePortal( bool IsBluePortal );

    virtual void OnStart() override;

    float m_movementSpeed = 550.f;

    bool m_prevPrimaryFireDown = false;
    bool m_prevSecondaryFireDown = false;
    bool m_firstUpdate = true;

    float LookSensitivity = 20.f;
    AudioSource* m_orangePortalShot = nullptr;
    AudioSource* m_bluePortalShot = nullptr;
    std::vector<AudioSource*> m_invalidPortalSounds;
    Camera* m_camera = nullptr;
    Transform* m_playerTransform = nullptr;
    Transform* m_cameraTransform = nullptr;
    CharacterController* m_controller = nullptr;
    Random64 random;
    Vector2 previousMousePos;
    //DirectX::Mouse::State m_previousMouseState;
};

ME_REGISTER_CORE( CharacterCore )