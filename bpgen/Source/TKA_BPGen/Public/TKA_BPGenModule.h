#pragma once
#include "Modules/ModuleManager.h"
class FTKA_BPGenModule : public IModuleInterface {
public:
  virtual void StartupModule() override {}
  virtual void ShutdownModule() override {}
};
