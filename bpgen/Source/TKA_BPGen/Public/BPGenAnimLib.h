#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "BPGenAnimLib.generated.h"
class UAnimSequenceBase;
// Read-back for editor tests: a montage's sections, segments and the notifies' objects are plain UPROPERTY()s the 4.27 editor Python API cannot see.
UCLASS()
class UBPGenAnimLib : public UBlueprintFunctionLibrary {
  GENERATED_BODY()
public:
  // One line per fact: "ANIM <name> class= length= ratescale= skeleton=", "BLEND in= out= trigger= auto=", "SLOT <i> <name> group=", "SEGMENT <slot> <i> anim= pos=
  // start= end= rate= loops=", "SECTION <i> <name> time= next= seg=<slot>:<segment> link=", "NOTIFY <i> name= class= object= time= duration= track= seg= link=
  // end=", "VALUE <i> <variable>=<value>" (every variable the notify's own classes add).
  UFUNCTION(BlueprintCallable, Category = "BPGen") static TArray<FString> DescribeAnim(UAnimSequenceBase* Anim);
  // Blend spaces and animation blueprints: "BLENDSPACE ...", "SAMPLE <i> anim= value= valid=", "ELEMENT <i> idx= w="; "ABP ...", "NODE <i> <class> ...",
  // "LINK <from> -> <to>" (pose and variable links of the AnimGraph).
  UFUNCTION(BlueprintCallable, Category = "BPGen") static TArray<FString> DescribeAnimAsset(UObject* Asset);
};
