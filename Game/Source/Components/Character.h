#pragma once
#include "ECS/Component.h"
#include "ECS/ComponentDetail.h"

class Camera;
class Transform;

// A first-person character. CharacterCore reads the project's Move / Look / Jump / Sprint / Crouch
// input actions (Assets/Config/Input.inputactions: keyboard + mouse and gamepad), drives the
// entity's CharacterController and aims the child entity named "Camera". The tunables live here so
// each character (and each scene) can have its own; the runtime state is kept per entity too, so
// several characters can coexist (split screen, possession).
class Character
    : public Component<Character>
{
    ME_REFLECTABLE( Character )
public:
    Character();

    // Movement (metres per second; the controller's MaxSpeed follows these)
    float WalkSpeed = 4.f;
    float SprintMultiplier = 1.6f;
    float CrouchMultiplier = 0.5f;

    // Look
    float LookSensitivity = 1.f;        // degrees per Look unit (mouse: pixels × the binding's scale)
    float StickLookSpeed = 180.f;       // degrees per second at full stick deflection
    float LookSmoothing = 0.04f;        // seconds to settle; 0 = raw
    float MaxPitch = 85.f;              // degrees above / below the horizon
    bool InvertY = false;

    // Camera
    float StandingEyeHeight = 0.7f;     // metres above the capsule centre
    float CrouchEyeHeight = 0.2f;
    float CrouchTransitionSeconds = 0.15f;
    float SprintFovBoost = 8.f;         // degrees added to the camera FOV while sprinting
    float FovTransitionSeconds = 0.25f;

    // Per-entity runtime state owned by CharacterCore (not reflected, not saved).
    struct State
    {
        Camera* View = nullptr;
        Transform* CameraTransform = nullptr;
        float Yaw = 0.f;
        float Pitch = 0.f;
        float TargetYaw = 0.f;
        float TargetPitch = 0.f;
        float EyeHeight = 0.f;
        float BaseFov = 0.f;
        float Fov = 0.f;
        bool Crouching = false;
        bool Sprinting = false;
    };
    State Runtime;

private:
    void OnSerialize( json& outJson ) final;
    void OnDeserialize( const json& inJson ) final;
};

ME_REGISTER_COMPONENT( Character )
