$input v_texcoord0, v_color0, v_viewPos, v_worldPos, v_particleData, v_particleVelocity

// Generated from Assets/ShaderGraphs/LostTemple/SpiritWisp.shadergraph by the shader graph compiler: edit the graph, not this file.
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
// u_sgParams[0]: Swirl Speed (Float)
// u_sgParams[1]: Core Tightness (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	float particleZ = v_viewPos.z;
	float sceneZ = sgSceneDepth(gl_FragCoord.xy * u_viewTexel.xy);
	if (sceneZ <= particleZ)
	{
		discard;
	}
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;
	vec4 sg_VertexColor = v_color0;
	float sg_ParticleRotation = v_particleData.x;
	vec3 sg_ParticleVelocity = v_particleVelocity;
	vec2 sg_ParticleQuadUV = v_particleData.zw;

	// Swizzle .xyz #29
	vec3 n29_Out = (sg_VertexColor).xyz;
	// Subtract #5
	vec2 n5_Out = sg_ParticleQuadUV - vec2(0.5, 0.5);
	// Length #6
	float n6_Out = length(n5_Out);
	// Multiply #7
	float n7_Out = n6_Out * 2.0;
	// Square #8
	float n8_Out = n7_Out * n7_Out;
	// Multiply #9
	float n9_Out = n8_Out * u_sgParams[1].x;
	// Negate #10
	float n10_Out = -n9_Out;
	// Exponential #11
	float n11_Out = exp(n10_Out);
	// Multiply #26
	float n26_Out = n11_Out * 3.0;
	// Polar Coordinates #12
	vec2 n12_Out = sgPolarCoordinates(sg_ParticleQuadUV, vec2(0.5, 0.5), 1.0, 1.0);
	// Multiply #14
	float n14_Out = u_sgParams[0].x * (-0.600000024);
	// Multiply #15
	float n15_Out = sg_Time * n14_Out;
	// Multiply #17
	float n17_Out = sg_Time * u_sgParams[0].x;
	// Combine #18
	vec4 n18_RGBA = vec4(n15_Out, n17_Out, 0.0, 1.0);
	// Add #19
	vec2 n19_Out = n12_Out + n18_RGBA.xy;
	// Gradient Noise #20
	float n20_Out = sgGradientNoise(n19_Out, 5.0);
	// Smoothstep #21
	float n21_Out = smoothstep(0.400000006, 0.850000024, n20_Out);
	// Smoothstep #22
	float n22_Out = smoothstep(0.150000006, 1.0, n7_Out);
	// One Minus #23
	float n23_Out = 1.0 - n22_Out;
	// Multiply #24
	float n24_Out = n21_Out * n23_Out;
	// Multiply #27
	float n27_Out = n24_Out * 1.39999998;
	// Add #28
	float n28_Out = n26_Out + n27_Out;
	// Multiply #30
	vec3 n30_Out = n29_Out * vec3_splat(n28_Out);
	// Multiply #31
	float n31_Out = n24_Out * 0.600000024;
	// Add #32
	float n32_Out = n11_Out + n31_Out;
	// Saturate #33
	float n33_Out = clamp(n32_Out, 0.0, 1.0);
	// Split #25
	vec4 n25_In = sg_VertexColor;
	// Multiply #34
	float n34_Out = n33_Out * n25_In.w;
	// Outputs
	vec3 sgOut_Color = n30_Out;
	float sgOut_Alpha = n34_Out;

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
