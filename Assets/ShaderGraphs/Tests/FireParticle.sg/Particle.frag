$input v_texcoord0, v_color0, v_viewPos, v_worldPos, v_particleData, v_particleVelocity

// Generated from Assets/ShaderGraphs/Tests/FireParticle.shadergraph by the shader graph compiler: edit the graph, not this file.
// Pairs with the engine's Particle.vert; behaves like Particle.frag around the graph's colour:
// manual depth test, soft fade, optional volume lighting, fog, premultiplied additive blending.
#define SG_TARGET_PARTICLE 1

#include "Common.sh"
#include "Lighting.sh"
#include "Fog.sh"
#include "ShaderGraph/SGLib.sh"

SAMPLER2D(s_sgParticleTexture, 6);
SAMPLER2D(s_sgSceneDepth, 7);
#define sgParticleTexture s_sgParticleTexture

uniform vec4 u_particleParams;   // z softness (view-space distance)
uniform vec4 u_particleParams2;  // y 1 = additive (premultiply), z 1 = lit by the scene's lights
uniform vec4 u_particleDepth;    // x P[2][2], y P[3][2], z orthographic, w depth range -1..1

// Linear view depth of the opaque scene under a screen UV.
float sgSceneDepth(vec2 _uv)
{
	float d = texture2DLod(s_sgSceneDepth, _uv, 0.0).r;
	float ndc = u_particleDepth.w > 0.5 ? d * 2.0 - 1.0 : d;
	if (u_particleDepth.z > 0.5)
	{
		return (ndc - u_particleDepth.y) / u_particleDepth.x;
	}
	return u_particleDepth.y / (ndc - u_particleDepth.x);
}

uniform vec4 u_sgParams[16];


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	float particleZ = v_viewPos.z;
	float sceneZ = sgSceneDepth(gl_FragCoord.xy * u_viewTexel.xy);
	if (sceneZ <= particleZ)
	{
		discard;
	}
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	vec4 sg_VertexColor = v_color0;
	float sg_ParticleRotation = v_particleData.x;
	vec3 sg_ParticleVelocity = v_particleVelocity;
	vec2 sg_ParticleQuadUV = v_particleData.zw;

	// Sample Texture 2D #3
	vec4 n3_RGBA = toLinear(texture2D(sgParticleTexture, sg_UV0));
	// Multiply #8
	vec4 n8_Out = vec4(n3_RGBA.xyz, 1.0) * sg_VertexColor;
	// Panner #5
	vec2 n5_Out = sg_ParticleQuadUV + vec2(0.0, -1.60000002) * sg_Time;
	// Gradient Noise #6
	float n6_Out = sgGradientNoise(n5_Out, 5.0);
	// Remap #7
	float n7_Out = 0.400000006 + (n6_Out - 0.0) * (1.60000002 - 0.400000006) / (1.0 - 0.0);
	// Multiply #9
	vec4 n9_Out = n8_Out * vec4_splat(n7_Out);
	// Split #10
	vec4 n10_In = sg_VertexColor;
	// Multiply #11
	float n11_Out = n3_RGBA.w * n10_In.w;
	// Multiply #12
	float n12_Out = n11_Out * n6_Out;
	// Outputs
	vec3 sgOut_Color = (n9_Out).xyz;
	float sgOut_Alpha = n12_Out;

	vec4 color = vec4(sgOut_Color, sgOut_Alpha);
	if (u_particleParams.z > 0.0)
	{
		color.a *= clamp((sceneZ - particleZ) / u_particleParams.z, 0.0, 1.0);
	}
	if (color.a < 0.002)
	{
		discard;
	}
	if (u_particleParams2.z > 0.5)
	{
		color.rgb *= volumeLighting(v_worldPos, gl_FragCoord.xy, particleZ);
	}
	vec3 sunColor = u_lightParams.x > 0.5 ? directionalRadiance(0, v_worldPos) : vec3_splat(0.0);
	vec4 fog = fogForward(mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz, v_worldPos, sunColor, u_dirLightDirection[0].xyz);
	color.rgb = u_particleParams2.y > 0.5 ? color.rgb * fog.a : color.rgb * fog.a + fog.rgb;
	gl_FragColor = u_particleParams2.y > 0.5 ? vec4(color.rgb * color.a, color.a) : color;
}
