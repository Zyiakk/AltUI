#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Engine/DataTable.h"
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

// The game's native library: only what AltUI calls. Signature as in the game's reflection data; the body here is empty,
// in the game the path resolves to the real function.
UCLASS()
class UMcoreFunctionLibrary : public UBlueprintFunctionLibrary {
  GENERATED_BODY()
public:
  UFUNCTION(BlueprintCallable, Category = "Mcore")
  static void AppendDataTableRow(FName rowName, const UDataTable* SourceTable, UDataTable* DestTable);
};
