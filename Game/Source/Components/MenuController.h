#pragma once
#include "Components/UI/BasicUIView.h"

class MenuController
	: public BasicUIView
{
public:
	MenuController();

#if USING( ME_UI )
	void OnUILoad(ultralight::JSObject& GlobalWindow, ultralight::View* Caller) override;

	void LoadScene(const ultralight::JSObject& thisObject, const ultralight::JSArgs& args);
#endif
};

ME_REGISTER_COMPONENT(MenuController);