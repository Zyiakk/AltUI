#pragma once
#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
class UBlueprint; class UEdGraph; class UClass;
namespace BPGenGraph {
  void PickBlueprintClasses(UClass* Parent, UClass*& BPClass, UClass*& GenClass);
  bool BuildGraph(UBlueprint* BP, UEdGraph* G, const TSharedPtr<FJsonObject>& J, FString& Err);
  bool BuildWidgetTree(UBlueprint* BP, const TSharedPtr<FJsonObject>& J, FString& Err);
}
