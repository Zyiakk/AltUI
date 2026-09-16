#pragma once
#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
class UPackage;

namespace BPGenAssets {
  bool Process(const TSharedPtr<FJsonObject>& A, FString& Err);   // dispatch by "type"
  extern FString BaseDir;   // directory of the current manifest file (for relative "file" paths)
  bool SaveAsset(UObject* Asset);
  UPackage* MakePackage(const FString& PackagePath, FString& OutName);
  void Dump(const FString& PackagePath);
}
