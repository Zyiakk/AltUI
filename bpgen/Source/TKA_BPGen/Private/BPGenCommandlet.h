#pragma once
#include "Commandlets/Commandlet.h"
#include "BPGenCommandlet.generated.h"
DECLARE_LOG_CATEGORY_EXTERN(LogBPGen, Log, All);
UCLASS()
class UBPGenCommandlet : public UCommandlet {
  GENERATED_BODY()
public:
  UBPGenCommandlet();
  virtual int32 Main(const FString& Params) override;
};
