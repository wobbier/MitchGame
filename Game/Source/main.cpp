#include "MitchGame.h"
#include "Engine/Engine.h"

int main()
{
	Engine gameEngine;

	gameEngine.Init(new MitchGame(&gameEngine));
	gameEngine.Run();

	return 0;
}