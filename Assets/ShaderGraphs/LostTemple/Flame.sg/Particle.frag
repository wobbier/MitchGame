$input v_texcoord0, v_color0, v_viewPos, v_worldPos, v_particleData, v_particleVelocity

// Generated from Assets/ShaderGraphs/LostTemple/Flame.shadergraph by the shader graph compiler: edit the graph, not this file.
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
// u_sgParams[0]: Core Color (Vector 3)
// u_sgParams[1]: Edge Color (Vector 3)
// u_sgParams[2]: Rise Speed (Float)


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
	vec4 sg_VertexColor = v_color0;
	float sg_ParticleRotation = v_particleData.x;
	vec3 sg_ParticleVelocity = v_particleVelocity;
	vec2 sg_ParticleQuadUV = v_particleData.zw;

	// Negate #6
	float n6_Out = -u_sgParams[2].x;
	// Combine #7
	vec4 n7_RGBA = vec4(0.0, n6_Out, 0.0, 1.0);
	// Panner #8
	vec2 n8_Out = sg_ParticleQuadUV + n7_RGBA.xy * sg_Time;
	// Gradient Noise #9
	float n9_Out = sgGradientNoise(n8_Out, 4.5);
	// Subtract #10
	float n10_Out = n9_Out - 0.5;
	// Multiply #11
	float n11_Out = n10_Out * 0.159999996;
	// Add #12
	vec2 n12_Out = sg_ParticleQuadUV + vec2_splat(n11_Out);
	// Sample Texture 2D #14
	vec4 n14_RGBA = toLinear(texture2D(sgParticleTexture, n12_Out));
	// Split #15
	vec2 n15_In = sg_ParticleQuadUV;
	// One Minus #16
	float n16_Out = 1.0 - n15_In.y;
	// Multiply #17
	float n17_Out = n14_RGBA.x * n16_Out;
	// Smoothstep #18
	float n18_Out = smoothstep(0.25, 0.949999988, n17_Out);
	// Lerp #19
	vec3 n19_Out = mix(u_sgParams[1].xyz, u_sgParams[0].xyz, vec3_splat(n18_Out));
	// Swizzle .xyz #20
	vec3 n20_Out = (sg_VertexColor).xyz;
	// Multiply #21
	vec3 n21_Out = n19_Out * n20_Out;
	// Split #22
	vec4 n22_In = sg_VertexColor;
	// Multiply #23
	float n23_Out = n14_RGBA.w * n22_In.w;
	// Remap #24
	float n24_Out = 0.550000012 + (n9_Out - 0.0) * (1.39999998 - 0.550000012) / (1.0 - 0.0);
	// Multiply #25
	float n25_Out = n23_Out * n24_Out;
	// Saturate #26
	float n26_Out = clamp(n25_Out, 0.0, 1.0);
	// Outputs
	vec3 sgOut_Color = n21_Out;
	float sgOut_Alpha = n26_Out;

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
