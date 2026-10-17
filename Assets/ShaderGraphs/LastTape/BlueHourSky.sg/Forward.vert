$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LastTape/BlueHourSky.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];

void sgCustom_LastLightOfSummer_62630(vec3 View, out vec3 Color)
{
vec3 direction = -View;
float elevation = clamp(direction.y,0.0,1.0);
vec3 dusk = mix(vec3(.075,.055,.12),vec3(.008,.019,.055),pow(elevation,.45));
vec2 spherical = vec2(atan2(direction.z,direction.x)/6.2831853+.5,asin(direction.y)/3.14159265+.5);
vec2 cell = floor(spherical*vec2(650.0,325.0));
vec2 within = fract(spherical*vec2(650.0,325.0))-vec2_splat(.5);
float seed = fract(sin(dot(cell,vec2(12.9898,78.233)))*43758.5453);
float stars = step(.996,seed)*(1.0-smoothstep(.02,.14,length(within)))*smoothstep(.05,.4,elevation);
vec3 moonDirection = normalize(vec3(.15,.32,.94));
float separation = length(direction-moonDirection);
float moon = 1.0-smoothstep(.017,.018,separation);
float halo = exp(-separation*38.0)*.03;
float haze = sgValueNoise(spherical*vec2(34.0,100.0),1.0)*(1.0-smoothstep(.0,.4,elevation))*.009;
Color = dusk + vec3_splat(stars*.28+halo+haze) + vec3(.62,.71,.79)*moon;
}


void main()
{
	// Instanced: the model matrix comes from the instance buffer (and the bone palette when skinned).
	mat4 sg_model = mtxFromCols(i_data0, i_data1, i_data2, i_data3);
#if SG_SKINNED
	sg_model = mul(sg_model, skinMatrix(a_indices, a_weight));
#endif
	mat3 sg_normalMatrix = cofactor(sg_model);


	// Outputs
	vec3 sgOut_PositionOffset = vec3(0.0, 0.0, 0.0);

	vec3 objectPos = a_position;
#if SG_OFFSET_WORLD
	vec3 worldPos = mul(sg_model, vec4(a_position, 1.0)).xyz + sgOut_PositionOffset;
#else
	objectPos += sgOut_PositionOffset;
	vec3 worldPos = mul(sg_model, vec4(objectPos, 1.0)).xyz;
#endif
	gl_Position = mul(u_viewProj, vec4(worldPos, 1.0));

	v_normal = mul(sg_normalMatrix, a_normal);
	v_tangent = mul(sg_model, vec4(a_tangent, 0.0)).xyz;
	v_bitangent = mul(sg_model, vec4(a_bitangent, 0.0)).xyz;
	v_worldPos = worldPos;
	v_viewPos = mul(u_view, vec4(worldPos, 1.0));
	v_texcoord0 = a_texcoord0;
	v_objectPos = objectPos;
	v_objectNormal = a_normal;
}
