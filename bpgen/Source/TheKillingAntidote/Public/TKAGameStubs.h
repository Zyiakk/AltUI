#pragma once
#include "CoreMinimal.h"
#include "TKAGameStubs.generated.h"

// One saved actor in a story save (TKA_Save: Player Save Data, Saved Actors): ByteData = the actor's SaveGame properties,
// tagged-property serialised. Members as the game declares them, only those AltUI reads (ComponentsData left out).
USTRUCT(BlueprintType)
struct FActorSaveData {
  GENERATED_BODY()
  UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector position;
  UPROPERTY(EditAnywhere, BlueprintReadWrite) FRotator Rotation;
  UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<uint8> ByteData;
};
