$input v_texcoord0, v_color0, v_viewPos, v_worldPos, v_particleData, v_particleVelocity

// Generated from Assets/ShaderGraphs/LaunchNight/PaperSheet.shadergraph by the shader graph compiler: edit the graph, not this file.
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
	vec4 sg_VertexColor = v_color0;
	float sg_ParticleRotation = v_particleData.x;
	vec3 sg_ParticleVelocity = v_particleVelocity;
	vec2 sg_ParticleQuadUV = v_particleData.zw;

	// Swizzle .xyz #24
	vec3 n24_Out = (sg_VertexColor).xyz;
	// Split #3
	vec2 n3_In = sg_ParticleQuadUV;
	// Multiply #11
	float n11_Out = n3_In.y * 22.0;
	// Fraction #12
	float n12_Out = fract(n11_Out);
	// Step #13
	float n13_Out = step(0.620000005, n12_Out);
	// Step #14
	float n14_Out = step(0.159999996, n3_In.y);
	// Multiply #15
	float n15_Out = n13_Out * n14_Out;
	// Step #16
	float n16_Out = step(n3_In.y, 0.720000029);
	// Step #17
	float n17_Out = step(0.25999999, n3_In.x);
	// Step #18
	float n18_Out = step(n3_In.x, 0.74000001);
	// Multiply #19
	float n19_Out = n17_Out * n18_Out;
	// Multiply #20
	float n20_Out = n16_Out * n19_Out;
	// Multiply #21
	float n21_Out = n15_Out * n20_Out;
	// Multiply #22
	float n22_Out = n21_Out * 0.550000012;
	// Subtract #23
	float n23_Out = 1.0 - n22_Out;
	// Multiply #25
	vec3 n25_Out = n24_Out * vec3_splat(n23_Out);
	// Step #4
	float n4_Out = step(0.180000007, n3_In.x);
	// Step #5
	float n5_Out = step(n3_In.x, 0.819999993);
	// Multiply #6
	float n6_Out = n4_Out * n5_Out;
	// Step #7
	float n7_Out = step(0.0799999982, n3_In.y);
	// Step #8
	float n8_Out = step(n3_In.y, 0.920000017);
	// Multiply #9
	float n9_Out = n7_Out * n8_Out;
	// Multiply #10
	float n10_Out = n6_Out * n9_Out;
	// Split #26
	vec4 n26_In = sg_VertexColor;
	// Multiply #27
	float n27_Out = n10_Out * n26_In.w;
	// Outputs
	vec3 sgOut_Color = n25_Out;
	float sgOut_Alpha = n27_Out;

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
