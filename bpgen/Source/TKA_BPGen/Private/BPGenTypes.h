#pragma once
#include "CoreMinimal.h"
#include "EdGraph/EdGraphPin.h"

namespace BPGenTypes {
  // Loads classes/structs/enums/assets. "/Script/X.Y" or "/Game/A/B[.B[_C]]"; Blueprint paths return the GeneratedClass.
  UObject* LoadObj(const FString& Path);
  UClass* LoadClassChecked(const FString& Path);
  // Spec: bool|int|float|name|string|text|byte|object:<Path>|class:<Path>|softobject:<Path>|softclass:<Path>|struct:<Path>|enum:<Path>
  // container: ""|array|set|map (ValueSpec for map)
  bool PinTypeFromSpec(const FString& Spec, const FString& Container, const FString& ValueSpec, FEdGraphPinType& Out, FString& Err);
  FString PinTypeToString(const FEdGraphPinType& T);
}
