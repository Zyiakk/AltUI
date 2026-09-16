#include "BPGenAssets.h"
#include "BPGenTypes.h"
#include "BPGenGraph.h"
#include "BPGenCommandlet.h"
#include "AssetRegistryModule.h"
#include "Engine/Blueprint.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "Engine/UserDefinedEnum.h"
#include "Engine/UserDefinedStruct.h"
#include "Engine/DataTable.h"
#include "Engine/CompositeDataTable.h"
#include "Engine/Texture2D.h"
#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Modules/ModuleManager.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "Kismet2/CompilerResultsLog.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/StructureEditorUtils.h"
#include "UserDefinedStructure/UserDefinedStructEditorData.h"
#include "Kismet2/EnumEditorUtils.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_FunctionResult.h"
#include "EdGraphSchema_K2.h"
#include "UObject/Package.h"
#include "Misc/PackageName.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"

UPackage* BPGenAssets::MakePackage(const FString& PackagePath, FString& OutName) {
  OutName = FPackageName::GetShortName(PackagePath);
  UPackage* Pkg = CreatePackage(*PackagePath);
  Pkg->FullyLoad();
  return Pkg;
}

bool BPGenAssets::SaveAsset(UObject* Asset) {
  UPackage* Pkg = Asset->GetOutermost();
  Pkg->MarkPackageDirty();
  FAssetRegistryModule::AssetCreated(Asset);
  const FString FileName = FPackageName::LongPackageNameToFilename(Pkg->GetName(), FPackageName::GetAssetPackageExtension());
  const bool bOk = UPackage::SavePackage(Pkg, Asset, RF_Public | RF_Standalone, *FileName, GError, nullptr, false, true, SAVE_NoError);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN saved %s -> %s (%s)"), *Asset->GetPathName(), *FileName, bOk ? TEXT("ok") : TEXT("FAILED"));
  return bOk;
}

FString BPGenAssets::BaseDir;

static FString JStr(const TSharedPtr<FJsonObject>& O, const TCHAR* K, const FString& Def = TEXT("")) { FString V; return O->TryGetStringField(K, V) ? V : Def; }
static bool JBool(const TSharedPtr<FJsonObject>& O, const TCHAR* K, bool Def = false) { bool V; return O->TryGetBoolField(K, V) ? V : Def; }
static const TArray<TSharedPtr<FJsonValue>>* JArr(const TSharedPtr<FJsonObject>& O, const TCHAR* K) { const TArray<TSharedPtr<FJsonValue>>* A = nullptr; O->TryGetArrayField(K, A); return A; }

// ---------- enum ----------
static bool MakeEnum(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; UPackage* Pkg = BPGenAssets::MakePackage(JStr(A, TEXT("path")), Name);
  UUserDefinedEnum* E = FindObject<UUserDefinedEnum>(Pkg, *Name);
  if (!E) E = Cast<UUserDefinedEnum>(FEnumEditorUtils::CreateUserDefinedEnum(Pkg, *Name, RF_Public | RF_Standalone));
  if (!E) { Err = TEXT("enum create failed"); return false; }
  const TArray<TSharedPtr<FJsonValue>>* Vals = JArr(A, TEXT("values"));
  if (!Vals) { Err = TEXT("enum: values missing"); return false; }
  for (const auto& V : *Vals) {
    const FString Wanted = V->AsString(); bool Found = false;
    for (int32 i = 0; i < E->NumEnums() - 1; ++i) if (E->GetDisplayNameTextByIndex(i).ToString() == Wanted) Found = true;
    if (Found) continue;
    FEnumEditorUtils::AddNewEnumeratorForUserDefinedEnum(E);
    FEnumEditorUtils::SetEnumeratorDisplayName(E, E->NumEnums() - 2, FText::FromString(Wanted));
  }
  return BPGenAssets::SaveAsset(E);
}

// ---------- struct ----------
static bool MakeStruct(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; UPackage* Pkg = BPGenAssets::MakePackage(JStr(A, TEXT("path")), Name);
  UUserDefinedStruct* S = FindObject<UUserDefinedStruct>(Pkg, *Name);
  if (!S) S = FStructureEditorUtils::CreateUserDefinedStruct(Pkg, *Name, RF_Public | RF_Standalone);
  if (!S) { Err = TEXT("struct create failed"); return false; }
  const TArray<TSharedPtr<FJsonValue>>* Members = JArr(A, TEXT("members"));
  if (!Members) { Err = TEXT("struct: members missing"); return false; }
  for (const auto& MV : *Members) {
    const TSharedPtr<FJsonObject> M = MV->AsObject();
    const FString MName = JStr(M, TEXT("name"));
    bool Exists = false;
    for (const FStructVariableDescription& D : FStructureEditorUtils::GetVarDesc(S)) if (D.FriendlyName == MName) Exists = true;
    if (Exists) continue;
    FEdGraphPinType T; if (!BPGenTypes::PinTypeFromSpec(JStr(M, TEXT("type")), JStr(M, TEXT("container")), JStr(M, TEXT("value_type")), T, Err)) return false;
    if (!FStructureEditorUtils::AddVariable(S, T)) { Err = TEXT("AddVariable failed: ") + MName; return false; }
    TArray<FStructVariableDescription>& Descs = FStructureEditorUtils::GetVarDesc(S);
    FStructureEditorUtils::RenameVariable(S, Descs.Last().VarGuid, MName);
    // stub of a game struct: the internal property name (Name_idx_GUID) must match the cooked original exactly
    const FString Internal = JStr(M, TEXT("internal_name"));
    if (!Internal.IsEmpty()) {
      FString GuidStr; Internal.Split(TEXT("_"), nullptr, &GuidStr, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
      FGuid Guid; if (!FGuid::ParseExact(GuidStr, EGuidFormats::Digits, Guid)) { Err = TEXT("struct: internal_name without GUID suffix: ") + Internal; return false; }
      Descs.Last().VarName = FName(*Internal); Descs.Last().VarGuid = Guid;
    }
  }
  // remove the default member "MemberVar_0" that CreateUserDefinedStruct creates
  for (const FStructVariableDescription& D : TArray<FStructVariableDescription>(FStructureEditorUtils::GetVarDesc(S)))
    if (D.FriendlyName.StartsWith(TEXT("MemberVar_")) && FStructureEditorUtils::GetVarDesc(S).Num() > 1) FStructureEditorUtils::RemoveVariable(S, D.VarGuid);
  FStructureEditorUtils::CompileStructure(S);
  return BPGenAssets::SaveAsset(S);
}

static FString NormName(const FString& S) { FString R = S.ToLower(); R.ReplaceInline(TEXT(" "), TEXT("")); R.ReplaceInline(TEXT("_"), TEXT("")); return R; }
// field name of a user-defined struct: FriendlyName or base name (without _idx_GUID) -> internal VarName
static FString ResolveMemberName(UScriptStruct* Struct, const FString& Key) {
  UUserDefinedStruct* UDS = Cast<UUserDefinedStruct>(Struct);
  if (!UDS) return Key;
  const FString W = NormName(Key);
  for (const FStructVariableDescription& D : FStructureEditorUtils::GetVarDesc(UDS)) {
    const FString VN = D.VarName.ToString();
    FString Base = VN; int32 L = VN.Len();
    if (L > 34 && VN[L - 33] == TCHAR('_')) { Base = VN.Left(L - 33); int32 Us; if (Base.FindLastChar(TCHAR('_'), Us)) Base = Base.Left(Us); }
    if (NormName(D.FriendlyName) == W || NormName(Base) == W || VN == Key) return VN;
  }
  return Key;
}

// ---------- datatable ----------
static bool MakeDataTable(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; UPackage* Pkg = BPGenAssets::MakePackage(JStr(A, TEXT("path")), Name);
  UScriptStruct* Row = Cast<UScriptStruct>(BPGenTypes::LoadObj(JStr(A, TEXT("row_struct"))));
  if (!Row) { Err = TEXT("row_struct not found: ") + JStr(A, TEXT("row_struct")); return false; }
  UDataTable* DT = FindObject<UDataTable>(Pkg, *Name);
  if (!DT) DT = JBool(A, TEXT("composite")) ? NewObject<UCompositeDataTable>(Pkg, *Name, RF_Public | RF_Standalone) : NewObject<UDataTable>(Pkg, *Name, RF_Public | RF_Standalone);
  DT->RowStruct = Row;
  const TSharedPtr<FJsonObject>* Rows = nullptr;
  if (A->TryGetObjectField(TEXT("rows"), Rows)) {
    // JSON array [{"Name":"row", "Field":value,...}] for CreateTableFromJSONString
    TArray<TSharedPtr<FJsonValue>> Arr;
    for (const auto& KV : (*Rows)->Values) {
      TSharedPtr<FJsonObject> O = MakeShared<FJsonObject>();
      O->SetStringField(TEXT("Name"), KV.Key);
      for (const auto& F : KV.Value->AsObject()->Values) O->SetField(ResolveMemberName(Row, F.Key), F.Value);
      Arr.Add(MakeShared<FJsonValueObject>(O));
    }
    FString JsonText; TSharedRef<TJsonWriter<>> Wr = TJsonWriterFactory<>::Create(&JsonText);
    FJsonSerializer::Serialize(Arr, Wr);
    TArray<FString> Problems = DT->CreateTableFromJSONString(JsonText);
    int32 Hard = 0;
    for (const FString& P : Problems) {
      if (P.Contains(TEXT("is missing an entry for"))) { UE_LOG(LogBPGen, Verbose, TEXT("BPGEN rows: %s"), *P); continue; }
      UE_LOG(LogBPGen, Warning, TEXT("BPGEN rows: %s"), *P); ++Hard;
    }
    if (Hard) { Err = TEXT("rows import problems in ") + Name; return false; }
  }
  const TArray<TSharedPtr<FJsonValue>>* Parents = JArr(A, TEXT("parent_tables"));
  if (Parents) {
    UCompositeDataTable* CDT = Cast<UCompositeDataTable>(DT);
    if (!CDT) { Err = TEXT("parent_tables on non-composite table ") + Name; return false; }
    TArray<UDataTable*> PT;
    for (const auto& V : *Parents) { UDataTable* T = Cast<UDataTable>(BPGenTypes::LoadObj(V->AsString())); if (!T) { Err = TEXT("parent table not found ") + V->AsString(); return false; } PT.Add(T); }
    CDT->AppendParentTables(PT);
  }
  return BPGenAssets::SaveAsset(DT);
}

// ---------- blueprint ----------
static UBlueprint* EnsureBlueprint(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; const FString Path = JStr(A, TEXT("path")); UPackage* Pkg = BPGenAssets::MakePackage(Path, Name);
  UBlueprint* BP = FindObject<UBlueprint>(Pkg, *Name);
  const FString Mode = JStr(A, TEXT("mode"), TEXT("create"));
  if (!BP) {
    if (Mode == TEXT("augment")) { Err = TEXT("augment: blueprint not found ") + Path; return nullptr; }
    UClass* Parent = BPGenTypes::LoadClassChecked(JStr(A, TEXT("parent")));
    if (!Parent) { Err = TEXT("parent not found: ") + JStr(A, TEXT("parent")); return nullptr; }
    UClass* BPClass = UBlueprint::StaticClass(); UClass* GenClass = UBlueprintGeneratedClass::StaticClass();
    BPGenGraph::PickBlueprintClasses(Parent, BPClass, GenClass);
    BP = FKismetEditorUtilities::CreateBlueprint(Parent, Pkg, *Name, BPTYPE_Normal, BPClass, GenClass, FName("BPGen"));
    if (!BP) { Err = TEXT("CreateBlueprint failed ") + Path; return nullptr; }
  }
  // variables
  if (const auto* Vars = JArr(A, TEXT("variables"))) for (const auto& VV : *Vars) {
    const TSharedPtr<FJsonObject> V = VV->AsObject(); const FName VName(*JStr(V, TEXT("name")));
    FEdGraphPinType T; if (!BPGenTypes::PinTypeFromSpec(JStr(V, TEXT("type")), JStr(V, TEXT("container")), JStr(V, TEXT("value_type")), T, Err)) return nullptr;
    if (FBlueprintEditorUtils::FindNewVariableIndex(BP, VName) == INDEX_NONE) {
      if (!FBlueprintEditorUtils::AddMemberVariable(BP, VName, T, JStr(V, TEXT("default")))) { Err = TEXT("AddMemberVariable failed ") + VName.ToString(); return nullptr; }
    }
    if (JBool(V, TEXT("expose_on_spawn"))) FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP, VName, nullptr, FBlueprintMetadata::MD_ExposeOnSpawn, TEXT("true"));
    if (JBool(V, TEXT("instance_editable"))) FBlueprintEditorUtils::SetBlueprintOnlyEditableFlag(BP, VName, false);
  }
  // widget tree (before the graphs so widget variables exist in the skeleton)
  const TSharedPtr<FJsonObject>* WT = nullptr;
  if (A->TryGetObjectField(TEXT("widget_tree"), WT)) {
    if (!BPGenGraph::BuildWidgetTree(BP, *WT, Err)) return nullptr;
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
  }
  // function signatures (+ optional body)
  if (const auto* Funcs = JArr(A, TEXT("functions"))) for (const auto& FV : *Funcs) {
    const TSharedPtr<FJsonObject> F = FV->AsObject(); const FName FnName(*JStr(F, TEXT("name")));
    const bool bOverride = JBool(F, TEXT("override"));
    UEdGraph* G = nullptr;
    for (UEdGraph* FG : BP->FunctionGraphs) if (FG->GetFName() == FnName) G = FG;
    if (!G) {
      G = FBlueprintEditorUtils::CreateNewGraph(BP, FnName, UEdGraph::StaticClass(), UEdGraphSchema_K2::StaticClass());
      if (bOverride) {
        UClass* Parent = BP->ParentClass;
        if (!Parent || !Parent->FindFunctionByName(FnName)) { Err = TEXT("override: parent has no function ") + FnName.ToString(); return nullptr; }
        FBlueprintEditorUtils::AddFunctionGraph<UClass>(BP, G, /*bIsUserCreated*/ false, Parent);
      } else {
        FBlueprintEditorUtils::AddFunctionGraph<UClass>(BP, G, /*bIsUserCreated*/ true, nullptr);
      }
    }
    TArray<UK2Node_FunctionEntry*> Entries; G->GetNodesOfClass(Entries);
    if (Entries.Num() == 0) { Err = TEXT("no entry node in ") + FnName.ToString(); return nullptr; }
    UK2Node_FunctionEntry* Entry = Entries[0];
    if (JBool(F, TEXT("pure"))) Entry->AddExtraFlags(FUNC_BlueprintPure);
    if (!bOverride) if (const auto* Ins = JArr(F, TEXT("inputs"))) for (const auto& PV : *Ins) {
      const TSharedPtr<FJsonObject> P = PV->AsObject(); const FName PName(*JStr(P, TEXT("name")));
      if (Entry->FindPin(PName)) continue;
      FEdGraphPinType T; if (!BPGenTypes::PinTypeFromSpec(JStr(P, TEXT("type")), JStr(P, TEXT("container")), JStr(P, TEXT("value_type")), T, Err)) return nullptr;
      T.bIsReference = JBool(P, TEXT("ref"));
      Entry->CreateUserDefinedPin(PName, T, EGPD_Output);
    }
    if (!bOverride) if (const auto* Outs = JArr(F, TEXT("outputs"))) if (Outs->Num() > 0) {
      TArray<UK2Node_FunctionResult*> Results; G->GetNodesOfClass(Results);
      UK2Node_FunctionResult* Result = Results.Num() ? Results[0] : nullptr;
      if (!Result) {
        FGraphNodeCreator<UK2Node_FunctionResult> Creator(*G); Result = Creator.CreateNode(); Result->NodePosX = 600; Creator.Finalize();
        UEdGraphPin* EntryThen = Entry->FindPin(UEdGraphSchema_K2::PN_Then); UEdGraphPin* ResExec = Result->FindPin(UEdGraphSchema_K2::PN_Execute);
        if (EntryThen && ResExec && EntryThen->LinkedTo.Num() == 0) EntryThen->MakeLinkTo(ResExec);
      }
      for (const auto& PV : *Outs) {
        const TSharedPtr<FJsonObject> P = PV->AsObject(); const FName PName(*JStr(P, TEXT("name")));
        if (Result->FindPin(PName)) continue;
        FEdGraphPinType T; if (!BPGenTypes::PinTypeFromSpec(JStr(P, TEXT("type")), JStr(P, TEXT("container")), JStr(P, TEXT("value_type")), T, Err)) return nullptr;
        Result->CreateUserDefinedPin(PName, T, EGPD_Input);
      }
    }
  }
  FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);   // skeleton with all new signatures/pins
  // pass 2: function bodies (all signatures now exist in the skeleton -> call_self possible)
  if (const auto* Funcs = JArr(A, TEXT("functions"))) for (const auto& FV : *Funcs) {
    const TSharedPtr<FJsonObject> F = FV->AsObject(); const FName FnName(*JStr(F, TEXT("name")));
    const TSharedPtr<FJsonObject>* Body = nullptr;
    if (!F->TryGetObjectField(TEXT("graph"), Body)) continue;
    UEdGraph* G = nullptr;
    for (UEdGraph* FG : BP->FunctionGraphs) if (FG->GetFName() == FnName) G = FG;
    if (!G) { Err = TEXT("body: graph missing ") + FnName.ToString(); return nullptr; }
    if (!BPGenGraph::BuildGraph(BP, G, *Body, Err)) return nullptr;
  }
  // event graph
  const TSharedPtr<FJsonObject>* EG = nullptr;
  if (A->TryGetObjectField(TEXT("event_graph"), EG)) {
    if (!BPGenGraph::BuildGraph(BP, FBlueprintEditorUtils::FindEventGraph(BP), *EG, Err)) return nullptr;
  }
  FCompilerResultsLog Results; Results.bSilentMode = false;
  FKismetEditorUtilities::CompileBlueprint(BP, EBlueprintCompileOptions::SkipGarbageCollection, &Results);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN compiled %s errors=%d warnings=%d"), *Path, Results.NumErrors, Results.NumWarnings);
  if (BP->Status == BS_Error || Results.NumErrors > 0) { Err = FString::Printf(TEXT("compile errors (%d) in %s"), Results.NumErrors, *Path); return nullptr; }
  // CDO defaults after compiling
  const TSharedPtr<FJsonObject>* Defs = nullptr;
  if (A->TryGetObjectField(TEXT("defaults"), Defs)) {
    UObject* CDO = BP->GeneratedClass->GetDefaultObject();
    for (const auto& KV : (*Defs)->Values) {
      FProperty* P = BP->GeneratedClass->FindPropertyByName(*KV.Key);
      if (!P) { Err = TEXT("default: property not found ") + KV.Key; return nullptr; }
      const FString Val = KV.Value->Type == EJson::String ? KV.Value->AsString() : (KV.Value->Type == EJson::Boolean ? (KV.Value->AsBool() ? TEXT("true") : TEXT("false")) : FString::SanitizeFloat(KV.Value->AsNumber()));
      if (!P->ImportText(*Val, P->ContainerPtrToValuePtr<void>(CDO), PPF_None, CDO)) { Err = TEXT("default: import failed ") + KV.Key; return nullptr; }
    }
    CDO->MarkPackageDirty();
  }
  return BP;
}

// ---------- texture (PNG -> UTexture2D, UI settings via "props") ----------
static bool MakeTexture(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; UPackage* Pkg = BPGenAssets::MakePackage(JStr(A, TEXT("path")), Name);
  FString File = JStr(A, TEXT("file"));
  if (FPaths::IsRelative(File)) File = FPaths::Combine(BPGenAssets::BaseDir, File);
  TArray<uint8> Png; if (!FFileHelper::LoadFileToArray(Png, *File)) { Err = TEXT("texture: cannot read ") + File; return false; }
  IImageWrapperModule& IWM = FModuleManager::LoadModuleChecked<IImageWrapperModule>(TEXT("ImageWrapper"));
  TSharedPtr<IImageWrapper> IW = IWM.CreateImageWrapper(EImageFormat::PNG);
  TArray<uint8> Raw;
  if (!IW.IsValid() || !IW->SetCompressed(Png.GetData(), Png.Num()) || !IW->GetRaw(ERGBFormat::BGRA, 8, Raw)) { Err = TEXT("texture: png decode failed ") + File; return false; }
  UTexture2D* T = FindObject<UTexture2D>(Pkg, *Name);
  if (!T) T = NewObject<UTexture2D>(Pkg, *Name, RF_Public | RF_Standalone);
  T->Source.Init(IW->GetWidth(), IW->GetHeight(), 1, 1, TSF_BGRA8, Raw.GetData());
  const TSharedPtr<FJsonObject>* Props = nullptr;
  if (A->TryGetObjectField(TEXT("props"), Props)) for (const auto& KV : (*Props)->Values) {
    FProperty* P = T->GetClass()->FindPropertyByName(*KV.Key);
    if (!P) { Err = TEXT("texture: property not found ") + KV.Key; return false; }
    const FString Val = KV.Value->Type == EJson::String ? KV.Value->AsString() : (KV.Value->Type == EJson::Boolean ? (KV.Value->AsBool() ? TEXT("true") : TEXT("false")) : FString::SanitizeFloat(KV.Value->AsNumber()));
    if (!P->ImportText(*Val, P->ContainerPtrToValuePtr<void>(T), PPF_None, T)) { Err = TEXT("texture: import failed ") + KV.Key + TEXT("=") + Val; return false; }
  }
  T->UpdateResource(); T->PostEditChange();
  UE_LOG(LogBPGen, Display, TEXT("BPGEN texture %s %dx%d from %s"), *Name, IW->GetWidth(), IW->GetHeight(), *File);
  return BPGenAssets::SaveAsset(T);
}

bool BPGenAssets::Process(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Type = JStr(A, TEXT("type"));
  UE_LOG(LogBPGen, Display, TEXT("BPGEN process %s %s"), *Type, *JStr(A, TEXT("path")));
  if (Type == TEXT("enum")) return MakeEnum(A, Err);
  if (Type == TEXT("struct")) return MakeStruct(A, Err);
  if (Type == TEXT("datatable")) return MakeDataTable(A, Err);
  if (Type == TEXT("texture")) return MakeTexture(A, Err);
  if (Type == TEXT("blueprint")) { UBlueprint* BP = EnsureBlueprint(A, Err); return BP && SaveAsset(BP); }
  Err = TEXT("unknown asset type ") + Type; return false;
}

static FString CppType(FProperty* P) { FString Ext; const FString T = P->GetCPPType(&Ext); return T + Ext; }

void BPGenAssets::Dump(const FString& PackagePath) {
  UClass* C = BPGenTypes::LoadClassChecked(PackagePath);
  if (!C) { UE_LOG(LogBPGen, Error, TEXT("DUMP ERROR class not found %s"), *PackagePath); return; }
  UE_LOG(LogBPGen, Display, TEXT("DUMP CLASS %s : %s"), *C->GetName(), *C->GetSuperClass()->GetName());
  for (TFieldIterator<FProperty> It(C, EFieldIteratorFlags::ExcludeSuper); It; ++It)
    UE_LOG(LogBPGen, Display, TEXT("DUMP VAR %s %s"), *It->GetName(), *CppType(*It));
  for (TFieldIterator<UFunction> It(C, EFieldIteratorFlags::ExcludeSuper); It; ++It) {
    FString Ins, Outs;
    for (TFieldIterator<FProperty> P(*It); P && (P->PropertyFlags & CPF_Parm); ++P) {
      const FString S = P->GetName() + TEXT(":") + CppType(*P);
      if (P->PropertyFlags & CPF_OutParm) { if (!Outs.IsEmpty()) Outs += TEXT(","); Outs += S; }
      else { if (!Ins.IsEmpty()) Ins += TEXT(","); Ins += S; }
    }
    UE_LOG(LogBPGen, Display, TEXT("DUMP FUNC %s(%s)%s%s script=%d"), *It->GetName(), *Ins, Outs.IsEmpty() ? TEXT("") : TEXT(" -> "), *Outs, It->Script.Num());
  }
  UObject* CDO = C->GetDefaultObject();
  for (TFieldIterator<FProperty> It(C); It; ++It) {
    if (It->GetName() != TEXT("InitialLifeSpan") && It->GetName() != TEXT("ViewPitchMin") && It->GetName() != TEXT("ViewPitchMax")) continue;
    FString V; It->ExportTextItem(V, It->ContainerPtrToValuePtr<void>(CDO), nullptr, CDO, PPF_None);
    UE_LOG(LogBPGen, Display, TEXT("DUMP DEFAULT %s %s"), *It->GetName(), *V);
  }
}
