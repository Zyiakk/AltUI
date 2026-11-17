#include "Modules/ModuleManager.h"
IMPLEMENT_MODULE(FDefaultModuleImpl, TheKillingAntidote)
#include "TKAGameStubs.h"
// editor stand-in: the row copied as the game's native does (editor tests read the result)
void UMcoreFunctionLibrary::AppendDataTableRow(FName rowName, const UDataTable* SourceTable, UDataTable* DestTable) {
  if (!SourceTable || !DestTable || SourceTable->RowStruct != DestTable->RowStruct) return;
  if (const uint8* Src = SourceTable->FindRowUnchecked(rowName)) DestTable->AddRow(rowName, *reinterpret_cast<const FTableRowBase*>(Src));
}
