#include "BPGenAssets.h"
#include "BPGenTypes.h"
#include "BPGenGraph.h"
#include "BPGenCommandlet.h"
#include "AssetRegistryModule.h"
#include "Engine/Blueprint.h"
#include "HAL/PlatformTime.h"
#include "HAL/PlatformMemory.h"
#include "UObject/UObjectGlobals.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "Engine/UserDefinedEnum.h"
#include "Engine/UserDefinedStruct.h"
#include "Engine/DataTable.h"
#include "Engine/CompositeDataTable.h"
#include "Engine/Texture2D.h"
#include "Exporters/Exporter.h"
#include "AssetExportTask.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstance.h"
#include "Materials/MaterialInstanceConstant.h"
#include "Materials/Material.h"
#include "Materials/MaterialExpression.h"
#include "Materials/MaterialExpressionParameter.h"
#include "Materials/MaterialExpressionTextureSampleParameter.h"
#include "Materials/MaterialExpressionComponentMask.h"
#include "StaticParameterSet.h"
#include "Factories/FbxFactory.h"
#include "Factories/FbxImportUI.h"
#include "Factories/FbxSkeletalMeshImportData.h"
#include "AssetImportTask.h"
#include "AssetToolsModule.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/Skeleton.h"
#include "Rendering/SkeletalMeshModel.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "ClothingAsset.h"
#include "ClothLODData.h"
#include "PointWeightMap.h"
#include "ClothConfigNv.h"
#include "ClothingAssetFactoryInterface.h"
#include "ClothingSystemEditorInterfaceModule.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Actor.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/Texture.h"
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
#include "Animation/AnimBlueprint.h"
#include "Animation/AnimBlueprintGeneratedClass.h"
#include "Animation/AnimInstance.h"
#include "Animation/Skeleton.h"
#include "AnimationGraph.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_LinkedInputPose.h"
#include "AnimGraphNode_LocalToComponentSpace.h"
#include "AnimGraphNode_ComponentToLocalSpace.h"
#include "AnimGraphNode_ModifyBone.h"
#include "AnimGraphNode_PoseSnapshot.h"
#include "AnimGraphNode_SequencePlayer.h"
#include "AnimGraphNode_TwoWayBlend.h"
#include "Animation/AnimSequence.h"
#include "AnimationBlueprintLibrary.h"
#include "Factories/FbxAnimSequenceImportData.h"
#include "K2Node_VariableGet.h"
#include "Engine/SimpleConstructionScript.h"
#include "Engine/SCS_Node.h"

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
// A function graph of the blueprint itself or of an interface it implements (those carry the interface's signature).
static UEdGraph* FindFnGraph(UBlueprint* BP, const FName& FnName, bool* bFromInterface = nullptr) {
  if (bFromInterface) *bFromInterface = false;
  for (UEdGraph* FG : BP->FunctionGraphs) if (FG->GetFName() == FnName) return FG;
  for (const FBPInterfaceDescription& I : BP->ImplementedInterfaces)
    for (UEdGraph* FG : I.Graphs) if (FG->GetFName() == FnName) { if (bFromInterface) *bFromInterface = true; return FG; }
  return nullptr;
}

static UBlueprint* EnsureBlueprint(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; const FString Path = JStr(A, TEXT("path")); UPackage* Pkg = BPGenAssets::MakePackage(Path, Name);
  UBlueprint* BP = FindObject<UBlueprint>(Pkg, *Name);
  const FString Mode = JStr(A, TEXT("mode"), TEXT("create"));
  if (!BP) {
    if (Mode == TEXT("augment")) { Err = TEXT("augment: blueprint not found ") + Path; return nullptr; }
    if (JStr(A, TEXT("blueprint_type")) == TEXT("interface")) {   // Blueprint interface: functions are signatures only
      BP = FKismetEditorUtilities::CreateBlueprint(UInterface::StaticClass(), Pkg, *Name, BPTYPE_Interface, UBlueprint::StaticClass(), UBlueprintGeneratedClass::StaticClass(), FName("BPGen"));
      if (!BP) { Err = TEXT("CreateBlueprint (interface) failed ") + Path; return nullptr; }
    }
  }
  if (!BP) {
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
  // components (SimpleConstructionScript): {name, class, parent?, properties{}} - parent names an earlier component, none
  // = a root node (the first one replaces DefaultSceneRoot); properties are ImportText strings on the component template
  if (const auto* Comps = JArr(A, TEXT("components"))) {
    USimpleConstructionScript* SCS = BP->SimpleConstructionScript;
    if (!SCS) { Err = TEXT("components: blueprint has no construction script ") + Path; return nullptr; }
    for (const auto& CV : *Comps) {
      const TSharedPtr<FJsonObject> C = CV->AsObject(); const FName CName(*JStr(C, TEXT("name")));
      if (SCS->FindSCSNode(CName)) continue;
      UClass* CC = BPGenTypes::LoadClassChecked(JStr(C, TEXT("class")));
      if (!CC || !CC->IsChildOf(UActorComponent::StaticClass())) { Err = TEXT("component class not found ") + JStr(C, TEXT("class")); return nullptr; }
      USCS_Node* Node = SCS->CreateNode(CC, CName);
      const TSharedPtr<FJsonObject>* Props = nullptr;
      if (C->TryGetObjectField(TEXT("properties"), Props)) for (const auto& KV : (*Props)->Values) {
        UObject* T = Node->ComponentTemplate; FProperty* P = CC->FindPropertyByName(*KV.Key);
        if (!P) { Err = TEXT("component property not found ") + CName.ToString() + TEXT(".") + KV.Key; return nullptr; }
        const FString Val = KV.Value->Type == EJson::String ? KV.Value->AsString() : (KV.Value->Type == EJson::Boolean ? (KV.Value->AsBool() ? TEXT("true") : TEXT("false")) : FString::SanitizeFloat(KV.Value->AsNumber()));
        if (!P->ImportText(*Val, P->ContainerPtrToValuePtr<void>(T), PPF_None, T)) { Err = TEXT("component: import failed ") + CName.ToString() + TEXT(".") + KV.Key + TEXT("=") + Val; return nullptr; }
      }
      const FString Parent = JStr(C, TEXT("parent"));
      if (Parent.IsEmpty()) SCS->AddNode(Node);
      else if (USCS_Node* PN = SCS->FindSCSNode(*Parent)) PN->AddChildNode(Node);
      else { Err = TEXT("component parent not found ") + Parent; return nullptr; }
    }
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
  }
  // implemented interfaces: their function graphs come with the interface's signature
  if (const auto* Ifs = JArr(A, TEXT("interfaces"))) for (const auto& IV : *Ifs) {
    UClass* IC = BPGenTypes::LoadClassChecked(IV->AsString());
    if (!IC) { Err = TEXT("interface not found ") + IV->AsString(); return nullptr; }
    const bool bHas = BP->ImplementedInterfaces.ContainsByPredicate([&](const FBPInterfaceDescription& D) { return D.Interface == IC; });
    if (!bHas && !FBlueprintEditorUtils::ImplementNewInterface(BP, IC->GetFName())) { Err = TEXT("ImplementNewInterface failed ") + IV->AsString(); return nullptr; }
  }
  // widget tree (before the graphs so widget variables exist in the skeleton)
  const TSharedPtr<FJsonObject>* WT = nullptr;
  if (A->TryGetObjectField(TEXT("widget_tree"), WT)) {
    if (!BPGenGraph::BuildWidgetTree(BP, *WT, Err)) return nullptr;
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
  }
  // function signatures (+ optional body)
  const double TSig = FPlatformTime::Seconds();
  if (const auto* Funcs = JArr(A, TEXT("functions"))) for (const auto& FV : *Funcs) {
    const TSharedPtr<FJsonObject> F = FV->AsObject(); const FName FnName(*JStr(F, TEXT("name")));
    bool bFromInterface = false;
    UEdGraph* G = FindFnGraph(BP, FnName, &bFromInterface);
    const bool bOverride = JBool(F, TEXT("override")) || bFromInterface;   // an interface function brings its own pins
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
  const double TBody = FPlatformTime::Seconds();
  // pass 2: function bodies (all signatures now exist in the skeleton -> call_self possible)
  // Every link to an input pin ends in MarkBlueprintAsModified (UK2Node::PinConnectionListChanged ->
  // ResetPinToAutogeneratedDefaultValue), which does blueprint-wide work - node caches, the class's post-construction
  // property list, PostEditChangeProperty. In the manager that was one full pass per link, and memory grew by ~100 MB per
  // function body up to the oom kill. BS_BeingCreated makes MarkBlueprintAsModified skip all of it; marked once below.
  const EBlueprintStatus StatusBefore = BP->Status; BP->Status = BS_BeingCreated;
  if (const auto* Funcs = JArr(A, TEXT("functions"))) for (const auto& FV : *Funcs) {
    const TSharedPtr<FJsonObject> F = FV->AsObject(); const FName FnName(*JStr(F, TEXT("name")));
    const TSharedPtr<FJsonObject>* Body = nullptr;
    if (!F->TryGetObjectField(TEXT("graph"), Body)) continue;
    UEdGraph* G = FindFnGraph(BP, FnName);
    if (!G) { Err = TEXT("body: graph missing ") + FnName.ToString(); return nullptr; }
    if (!BPGenGraph::BuildGraph(BP, G, *Body, Err, /*bMarkModified*/ false)) return nullptr;
  }
  // event graph
  const TSharedPtr<FJsonObject>* EG = nullptr;
  if (A->TryGetObjectField(TEXT("event_graph"), EG)) {
    if (!BPGenGraph::BuildGraph(BP, FBlueprintEditorUtils::FindEventGraph(BP), *EG, Err)) return nullptr;
  }
  BP->Status = (StatusBefore == BS_BeingCreated) ? BS_Dirty : StatusBefore;
  FBlueprintEditorUtils::MarkBlueprintAsModified(BP);   // once for all bodies and the event graph
  const double TComp = FPlatformTime::Seconds();
  FCompilerResultsLog Results; Results.bSilentMode = false;
  FKismetEditorUtilities::CompileBlueprint(BP, EBlueprintCompileOptions::SkipGarbageCollection, &Results);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN compiled %s errors=%d warnings=%d"), *Path, Results.NumErrors, Results.NumWarnings);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN timing %s signatures=%.1fs bodies=%.1fs (create=%.1f defaults=%.1f links=%.1f) compile=%.1fs"), *Path, TBody - TSig, TComp - TBody, BPGenGraph::TCreate, BPGenGraph::TDefaults, BPGenGraph::TLinks, FPlatformTime::Seconds() - TComp);
  BPGenGraph::TCreate = BPGenGraph::TDefaults = BPGenGraph::TLinks = 0;
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

// ---------- animblueprint (post-process ABP: InputPose -> LocalToComponent -> ModifyBone... -> ComponentToLocal -> Output) ----------
static UEdGraphPin* PosePin(UEdGraphNode* N, EEdGraphPinDirection Dir) {
  for (UEdGraphPin* P : N->Pins) {
    if (P->Direction != Dir) continue;
    UObject* Sub = P->PinType.PinSubCategoryObject.Get();
    if (Sub == FPoseLink::StaticStruct() || Sub == FComponentSpacePoseLink::StaticStruct()) return P;
  }
  return nullptr;
}

static bool MakeAnimBlueprint(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; const FString Path = JStr(A, TEXT("path")); UPackage* Pkg = BPGenAssets::MakePackage(Path, Name);
  USkeleton* Skel = Cast<USkeleton>(BPGenTypes::LoadObj(JStr(A, TEXT("skeleton"))));
  if (!Skel) { Err = TEXT("animblueprint: skeleton not found ") + JStr(A, TEXT("skeleton")); return false; }
  if (FindObject<UAnimBlueprint>(Pkg, *Name)) { Err = TEXT("animblueprint: exists (bpgen.sh deletes Mod/AltUI before the run) ") + Path; return false; }
  UAnimBlueprint* BP = Cast<UAnimBlueprint>(FKismetEditorUtilities::CreateBlueprint(UAnimInstance::StaticClass(), Pkg, *Name, BPTYPE_Normal,
      UAnimBlueprint::StaticClass(), UAnimBlueprintGeneratedClass::StaticClass(), FName("BPGen")));
  if (!BP) { Err = TEXT("animblueprint: CreateBlueprint failed ") + Path; return false; }
  BP->TargetSkeleton = Skel;
  if (const auto* Vars = JArr(A, TEXT("variables"))) for (const auto& VV : *Vars) {
    const TSharedPtr<FJsonObject> V = VV->AsObject(); const FName VName(*JStr(V, TEXT("name")));
    FEdGraphPinType T; if (!BPGenTypes::PinTypeFromSpec(JStr(V, TEXT("type")), JStr(V, TEXT("container")), JStr(V, TEXT("value_type")), T, Err)) return false;
    if (!FBlueprintEditorUtils::AddMemberVariable(BP, VName, T, JStr(V, TEXT("default")))) { Err = TEXT("animblueprint: AddMemberVariable failed ") + VName.ToString(); return false; }
  }
  FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);   // variables in the skeleton class before the Get nodes reference them
  UEdGraph* G = nullptr; for (UEdGraph* FG : BP->FunctionGraphs) if (FG->IsA<UAnimationGraph>()) G = FG;
  if (!G) { Err = TEXT("animblueprint: no AnimGraph in ") + Path; return false; }
  TArray<UAnimGraphNode_Root*> Roots; G->GetNodesOfClass(Roots);
  if (Roots.Num() == 0) { Err = TEXT("animblueprint: no Output Pose node"); return false; }
  const UEdGraphSchema* Schema = G->GetSchema();
  int32 X = -400;
  UEdGraphNode* In = nullptr;
  if (JStr(A, TEXT("source")) == TEXT("snapshot")) {
    // the pose comes from a PoseSnapshot variable (SnapshotPose / a saved pose): Pose Snapshot node in "Snapshot Pin" mode, its
    // hidden Snapshot pin shown and fed from the variable named by "snapshot_var" (a standalone ABP, no Input Pose)
    FGraphNodeCreator<UAnimGraphNode_PoseSnapshot> CS(*G); UAnimGraphNode_PoseSnapshot* S = CS.CreateNode(); S->NodePosX = X;
    S->Node.Mode = ESnapshotSourceMode::SnapshotPin; CS.Finalize();
    bool bShown = false;
    for (FOptionalPinFromProperty& O : S->ShowPinForProperties) if (O.PropertyName == TEXT("Snapshot")) { O.bShowPin = true; bShown = true; }
    if (!bShown) { Err = TEXT("animblueprint: Pose Snapshot node has no optional Snapshot pin"); return false; }
    S->ReconstructNode();
    UEdGraphPin* SnapPin = S->FindPin(TEXT("Snapshot"));
    if (!SnapPin) { Err = TEXT("animblueprint: Snapshot pin not shown after ReconstructNode"); return false; }
    FGraphNodeCreator<UK2Node_VariableGet> CG(*G); UK2Node_VariableGet* GetV = CG.CreateNode(); GetV->NodePosX = X - 300; GetV->NodePosY = 200;
    GetV->VariableReference.SetSelfMember(FName(*JStr(A, TEXT("snapshot_var")))); CG.Finalize();
    UEdGraphPin* Out = nullptr; for (UEdGraphPin* P : GetV->Pins) if (P->Direction == EGPD_Output) Out = P;
    if (!Out || !Schema->TryCreateConnection(Out, SnapPin)) { Err = TEXT("animblueprint: variable->Snapshot link failed: ") + JStr(A, TEXT("snapshot_var")); return false; }
    In = S;
  } else {
    FGraphNodeCreator<UAnimGraphNode_LinkedInputPose> CIn(*G); UAnimGraphNode_LinkedInputPose* LI = CIn.CreateNode(); LI->NodePosX = X; CIn.Finalize(); In = LI;
  }
  X += 300;
  FGraphNodeCreator<UAnimGraphNode_LocalToComponentSpace> CL2C(*G); UAnimGraphNode_LocalToComponentSpace* L2C = CL2C.CreateNode(); L2C->NodePosX = X; CL2C.Finalize();
  if (!Schema->TryCreateConnection(PosePin(In, EGPD_Output), PosePin(L2C, EGPD_Input))) { Err = TEXT("animblueprint: link InputPose->LocalToComponent failed"); return false; }
  UEdGraphNode* Prev = L2C;
  if (const auto* Nodes = JArr(A, TEXT("nodes"))) for (const auto& NV : *Nodes) {
    const TSharedPtr<FJsonObject> N = NV->AsObject(); X += 300;
    FGraphNodeCreator<UAnimGraphNode_ModifyBone> CM(*G); UAnimGraphNode_ModifyBone* M = CM.CreateNode(); M->NodePosX = X;
    M->Node.BoneToModify.BoneName = FName(*JStr(N, TEXT("bone")));
    const bool bTranslate = JStr(N, TEXT("kind")) == TEXT("translate");   // "translate": additive component-space translation from the variable instead of a scale
    M->Node.TranslationMode = bTranslate ? BMM_Additive : BMM_Ignore; M->Node.RotationMode = BMM_Ignore;
    M->Node.ScaleMode = bTranslate ? BMM_Ignore : (JStr(N, TEXT("mode")) == TEXT("Replace") ? BMM_Replace : BMM_Additive);
    M->Node.TranslationSpace = BCS_ComponentSpace; M->Node.RotationSpace = BCS_ComponentSpace; M->Node.ScaleSpace = BCS_ComponentSpace;
    CM.Finalize();
    if (!Schema->TryCreateConnection(PosePin(Prev, EGPD_Output), PosePin(M, EGPD_Input))) { Err = TEXT("animblueprint: pose link failed at ") + JStr(N, TEXT("bone")); return false; }
    UEdGraphPin* ScalePin = M->FindPin(bTranslate ? TEXT("Translation") : TEXT("Scale"));
    if (!ScalePin) { Err = TEXT("animblueprint: ModifyBone has no Scale / Translation pin (PinShownByDefault expected)"); return false; }
    FGraphNodeCreator<UK2Node_VariableGet> CG(*G); UK2Node_VariableGet* GetV = CG.CreateNode(); GetV->NodePosX = X; GetV->NodePosY = 300;
    GetV->VariableReference.SetSelfMember(FName(*JStr(N, TEXT("var")))); CG.Finalize();
    UEdGraphPin* Out = nullptr; for (UEdGraphPin* P : GetV->Pins) if (P->Direction == EGPD_Output) Out = P;
    if (!Out || !Schema->TryCreateConnection(Out, ScalePin)) { Err = TEXT("animblueprint: variable->Scale link failed: ") + JStr(N, TEXT("var")); return false; }
    Prev = M;
  }
  X += 300;
  FGraphNodeCreator<UAnimGraphNode_ComponentToLocalSpace> CC2L(*G); UAnimGraphNode_ComponentToLocalSpace* C2L = CC2L.CreateNode(); C2L->NodePosX = X; CC2L.Finalize();
  if (!Schema->TryCreateConnection(PosePin(Prev, EGPD_Output), PosePin(C2L, EGPD_Input))) { Err = TEXT("animblueprint: link ->ComponentToLocal failed"); return false; }
  Roots[0]->NodePosX = X + 300;
  if (!Schema->TryCreateConnection(PosePin(C2L, EGPD_Output), PosePin(Roots[0], EGPD_Input))) { Err = TEXT("animblueprint: link ->Output Pose failed"); return false; }
  FCompilerResultsLog Results; Results.bSilentMode = false;
  FKismetEditorUtilities::CompileBlueprint(BP, EBlueprintCompileOptions::SkipGarbageCollection, &Results);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN compiled %s errors=%d warnings=%d"), *Path, Results.NumErrors, Results.NumWarnings);
  if (BP->Status == BS_Error || Results.NumErrors > 0) { Err = FString::Printf(TEXT("compile errors (%d) in %s"), Results.NumErrors, *Path); return false; }
  return BPGenAssets::SaveAsset(BP);
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

// "materialinstance": parent + scalars/vectors/textures/switches (switches are static parameters: new permutation)
static bool MakeMaterialInstance(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; UPackage* Pkg = BPGenAssets::MakePackage(JStr(A, TEXT("path")), Name);
  UMaterialInterface* Parent = LoadObject<UMaterialInterface>(nullptr, *JStr(A, TEXT("parent")));
  if (!Parent) { Err = TEXT("materialinstance: parent not found ") + JStr(A, TEXT("parent")); return false; }
  UMaterialInstanceConstant* MI = FindObject<UMaterialInstanceConstant>(Pkg, *Name);
  if (!MI) MI = NewObject<UMaterialInstanceConstant>(Pkg, *Name, RF_Public | RF_Standalone);
  MI->SetParentEditorOnly(Parent);
  MI->ClearParameterValuesEditorOnly();
  const TSharedPtr<FJsonObject>* O = nullptr;
  if (A->TryGetObjectField(TEXT("scalars"), O)) for (const auto& KV : (*O)->Values)
    MI->SetScalarParameterValueEditorOnly(FMaterialParameterInfo(*KV.Key), KV.Value->AsNumber());
  if (A->TryGetObjectField(TEXT("vectors"), O)) for (const auto& KV : (*O)->Values) {
    const TArray<TSharedPtr<FJsonValue>>& V = KV.Value->AsArray();
    if (V.Num() != 4) { Err = TEXT("materialinstance: vector needs 4 values ") + KV.Key; return false; }
    MI->SetVectorParameterValueEditorOnly(FMaterialParameterInfo(*KV.Key), FLinearColor(V[0]->AsNumber(), V[1]->AsNumber(), V[2]->AsNumber(), V[3]->AsNumber()));
  }
  if (A->TryGetObjectField(TEXT("textures"), O)) for (const auto& KV : (*O)->Values) {
    UTexture* T = LoadObject<UTexture>(nullptr, *KV.Value->AsString());
    if (!T) { Err = TEXT("materialinstance: texture not found ") + KV.Value->AsString(); return false; }
    MI->SetTextureParameterValueEditorOnly(FMaterialParameterInfo(*KV.Key), T);
  }
  if (A->TryGetObjectField(TEXT("switches"), O)) {
    FStaticParameterSet Set; MI->GetStaticParameterValues(Set);
    for (const auto& KV : (*O)->Values) {
      FStaticSwitchParameter* P = Set.StaticSwitchParameters.FindByPredicate([&](const FStaticSwitchParameter& S) { return S.ParameterInfo.Name == FName(*KV.Key); });
      if (!P) { Err = TEXT("materialinstance: static switch not found ") + KV.Key; return false; }
      P->Value = KV.Value->AsBool(); P->bOverride = true;
    }
    MI->UpdateStaticPermutation(Set);
  }
  MI->PostEditChange();
  UE_LOG(LogBPGen, Display, TEXT("BPGEN materialinstance %s parent=%s"), *Name, *Parent->GetPathName());
  return BPGenAssets::SaveAsset(MI);
}

static bool MakeCloth(USkeletalMesh* M, const TSharedPtr<FJsonObject>& C, FString& Err);

// which sections of LOD 0 are bound to clothing, and what the user data says (diagnostic)
static void LogClothBinding(USkeletalMesh* M, const TCHAR* Where) {
  FSkeletalMeshLODModel& L = M->GetImportedModel()->LODModels[0];
  FString S;
  for (int32 i = 0; i < L.Sections.Num(); ++i) {
    const FSkelMeshSourceSectionUserData* U = L.UserSectionsData.Find(L.Sections[i].OriginalDataSectionIndex);
    if (L.Sections[i].HasClothingData() || (U && U->HasClothingData()))
      S += FString::Printf(TEXT(" sec%d(orig%d) bound=%d guid=%d mapping=%d asset=%d user=%d"), i, L.Sections[i].OriginalDataSectionIndex,
                           L.Sections[i].HasClothingData() ? 1 : 0, L.Sections[i].ClothingData.AssetGuid.IsValid() ? 1 : 0,
                           L.Sections[i].ClothMappingData.Num(), L.Sections[i].CorrespondClothAssetIndex, U && U->HasClothingData() ? 1 : 0);
  }
  FSkeletalMeshRenderData* R = M->GetResourceForRendering(); int32 RB = 0;
  if (R) for (const FSkeletalMeshLODRenderData& LR : R->LODRenderData) for (const FSkelMeshRenderSection& RS : LR.RenderSections)
    if (RS.ClothingData.AssetGuid.IsValid()) { ++RB; S += FString::Printf(TEXT(" render-mapping=%d render-asset=%d"), RS.ClothMappingData.Num(), RS.CorrespondClothAssetIndex); }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN clothbind %s %s:%s render=%d assets=%d"), *M->GetName(), Where, *S, RB, M->GetMeshClothingAssets().Num());
}

// "skeletalmesh": FBX onto an existing skeleton, no materials/textures/physics from the file; "materials" maps every
// material slot name of the FBX to a material (a slot without an entry is an error - nothing stays on a default)
static bool MakeSkeletalMesh(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = JStr(A, TEXT("path")); FString Dir, Name;
  Path.Split(TEXT("/"), &Dir, &Name, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
  USkeleton* Skel = LoadObject<USkeleton>(nullptr, *JStr(A, TEXT("skeleton")));
  if (!Skel) { Err = TEXT("skeletalmesh: skeleton not found ") + JStr(A, TEXT("skeleton")); return false; }
  FString File = JStr(A, TEXT("file"));
  if (FPaths::IsRelative(File)) File = FPaths::Combine(BPGenAssets::BaseDir, File);
  if (!FPaths::FileExists(File)) { Err = TEXT("skeletalmesh: file missing ") + File; return false; }
  UFbxFactory* F = NewObject<UFbxFactory>(); F->AddToRoot();
  F->SetDetectImportTypeOnImport(false);
  UFbxImportUI* UI = F->ImportUI;
  UI->bImportMesh = true; UI->bImportAsSkeletal = true; UI->MeshTypeToImport = FBXIT_SkeletalMesh; UI->OriginalImportType = FBXIT_SkeletalMesh;
  UI->Skeleton = Skel; UI->bImportAnimations = false; UI->bCreatePhysicsAsset = false; UI->PhysicsAsset = nullptr;
  UI->bImportMaterials = false; UI->bImportTextures = false; UI->bAutomatedImportShouldDetectType = false;
  UI->SkeletalMeshImportData->bImportMorphTargets = false;
  UI->SkeletalMeshImportData->bUseT0AsRefPose = false;
  UAssetImportTask* T = NewObject<UAssetImportTask>(); T->AddToRoot();
  T->Filename = File; T->DestinationPath = Dir; T->DestinationName = Name;
  T->bReplaceExisting = true; T->bAutomated = true; T->bSave = false; T->Factory = F; T->Options = UI;
  FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get().ImportAssetTasks({T});
  T->RemoveFromRoot(); F->RemoveFromRoot();
  USkeletalMesh* M = LoadObject<USkeletalMesh>(nullptr, *(Path + TEXT(".") + Name));
  if (!M) { Err = TEXT("skeletalmesh: import failed ") + File; return false; }
  const TSharedPtr<FJsonObject>* Mats = nullptr; A->TryGetObjectField(TEXT("materials"), Mats);
  FString Slots;
  for (FSkeletalMaterial& SM : M->GetMaterials()) {
    const FString Slot = SM.MaterialSlotName.ToString(); Slots += Slot + TEXT(",");
    FString MP; if (!Mats || !(*Mats)->TryGetStringField(Slot, MP)) { Err = TEXT("skeletalmesh: no material for slot ") + Slot + TEXT(" (slots: ") + Slots + TEXT("...)"); return false; }
    SM.MaterialInterface = LoadObject<UMaterialInterface>(nullptr, *MP);
    if (!SM.MaterialInterface) { Err = TEXT("skeletalmesh: material not found ") + MP; return false; }
  }
  // the mesh's reference pose must match the skeleton's: animations are local bone transforms of the skeleton, so a
  // bone that Blender turned (roll/axis) or moved would bend the garment wrongly in game
  const FReferenceSkeleton& MR = M->GetRefSkeleton(); const FReferenceSkeleton& SR = Skel->GetReferenceSkeleton();
  float WorstPos = 0, WorstRot = 0; FString WorstPosBone, WorstRotBone;
  for (int32 i = 0; i < MR.GetNum(); ++i) {
    const int32 j = SR.FindBoneIndex(MR.GetBoneName(i));
    if (j == INDEX_NONE) { Err = TEXT("skeletalmesh: bone not in skeleton ") + MR.GetBoneName(i).ToString(); return false; }
    const FTransform& TM = MR.GetRefBonePose()[i]; const FTransform& TS = SR.GetRefBonePose()[j];
    const float P = (TM.GetTranslation() - TS.GetTranslation()).Size();
    const float R = FMath::RadiansToDegrees(TM.GetRotation().AngularDistance(TS.GetRotation()));
    if (P > WorstPos) { WorstPos = P; WorstPosBone = MR.GetBoneName(i).ToString() + TEXT(" mesh=") + TM.GetTranslation().ToString() + TEXT(" skel=") + TS.GetTranslation().ToString(); }
    if (R > WorstRot) { WorstRot = R; WorstRotBone = MR.GetBoneName(i).ToString(); }
  }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN skeletalmesh %s refpose maxpos=%.4fcm (%s) maxrot=%.3fdeg (%s)"), *Name, WorstPos, *WorstPosBone, WorstRot, *WorstRotBone);
  M->PostEditChange();
  const TSharedPtr<FJsonObject>* Cloth = nullptr;
  if (A->TryGetObjectField(TEXT("cloth"), Cloth)) {
    if (!MakeCloth(M, *Cloth, Err)) return false;
    LogClothBinding(M, TEXT("bound"));
    M->PostEditChange();
    LogClothBinding(M, TEXT("posteditchange"));
  }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN skeletalmesh %s verts=%d bones=%d slots=%s"), *Name,
    M->GetImportedModel()->LODModels[0].NumVertices, M->GetRefSkeleton().GetNum(), *Slots);
  const bool Ok = BPGenAssets::SaveAsset(M);
  if (A->HasField(TEXT("cloth"))) LogClothBinding(M, TEXT("saved"));
  return Ok;
}

// "cloth": {"slot": <material slot>, "max_distance": <cm>} - that slot's section becomes cloth (UE's clothing tool, as
// "Create Clothing Data from Section" in the editor does). How far each point may leave its skinned position comes from
// the vertex colour's red (0..255 -> 0..max_distance): the mesh author paints the hinge 0 and the free end 255.
// Stiff (metal pull tabs): all constraints at full stiffness, little damping of the swing.
static bool MakeCloth(USkeletalMesh* M, const TSharedPtr<FJsonObject>& C, FString& Err) {
  const FString Slot = JStr(C, TEXT("slot"));
  double MaxDist = 1.0; C->TryGetNumberField(TEXT("max_distance"), MaxDist);
  int32 MatIdx = INDEX_NONE;
  for (int32 i = 0; i < M->GetMaterials().Num(); ++i)
    if (M->GetMaterials()[i].MaterialSlotName.ToString() == Slot) MatIdx = i;
  if (MatIdx == INDEX_NONE) { Err = TEXT("cloth: no material slot ") + Slot; return false; }
  FSkeletalMeshLODModel& Lod = M->GetImportedModel()->LODModels[0];
  int32 Sec = INDEX_NONE;
  for (int32 i = 0; i < Lod.Sections.Num(); ++i) if (Lod.Sections[i].MaterialIndex == MatIdx) { Sec = i; break; }
  if (Sec == INDEX_NONE) { Err = TEXT("cloth: no section with slot ") + Slot; return false; }
  // the section's colours by position, before the section is bound (binding leaves them, but read them first)
  TArray<FVector> Pos; TArray<uint8> Red, Green;
  for (const FSoftSkinVertex& V : Lod.Sections[Sec].SoftVertices) { Pos.Add(V.Position); Red.Add(V.Color.R); Green.Add(V.Color.G); }
  UClothingAssetFactoryBase* F = FModuleManager::LoadModuleChecked<FClothingSystemEditorInterfaceModule>("ClothingSystemEditorInterface").GetClothingAssetFactory();
  FSkeletalMeshClothBuildParams P; P.LodIndex = 0; P.SourceSection = Sec; P.AssetName = TEXT("Cloth_") + Slot; P.bRemoveFromMesh = false;
  UClothingAssetCommon* CA = Cast<UClothingAssetCommon>(F->CreateFromSkeletalMesh(M, P));
  if (!CA) { Err = TEXT("cloth: CreateFromSkeletalMesh failed for slot ") + Slot; return false; }
  M->AddClothingAsset(CA);
  FClothLODDataCommon& LD = CA->LodData[0];
  const TArray<FVector>& PV = LD.PhysicalMeshData.Vertices;
  FPointWeightMap Mask; Mask.Initialize(PV.Num()); Mask.Name = TEXT("MaxDistance");
  Mask.CurrentTarget = (uint8)EWeightMapTargetCommon::MaxDistance; Mask.bEnabled = true;
  int32 Free = 0; TArray<bool> Top; Top.SetNum(PV.Num());
  for (int32 i = 0; i < PV.Num(); ++i) {
    int32 Best = 0; float BestD = MAX_FLT;
    for (int32 j = 0; j < Pos.Num(); ++j) { const float D = FVector::DistSquared(Pos[j], PV[i]); if (D < BestD) { BestD = D; Best = j; } }
    Mask.Values[i] = (float)MaxDist * Red[Best] / 255.f;
    Top[i] = Green[Best] >= 128;
    if (Mask.Values[i] > 0) ++Free;
  }
  LD.PointWeightMaps.Reset();                       // the factory adds an empty mask of its own
  LD.PointWeightMaps.Add(Mask);
  // Backstop (NvCloth has no collision with the mesh itself, a tab fell straight through its slider): per piece (a
  // connected part of the sim mesh) the outward normal = mean normal of the outer face (vertex colour green) minus
  // that of the inner face; every point of the piece gets it as its sim normal, and a big backstop sphere behind it
  // whose surface lies at the piece's lowest rest point along that normal - a plane under the tab that moves with the
  // skinning. A tab can swing up and flip over its slider, but not sink through it or into the leather.
  FClothPhysicalMeshData& PM = LD.PhysicalMeshData;
  TArray<int32> Root; Root.SetNum(PV.Num());
  for (int32 i = 0; i < PV.Num(); ++i) Root[i] = i;
  auto Find = [&Root](int32 i) { while (Root[i] != i) i = Root[i] = Root[Root[i]]; return i; };
  for (int32 t = 0; t + 2 < PM.Indices.Num(); t += 3)
    for (int32 k = 1; k < 3; ++k) Root[Find(PM.Indices[t + k])] = Find(PM.Indices[t]);
  TMap<int32, FVector> Out; TMap<int32, float> Low;
  for (int32 i = 0; i < PV.Num(); ++i) Out.FindOrAdd(Find(i)) += Top[i] ? PM.Normals[i] : -PM.Normals[i];
  for (auto& KV : Out) KV.Value = KV.Value.GetSafeNormal();
  for (int32 i = 0; i < PV.Num(); ++i) { float& Lo = Low.FindOrAdd(Find(i), MAX_FLT); Lo = FMath::Min(Lo, FVector::DotProduct(PV[i], Out[Find(i)])); }
  const float BackR = 100.f;                         // cm; flat enough: a tab flipped over (4 cm off) is 0.8 mm off the plane
  FPointWeightMap BD, BR; BD.Initialize(PV.Num()); BR.Initialize(PV.Num());
  BD.Name = TEXT("BackstopDistance"); BD.CurrentTarget = (uint8)EWeightMapTargetCommon::BackstopDistance; BD.bEnabled = true;
  BR.Name = TEXT("BackstopRadius"); BR.CurrentTarget = (uint8)EWeightMapTargetCommon::BackstopRadius; BR.bEnabled = true;
  int32 Bad = 0;
  for (int32 i = 0; i < PV.Num(); ++i) {
    const int32 Pc = Find(i); PM.Normals[i] = Out[Pc];
    BR.Values[i] = BackR; BD.Values[i] = BackR + FVector::DotProduct(PV[i], Out[Pc]) - Low[Pc];
    if (Out[Pc].IsNearlyZero()) ++Bad;
  }
  if (Bad) { Err = FString::Printf(TEXT("cloth: %d points without an outward normal (vertex colour green: outer face 1, inner 0)"), Bad); return false; }
  LD.PointWeightMaps.Add(BD); LD.PointWeightMaps.Add(BR);
  CA->ApplyParameterMasks();
  if (UClothConfigNv* Cfg = CA->GetClothConfig<UClothConfigNv>()) {
    for (FClothConstraintSetupNv* K : {&Cfg->VerticalConstraint, &Cfg->HorizontalConstraint, &Cfg->BendConstraint, &Cfg->ShearConstraint}) {
      K->Stiffness = 1.f; K->StiffnessMultiplier = 1.f;
    }
    Cfg->Damping = FVector(0.2f);
  }
  // Bind and record the binding in the section's user data inside ONE outer edit scope, as the editor's "Apply
  // Clothing" does. BindToSkeletalMesh opens its own scope; alone, the rebuild at its end ran before the user data
  // knew of the binding and dropped it (in game nothing swung; the render section had the asset's guid but no
  // render-to-sim mapping). With the outer scope the rebuild comes after, backs the binding up and restores it.
  FScopedSkeletalMeshPostEditChange Outer(M);
  if (!CA->BindToSkeletalMesh(M, 0, Sec, 0)) { Err = TEXT("cloth: BindToSkeletalMesh failed for slot ") + Slot; return false; }
  {
    FSkeletalMeshLODModel& L = M->GetImportedModel()->LODModels[0];
    FSkelMeshSourceSectionUserData& U = L.UserSectionsData.FindOrAdd(L.Sections[Sec].OriginalDataSectionIndex);
    int32 AssetIndex = INDEX_NONE; M->GetMeshClothingAssets().Find(CA, AssetIndex);
    U.CorrespondClothAssetIndex = AssetIndex;
    U.ClothingData.AssetGuid = CA->GetAssetGuid();
    U.ClothingData.AssetLodIndex = 0;
  }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN cloth %s slot=%s section=%d particles=%d free=%d max=%.2fcm pieces=%d"), *M->GetName(), *Slot, Sec, PV.Num(), Free, MaxDist, Out.Num());
  return true;
}

// "skeleton": a stand-in for a game skeleton the kit does not have (animation blueprints need a target skeleton to compile).
// Empty (no bones) and only created when nothing is at the path - a real skeleton is never touched. The mod pak only holds
// Mod/AltUI, so the stand-in never ships; in the game the reference resolves to the real skeleton by path.
static bool MakeSkeletonStub(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = JStr(A, TEXT("path")); FString Dir, Name;
  Path.Split(TEXT("/"), &Dir, &Name, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
  if (LoadObject<USkeleton>(nullptr, *(Path + TEXT(".") + Name), nullptr, LOAD_NoWarn | LOAD_Quiet)) return true;
  UPackage* Pkg = CreatePackage(*Path);
  USkeleton* S = NewObject<USkeleton>(Pkg, *Name, RF_Public | RF_Standalone);
  if (!S) { Err = TEXT("skeleton: cannot create ") + Path; return false; }
  FAssetRegistryModule::AssetCreated(S); Pkg->MarkPackageDirty();
  UE_LOG(LogBPGen, Display, TEXT("BPGEN skeleton stub %s"), *Path);
  return BPGenAssets::SaveAsset(S);
}

// "animsequence_stub": a stand-in for a game animation the kit does not have (a child ABP's override needs an asset to point at).
// Empty, only created when nothing is at the path, never packed (the pak holds Mod/AltUI only); in the game the reference resolves
// to the real animation by path.
static bool MakeAnimSequenceStub(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = JStr(A, TEXT("path")); FString Dir, Name;
  Path.Split(TEXT("/"), &Dir, &Name, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
  if (LoadObject<UAnimSequenceBase>(nullptr, *(Path + TEXT(".") + Name), nullptr, LOAD_NoWarn | LOAD_Quiet)) return true;
  USkeleton* Skel = Cast<USkeleton>(BPGenTypes::LoadObj(JStr(A, TEXT("skeleton"))));
  if (!Skel) { Err = TEXT("animsequence_stub: skeleton not found ") + JStr(A, TEXT("skeleton")); return false; }
  UPackage* Pkg = CreatePackage(*Path);
  UAnimSequence* S = NewObject<UAnimSequence>(Pkg, *Name, RF_Public | RF_Standalone);
  if (!S) { Err = TEXT("animsequence_stub: cannot create ") + Path; return false; }
  S->SetSkeleton(Skel);
  FAssetRegistryModule::AssetCreated(S); Pkg->MarkPackageDirty();
  UE_LOG(LogBPGen, Display, TEXT("BPGEN animsequence stub %s"), *Path);
  return BPGenAssets::SaveAsset(S);
}

// "animstub": a stand-in for a game animation blueprint (Jodi_Anim) that carries sequence players whose compiled properties have the
// names of the game's nodes (the child's cooked CDO addresses the game's property by name). The compiler numbers the properties per node
// type (AnimGraphNode_SequencePlayer, _1, _2, ...), so the stub gets as many players as the highest wanted number needs and checks the
// names after compiling. Players chained by Two-Way Blends into Output Pose - isolated nodes are pruned. Only created when nothing is at
// the path, never packed.
static bool MakeAnimStub(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = JStr(A, TEXT("path")); FString Dir, Name;
  Path.Split(TEXT("/"), &Dir, &Name, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
  if (LoadObject<UAnimBlueprint>(nullptr, *(Path + TEXT(".") + Name), nullptr, LOAD_NoWarn | LOAD_Quiet)) return true;
  USkeleton* Skel = Cast<USkeleton>(BPGenTypes::LoadObj(JStr(A, TEXT("skeleton"))));
  if (!Skel) { Err = TEXT("animstub: skeleton not found ") + JStr(A, TEXT("skeleton")); return false; }
  UPackage* Pkg = CreatePackage(*Path);
  UAnimBlueprint* BP = Cast<UAnimBlueprint>(FKismetEditorUtilities::CreateBlueprint(UAnimInstance::StaticClass(), Pkg, *Name, BPTYPE_Normal,
      UAnimBlueprint::StaticClass(), UAnimBlueprintGeneratedClass::StaticClass(), FName("BPGen")));
  if (!BP) { Err = TEXT("animstub: CreateBlueprint failed ") + Path; return false; }
  BP->TargetSkeleton = Skel;
  UEdGraph* G = nullptr; for (UEdGraph* FG : BP->FunctionGraphs) if (FG->IsA<UAnimationGraph>()) G = FG;
  TArray<UAnimGraphNode_Root*> Roots; if (G) G->GetNodesOfClass(Roots);
  if (!G || Roots.Num() == 0) { Err = TEXT("animstub: no AnimGraph / Output Pose in ") + Path; return false; }
  const UEdGraphSchema* Schema = G->GetSchema(); int32 X = -1200; UEdGraphNode* Prev = nullptr;
  const auto* Players = JArr(A, TEXT("players"));
  if (!Players || Players->Num() == 0) { Err = TEXT("animstub: no players"); return false; }
  int32 Count = 0;
  for (const auto& PV : *Players) {   // "AnimGraphNode_SequencePlayer_<n>" needs n + 1 players, the bare name one
    FString L, R; const FString NodeName = JStr(PV->AsObject(), TEXT("name"));
    Count = FMath::Max(Count, NodeName.Split(TEXT("_"), &L, &R, ESearchCase::IgnoreCase, ESearchDir::FromEnd) && R.IsNumeric() ? FCString::Atoi(*R) + 1 : 1);
  }
  UAnimSequenceBase* Seq = nullptr;   // a player without a sequence fails to compile: every player gets the first given asset
  for (const auto& PV : *Players) if (!Seq && !JStr(PV->AsObject(), TEXT("asset")).IsEmpty()) Seq = Cast<UAnimSequenceBase>(BPGenTypes::LoadObj(JStr(PV->AsObject(), TEXT("asset"))));
  if (!Seq) { Err = TEXT("animstub: no loadable asset among the players"); return false; }
  for (int32 i = 0; i < Count; ++i) {
    FGraphNodeCreator<UAnimGraphNode_SequencePlayer> C(*G); UAnimGraphNode_SequencePlayer* N = C.CreateNode(); N->NodePosX = X; N->NodePosY = 200 + 150 * i;
    N->Node.Sequence = Seq; C.Finalize();
    if (!Prev) { Prev = N; continue; }
    X += 300;
    FGraphNodeCreator<UAnimGraphNode_TwoWayBlend> CB(*G); UAnimGraphNode_TwoWayBlend* B = CB.CreateNode(); B->NodePosX = X; CB.Finalize();
    if (!Schema->TryCreateConnection(PosePin(Prev, EGPD_Output), B->FindPin(TEXT("A"))) || !Schema->TryCreateConnection(PosePin(N, EGPD_Output), B->FindPin(TEXT("B")))) {
      Err = TEXT("animstub: blend link failed"); return false; }
    Prev = B;
  }
  Roots[0]->NodePosX = X + 300;
  if (!Schema->TryCreateConnection(PosePin(Prev, EGPD_Output), PosePin(Roots[0], EGPD_Input))) { Err = TEXT("animstub: link ->Output Pose failed"); return false; }
  FCompilerResultsLog Results; Results.bSilentMode = false;
  FKismetEditorUtilities::CompileBlueprint(BP, EBlueprintCompileOptions::SkipGarbageCollection, &Results);
  if (BP->Status == BS_Error || Results.NumErrors > 0) { Err = FString::Printf(TEXT("compile errors (%d) in %s"), Results.NumErrors, *Path); return false; }
  for (const auto& PV : *Players) {   // the compiled class must carry the properties under the given names
    const FString NodeName = JStr(PV->AsObject(), TEXT("name"));
    if (!FindFProperty<FStructProperty>(BP->GeneratedClass, *NodeName)) {
      FString Have; for (TFieldIterator<FStructProperty> It(BP->GeneratedClass, EFieldIteratorFlags::ExcludeSuper); It; ++It) Have += It->GetName() + TEXT(" ");
      Err = TEXT("animstub: no property ") + NodeName + TEXT(" after compiling ") + Path + TEXT(" (has: ") + Have + TEXT(")"); return false; }
  }
  FAssetRegistryModule::AssetCreated(BP);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN animstub %s"), *Path);
  return BPGenAssets::SaveAsset(BP);
}

// "animchild": a child of an animation blueprint that only swaps the assets of named parent nodes (ParentAssetOverrides by the parent
// node's GUID; the compiler patches them into the child's CDO). At runtime state machines, notifies and sync groups come from the root
// class (UAnimBlueprintGeneratedClass::GetRootClass), so the child carries nothing but the swapped assets.
static bool MakeAnimChild(const TSharedPtr<FJsonObject>& A, FString& Err) {
  FString Name; const FString Path = JStr(A, TEXT("path")); UPackage* Pkg = BPGenAssets::MakePackage(Path, Name);
  if (FindObject<UAnimBlueprint>(Pkg, *Name)) { Err = TEXT("animchild: exists ") + Path; return false; }
  const FString ParentPath = JStr(A, TEXT("parent")); FString PDir, PName; ParentPath.Split(TEXT("/"), &PDir, &PName, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
  UAnimBlueprint* Parent = LoadObject<UAnimBlueprint>(nullptr, *(ParentPath + TEXT(".") + PName));
  if (!Parent || !Parent->GeneratedClass) { Err = TEXT("animchild: parent not found ") + ParentPath; return false; }
  USkeleton* Skel = Cast<USkeleton>(BPGenTypes::LoadObj(JStr(A, TEXT("skeleton"))));
  if (!Skel) { Err = TEXT("animchild: skeleton not found ") + JStr(A, TEXT("skeleton")); return false; }
  UAnimBlueprint* BP = Cast<UAnimBlueprint>(FKismetEditorUtilities::CreateBlueprint(Parent->GeneratedClass, Pkg, *Name, BPTYPE_Normal,
      UAnimBlueprint::StaticClass(), UAnimBlueprintGeneratedClass::StaticClass(), FName("BPGen")));
  if (!BP) { Err = TEXT("animchild: CreateBlueprint failed ") + Path; return false; }
  BP->TargetSkeleton = Skel;
  TArray<UAnimGraphNode_Base*> ParentNodes; FBlueprintEditorUtils::GetAllNodesOfClass<UAnimGraphNode_Base>(Parent, ParentNodes);
  const TSharedPtr<FJsonObject>* Ov = nullptr;
  if (!A->TryGetObjectField(TEXT("overrides"), Ov) || !Ov) { Err = TEXT("animchild: no overrides"); return false; }
  UAnimBlueprintGeneratedClass* PClass = Cast<UAnimBlueprintGeneratedClass>(Parent->GeneratedClass);
  for (const auto& KV : (*Ov)->Values) {   // the key is the compiled property name of the parent node
    UAnimGraphNode_Base* const* Found = ParentNodes.FindByPredicate([&](UAnimGraphNode_Base* N) {
      FStructProperty* P = PClass ? PClass->GetPropertyForNode<FAnimNode_Base>(N) : nullptr; return P && P->GetName() == KV.Key; });
    if (!Found) { Err = TEXT("animchild: parent node not found ") + KV.Key; return false; }
    UAnimationAsset* Asset = Cast<UAnimationAsset>(BPGenTypes::LoadObj(KV.Value->AsString()));
    if (!Asset) { Err = TEXT("animchild: asset not found ") + KV.Value->AsString(); return false; }
    BP->ParentAssetOverrides.Add(FAnimParentNodeAssetOverride((*Found)->NodeGuid, Asset));
  }
  FCompilerResultsLog Results; Results.bSilentMode = false;
  FKismetEditorUtilities::CompileBlueprint(BP, EBlueprintCompileOptions::SkipGarbageCollection, &Results);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN compiled %s errors=%d warnings=%d"), *Path, Results.NumErrors, Results.NumWarnings);
  if (BP->Status == BS_Error || Results.NumErrors > 0) { Err = FString::Printf(TEXT("compile errors (%d) in %s"), Results.NumErrors, *Path); return false; }
  return BPGenAssets::SaveAsset(BP);
}

// "animimport": an animation FBX (Blender, docs/specs/2026-10-06-anim-pipeline-design.md) onto an existing skeleton as AnimSequence, then
// the game's curves ({name: [[t, v], ...]}), sync markers ([[name, t]]) and notifies by name ([[name, t]], like the game's "Footstep" -
// no notify class, Jodi_Anim handles AnimNotify_<name>). Logs pelvis / foot transforms at time 0 for the round trip check.
static bool MakeAnimImport(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = JStr(A, TEXT("path")); FString Dir, Name;
  Path.Split(TEXT("/"), &Dir, &Name, ESearchCase::IgnoreCase, ESearchDir::FromEnd);
  USkeleton* Skel = LoadObject<USkeleton>(nullptr, *JStr(A, TEXT("skeleton")));
  if (!Skel) { Err = TEXT("animimport: skeleton not found ") + JStr(A, TEXT("skeleton")); return false; }
  FString File = JStr(A, TEXT("fbx"));
  if (FPaths::IsRelative(File)) File = FPaths::Combine(BPGenAssets::BaseDir, File);
  if (!FPaths::FileExists(File)) { Err = TEXT("animimport: file missing ") + File; return false; }
  UFbxFactory* F = NewObject<UFbxFactory>(); F->AddToRoot(); F->SetDetectImportTypeOnImport(false);
  UFbxImportUI* UI = F->ImportUI;
  UI->bImportMesh = false; UI->bImportAsSkeletal = true; UI->MeshTypeToImport = FBXIT_Animation; UI->OriginalImportType = FBXIT_Animation;
  UI->Skeleton = Skel; UI->bImportAnimations = true; UI->bCreatePhysicsAsset = false; UI->bImportMaterials = false; UI->bImportTextures = false;
  UI->bAutomatedImportShouldDetectType = false;
  UI->AnimSequenceImportData->AnimationLength = FBXALIT_ExportedTime; UI->AnimSequenceImportData->bRemoveRedundantKeys = false;
  UI->AnimSequenceImportData->bImportCustomAttribute = false; UI->AnimSequenceImportData->bDeleteExistingMorphTargetCurves = false;
  UI->AnimSequenceImportData->bUseDefaultSampleRate = false; UI->AnimSequenceImportData->CustomSampleRate = 30;
  UAssetImportTask* T = NewObject<UAssetImportTask>(); T->AddToRoot();
  T->Filename = File; T->DestinationPath = Dir; T->DestinationName = Name;
  T->bReplaceExisting = true; T->bAutomated = true; T->bSave = false; T->Factory = F; T->Options = UI;
  FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get().ImportAssetTasks({T});
  UAnimSequence* S = LoadObject<UAnimSequence>(nullptr, *(Path + TEXT(".") + Name), nullptr, LOAD_NoWarn | LOAD_Quiet);
  if (!S) for (const FString& OP : T->ImportedObjectPaths) if (UAnimSequence* AS = LoadObject<UAnimSequence>(nullptr, *OP, nullptr, LOAD_NoWarn | LOAD_Quiet)) S = AS;
  T->RemoveFromRoot(); F->RemoveFromRoot();
  if (!S) { Err = TEXT("animimport: no AnimSequence from ") + File; return false; }
  if (S->GetName() != Name) { Err = TEXT("animimport: imported as ") + S->GetPathName() + TEXT(", expected ") + Path; return false; }
  // curves (the game's movement data); every key time clamped into the sequence
  const TSharedPtr<FJsonObject>* Curves = nullptr;
  if (A->TryGetObjectField(TEXT("curves"), Curves)) for (const auto& KV : (*Curves)->Values) {
    TArray<float> Ts, Vs; TArray<FString> Modes;
    for (const auto& R : KV.Value->AsArray()) { const auto& P = R->AsArray(); Ts.Add(FMath::Clamp((float)P[0]->AsNumber(), 0.f, S->SequenceLength)); Vs.Add((float)P[1]->AsNumber()); Modes.Add(P.Num() > 2 ? P[2]->AsString() : TEXT("linear")); }
    UAnimationBlueprintLibrary::AddCurve(S, FName(*KV.Key), ERawCurveTrackTypes::RCT_Float, false);
    UAnimationBlueprintLibrary::AddFloatCurveKeys(S, FName(*KV.Key), Ts, Vs);
    for (FFloatCurve& C : S->RawCurveData.FloatCurves) if (C.Name.DisplayName == FName(*KV.Key)) {   // interpolation per key (the game's FootPhase steps)
      for (int32 i = 0; i < C.FloatCurve.Keys.Num() && i < Modes.Num(); ++i)
        C.FloatCurve.Keys[i].InterpMode = Modes[i] == TEXT("constant") ? RCIM_Constant : Modes[i] == TEXT("cubic") ? RCIM_Cubic : RCIM_Linear;
    }
  }
  if (const auto* Markers = JArr(A, TEXT("markers"))) {
    UAnimationBlueprintLibrary::AddAnimationNotifyTrack(S, TEXT("Markers"));
    for (const auto& M : *Markers) { const auto& P = M->AsArray(); UAnimationBlueprintLibrary::AddAnimationSyncMarker(S, FName(*P[0]->AsString()), (float)P[1]->AsNumber(), TEXT("Markers")); }
  }
  if (const auto* Notes = JArr(A, TEXT("notifies"))) {
    if (S->AnimNotifyTracks.Num() == 0) S->AnimNotifyTracks.Add(FAnimNotifyTrack(TEXT("1"), FLinearColor::White));
    for (const auto& M : *Notes) {
      const auto& P = M->AsArray(); FAnimNotifyEvent E; E.NotifyName = FName(*P[0]->AsString());
      E.Link(S, (float)P[1]->AsNumber()); E.TriggerTimeOffset = GetTriggerTimeOffsetForType(S->CalculateOffsetForNotify(E.GetTime()));
      E.TrackIndex = 0; S->Notifies.Add(E);
    }
    S->RefreshCacheData();
  }
  S->MarkPackageDirty(); S->PostEditChange();
  FString Probe;
  for (const TCHAR* B : {TEXT("pelvis"), TEXT("foot_l"), TEXT("calf_r")}) {
    const int32 Track = S->GetAnimationTrackNames().IndexOfByKey(FName(B)); if (Track == INDEX_NONE) continue;
    FTransform X; S->GetBoneTransform(X, Track, 0.f, true);
    const int32 SI = Skel->GetReferenceSkeleton().FindBoneIndex(FName(B));
    Probe += FString::Printf(TEXT(" %s t=%s r=%s ref=%s"), B, *X.GetTranslation().ToString(), *X.GetRotation().ToString(),
      SI == INDEX_NONE ? TEXT("-") : *Skel->GetReferenceSkeleton().GetRefBonePose()[SI].GetTranslation().ToString());
  }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN animimport %s len=%.4f frames=%d curves=%d markers=%d notifies=%d%s"), *Name, S->SequenceLength, S->GetRawNumberOfFrames(),
    S->RawCurveData.FloatCurves.Num(), S->AuthoredSyncMarkers.Num(), S->Notifies.Num(), *Probe);
  return BPGenAssets::SaveAsset(S);
}

bool BPGenAssets::Process(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Type = JStr(A, TEXT("type"));
  UE_LOG(LogBPGen, Display, TEXT("BPGEN process %s %s"), *Type, *JStr(A, TEXT("path")));
  if (Type == TEXT("enum")) return MakeEnum(A, Err);
  if (Type == TEXT("struct")) return MakeStruct(A, Err);
  if (Type == TEXT("datatable")) return MakeDataTable(A, Err);
  if (Type == TEXT("texture")) return MakeTexture(A, Err);
  if (Type == TEXT("materialinstance")) return MakeMaterialInstance(A, Err);
  if (Type == TEXT("skeletalmesh")) return MakeSkeletalMesh(A, Err);
  if (Type == TEXT("animblueprint")) return MakeAnimBlueprint(A, Err);
  if (Type == TEXT("skeleton")) return MakeSkeletonStub(A, Err);
  if (Type == TEXT("animsequence_stub")) return MakeAnimSequenceStub(A, Err);
  if (Type == TEXT("animstub")) return MakeAnimStub(A, Err);
  if (Type == TEXT("animchild")) return MakeAnimChild(A, Err);
  if (Type == TEXT("animimport")) return MakeAnimImport(A, Err);
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
  // components: every SCS node with the template properties that differ from the component class's defaults
  if (UBlueprintGeneratedClass* BPGC = Cast<UBlueprintGeneratedClass>(C)) if (BPGC->SimpleConstructionScript)
    for (USCS_Node* N : BPGC->SimpleConstructionScript->GetAllNodes()) {
      USCS_Node* PN = BPGC->SimpleConstructionScript->FindParentNode(N);
      UE_LOG(LogBPGen, Display, TEXT("DUMP COMP %s %s parent=%s"), *N->GetVariableName().ToString(), *N->ComponentClass->GetName(), PN ? *PN->GetVariableName().ToString() : TEXT("-"));
      UObject* T = N->ComponentTemplate; UObject* Def = N->ComponentClass->GetDefaultObject();
      for (TFieldIterator<FProperty> It(N->ComponentClass); It; ++It) {
        if (It->Identical_InContainer(T, Def)) continue;
        FString V; It->ExportTextItem(V, It->ContainerPtrToValuePtr<void>(T), nullptr, T, PPF_None);
        UE_LOG(LogBPGen, Display, TEXT("DUMP COMP %s.%s %s"), *N->GetVariableName().ToString(), *It->GetName(), *V);
      }
    }
  UObject* CDO = C->GetDefaultObject();
  for (TFieldIterator<FProperty> It(C); It; ++It) {
    if (It->GetName() != TEXT("InitialLifeSpan") && It->GetName() != TEXT("ViewPitchMin") && It->GetName() != TEXT("ViewPitchMax")) continue;
    FString V; It->ExportTextItem(V, It->ContainerPtrToValuePtr<void>(CDO), nullptr, CDO, PPF_None);
    UE_LOG(LogBPGen, Display, TEXT("DUMP DEFAULT %s %s"), *It->GetName(), *V);
  }
}

bool BPGenAssets::ExportFbx(const FString& ObjectPath, const FString& File) {
  UObject* Obj = LoadObject<UObject>(nullptr, *ObjectPath);
  if (!Obj) { UE_LOG(LogBPGen, Error, TEXT("BPGEN exportfbx: not found %s"), *ObjectPath); return false; }
  UAssetExportTask* T = NewObject<UAssetExportTask>();
  T->Object = Obj; T->Filename = File; T->bSelected = false; T->bReplaceIdentical = true;
  T->bPrompt = false; T->bAutomated = true; T->bUseFileArchive = false; T->bWriteEmptyFiles = false;
  const bool Ok = UExporter::RunAssetExportTask(T);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN exportfbx %s -> %s %s"), *ObjectPath, *File, Ok ? TEXT("ok") : TEXT("FAILED"));
  return Ok;
}

void BPGenAssets::DumpCloth(const FString& MeshPath) {
  USkeletalMesh* M = LoadObject<USkeletalMesh>(nullptr, *MeshPath);
  if (!M) { UE_LOG(LogBPGen, Error, TEXT("DUMPCLOTH %s not found"), *MeshPath); return; }
  const FSkeletalMeshLODModel& Lod = M->GetImportedModel()->LODModels[0];
  for (int32 s = 0; s < Lod.Sections.Num(); ++s)
    if (Lod.Sections[s].HasClothingData())
      UE_LOG(LogBPGen, Display, TEXT("DUMPCLOTH %s section %d cloth lod %d verts %d mapping %d"), *M->GetName(), s,
        Lod.Sections[s].ClothingData.AssetLodIndex, Lod.Sections[s].SoftVertices.Num(), Lod.Sections[s].ClothMappingData.Num());
  for (UClothingAssetBase* B : M->GetMeshClothingAssets()) {
    UClothingAssetCommon* CA = Cast<UClothingAssetCommon>(B); if (!CA) continue;
    UE_LOG(LogBPGen, Display, TEXT("DUMPCLOTH %s asset %s lods %d physasset %s refbone %d usedbones %d"), *M->GetName(), *CA->GetName(),
      CA->LodData.Num(), CA->PhysicsAsset ? *CA->PhysicsAsset->GetName() : TEXT("-"), CA->ReferenceBoneIndex, CA->UsedBoneIndices.Num());
    for (auto& KV : CA->ClothConfigs) {
      UClothConfigBase* C = KV.Value; if (!C) continue;
      FString Props;
      for (TFieldIterator<FProperty> It(C->GetClass()); It; ++It) {
        FString V; It->ExportTextItem(V, It->ContainerPtrToValuePtr<void>(C), nullptr, C, PPF_None);
        Props += It->GetName() + TEXT("=") + V + TEXT(" ");
      }
      UE_LOG(LogBPGen, Display, TEXT("DUMPCLOTH %s config %s %s"), *M->GetName(), *KV.Key.ToString(), *Props);
    }
    for (int32 l = 0; l < CA->LodData.Num(); ++l) {
      const FClothPhysicalMeshData& PM = CA->LodData[l].PhysicalMeshData;
      UE_LOG(LogBPGen, Display, TEXT("DUMPCLOTH %s lod %d particles %d fixed %d masks %d"), *M->GetName(), l, PM.Vertices.Num(), PM.NumFixedVerts, CA->LodData[l].PointWeightMaps.Num());
      for (const auto& W : PM.WeightMaps) {
        float Mn = MAX_FLT, Mx = -MAX_FLT; int32 NZ = 0;
        for (float x : W.Value.Values) { Mn = FMath::Min(Mn, x); Mx = FMath::Max(Mx, x); if (x > 0) ++NZ; }
        UE_LOG(LogBPGen, Display, TEXT("DUMPCLOTH %s lod %d weightmap %u n=%d nonzero=%d min=%.3f max=%.3f"), *M->GetName(), l, W.Key, W.Value.Values.Num(), NZ, Mn, Mx);
      }
    }
  }
}

// A game world with just this mesh: ticked 3 s at 60 Hz, the first second still, then moved to and fro (inertia).
// Reports per clothing asset how far the simulated particles are from where the skinning (ref pose) puts them.
void BPGenAssets::SimCloth(const FString& MeshPath) {
  USkeletalMesh* M = LoadObject<USkeletalMesh>(nullptr, *MeshPath);
  if (!M) { UE_LOG(LogBPGen, Error, TEXT("SIMCLOTH %s not found"), *MeshPath); return; }
  UWorld* W = UWorld::CreateWorld(EWorldType::Game, false);
  FWorldContext& Ctx = GEngine->CreateNewWorldContext(EWorldType::Game); Ctx.SetCurrentWorld(W);
  W->InitializeActorsForPlay(FURL()); W->BeginPlay();
  AActor* A = W->SpawnActor<AActor>();
  USkeletalMeshComponent* C = NewObject<USkeletalMeshComponent>(A);
  A->SetRootComponent(C); C->SetSkeletalMesh(M); C->RegisterComponent();
  UE_LOG(LogBPGen, Display, TEXT("SIMCLOTH %s active=%d canSim=%d"), *M->GetName(), M->HasActiveClothingAssets() ? 1 : 0, C->CanSimulateClothing() ? 1 : 0);
  for (int32 f = 0; f < 180; ++f) {
    if (f >= 60) A->SetActorLocation(FVector(FMath::Sin(f * 0.25f) * 20.f, 0.f, 0.f));
    W->Tick(LEVELTICK_All, 1.f / 60.f);
    if (f % 30 == 29 || f == 0) {
      const TMap<int32, FClothSimulData> D = C->GetCurrentClothingData_GameThread();
      for (const auto& KV : D) {
        UClothingAssetCommon* CA = M->GetMeshClothingAssets().IsValidIndex(KV.Key) ? Cast<UClothingAssetCommon>(M->GetMeshClothingAssets()[KV.Key]) : nullptr;
        if (!CA) continue;
        const TArray<FVector>& Rest = CA->LodData[0].PhysicalMeshData.Vertices;
        float Mx = 0, Sum = 0; const int32 N = FMath::Min(Rest.Num(), KV.Value.Positions.Num());
        // positions come in the sim's space (component / reference bone); compare relative to particle 0 (a fixed one
        // or not - the spread of the offsets is what shows movement)
        for (int32 i = 0; i < N; ++i) { const float d = FVector::Dist(KV.Value.Positions[i], Rest[i]); Mx = FMath::Max(Mx, d); Sum += d; }
        UE_LOG(LogBPGen, Display, TEXT("SIMCLOTH %s frame %d asset %d particles %d offset max %.3f mean %.3f cm"), *M->GetName(), f, KV.Key, N, Mx, N ? Sum / N : 0);
      }
      if (D.Num() == 0) UE_LOG(LogBPGen, Display, TEXT("SIMCLOTH %s frame %d no cloth data"), *M->GetName(), f);
    }
  }
  W->DestroyWorld(false); GEngine->DestroyWorldContext(W);
}

void BPGenAssets::DumpMaterial(const FString& MaterialPath) {
  UMaterialInterface* M = LoadObject<UMaterialInterface>(nullptr, *MaterialPath);
  if (!M) { UE_LOG(LogBPGen, Error, TEXT("DUMPMAT ERROR not found %s"), *MaterialPath); return; }
  UMaterialInterface* Parent = M; while (UMaterialInstance* MI = Cast<UMaterialInstance>(Parent)) Parent = MI->Parent;
  UE_LOG(LogBPGen, Display, TEXT("DUMPMAT %s base %s"), *MaterialPath, Parent ? *Parent->GetPathName() : TEXT("-"));
  TArray<FMaterialParameterInfo> Infos; TArray<FGuid> Ids;
  M->GetAllScalarParameterInfo(Infos, Ids);
  for (const FMaterialParameterInfo& I : Infos) { float V = 0; M->GetScalarParameterValue(I, V);
    UE_LOG(LogBPGen, Display, TEXT("DUMPMAT %s scalar %s %g"), *MaterialPath, *I.Name.ToString(), V); }
  Infos.Reset(); Ids.Reset(); M->GetAllVectorParameterInfo(Infos, Ids);
  for (const FMaterialParameterInfo& I : Infos) { FLinearColor V; M->GetVectorParameterValue(I, V);
    UE_LOG(LogBPGen, Display, TEXT("DUMPMAT %s vector %s %s"), *MaterialPath, *I.Name.ToString(), *V.ToString()); }
  Infos.Reset(); Ids.Reset(); M->GetAllTextureParameterInfo(Infos, Ids);
  for (const FMaterialParameterInfo& I : Infos) { UTexture* V = nullptr; M->GetTextureParameterValue(I, V);
    UE_LOG(LogBPGen, Display, TEXT("DUMPMAT %s texture %s %s"), *MaterialPath, *I.Name.ToString(), V ? *V->GetPathName() : TEXT("None")); }
  Infos.Reset(); Ids.Reset(); M->GetAllStaticSwitchParameterInfo(Infos, Ids);
  for (const FMaterialParameterInfo& I : Infos) { bool V = false; FGuid G; M->GetStaticSwitchParameterValue(I, V, G);
    UE_LOG(LogBPGen, Display, TEXT("DUMPMAT %s switch %s %d"), *MaterialPath, *I.Name.ToString(), V ? 1 : 0); }
}

// DUMPGRAPH lines: every expression of a material (index, class, parameter name / mask) and what feeds its inputs,
// then what feeds the material's own inputs - enough to see which texture channel goes where
void BPGenAssets::DumpMaterialGraph(const FString& MaterialPath) {
  UMaterial* M = LoadObject<UMaterial>(nullptr, *MaterialPath);
  if (!M) { UE_LOG(LogBPGen, Error, TEXT("DUMPGRAPH ERROR not a material %s"), *MaterialPath); return; }
  TArray<UMaterialExpression*>& Ex = M->Expressions;
  auto Id = [&](UMaterialExpression* E) { return Ex.IndexOfByKey(E); };
  for (int32 i = 0; i < Ex.Num(); ++i) {
    UMaterialExpression* E = Ex[i]; FString Extra;
    if (auto* P = Cast<UMaterialExpressionParameter>(E)) Extra = P->ParameterName.ToString();
    if (auto* T = Cast<UMaterialExpressionTextureSampleParameter>(E)) Extra = T->ParameterName.ToString();
    if (auto* K = Cast<UMaterialExpressionComponentMask>(E)) Extra = FString::Printf(TEXT("mask %d%d%d%d"), K->R, K->G, K->B, K->A);
    FString Ins;
    for (FExpressionInput* In : E->GetInputs()) if (In && In->Expression)
      Ins += FString::Printf(TEXT(" %s<-%d.%d"), *In->InputName.ToString(), Id(In->Expression), In->OutputIndex);
    UE_LOG(LogBPGen, Display, TEXT("DUMPGRAPH %d %s %s |%s"), i, *E->GetClass()->GetName(), *Extra, *Ins);
  }
  for (int32 p = 0; p < MP_MAX; ++p) {
    FExpressionInput* In = M->GetExpressionInputForProperty((EMaterialProperty)p);
    if (In && In->Expression) UE_LOG(LogBPGen, Display, TEXT("DUMPGRAPH out %d <- %d.%d"), p, Id(In->Expression), In->OutputIndex);
  }
}
