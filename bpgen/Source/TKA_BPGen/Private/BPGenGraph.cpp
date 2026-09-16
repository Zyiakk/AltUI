#include "BPGenGraph.h"
#include "BPGenTypes.h"
#include "BPGenCommandlet.h"
#include "Engine/Blueprint.h"
#include "EdGraph/EdGraph.h"
#include "EdGraphSchema_K2.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "K2Node_Event.h"
#include "K2Node_CustomEvent.h"
#include "K2Node_CallFunction.h"
#include "K2Node_CallArrayFunction.h"
#include "K2Node_VariableGet.h"
#include "K2Node_VariableSet.h"
#include "K2Node_IfThenElse.h"
#include "K2Node_ExecutionSequence.h"
#include "K2Node_DynamicCast.h"
#include "K2Node_ClassDynamicCast.h"
#include "K2Node_Self.h"
#include "K2Node_SpawnActorFromClass.h"
#include "K2Node_MacroInstance.h"
#include "K2Node_MakeArray.h"
#include "K2Node_BreakStruct.h"
#include "K2Node_MakeStruct.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_FunctionResult.h"
#include "K2Node_InputKey.h"
#include "K2Node_GetDataTableRow.h"
#include "Engine/DataTable.h"
#include "Blueprint/UserWidget.h"
#include "WidgetBlueprint.h"
#include "Blueprint/WidgetBlueprintGeneratedClass.h"
#include "GameFramework/Actor.h"
#include "Blueprint/WidgetTree.h"
#include "Components/PanelWidget.h"
#include "Components/PanelSlot.h"
#include "Components/Widget.h"

static FString JS(const TSharedPtr<FJsonObject>& O, const TCHAR* K, const FString& D = TEXT("")) { FString V; return O->TryGetStringField(K, V) ? V : D; }
static int32 JI(const TSharedPtr<FJsonObject>& O, const TCHAR* K, int32 D = 0) { double V; return O->TryGetNumberField(K, V) ? (int32)V : D; }
static FString Norm(const FString& S) { FString R = S.ToLower(); R.ReplaceInline(TEXT(" "), TEXT("")); R.ReplaceInline(TEXT("_"), TEXT("")); return R; }

void BPGenGraph::PickBlueprintClasses(UClass* Parent, UClass*& BPClass, UClass*& GenClass) {
  if (Parent && Parent->IsChildOf(UUserWidget::StaticClass())) { BPClass = UWidgetBlueprint::StaticClass(); GenClass = UWidgetBlueprintGeneratedClass::StaticClass(); }
}

static FString StripGuid(const FString& S) {
  // "SortKey_3_0123ABCD..." -> "SortKey"  (user-defined struct member)
  int32 L = S.Len();
  if (L > 34 && S[L - 33] == TCHAR('_')) {
    bool bHex = true; for (int32 i = L - 32; i < L; ++i) if (!FChar::IsHexDigit(S[i])) { bHex = false; break; }
    if (bHex) { FString Base = S.Left(L - 33); int32 Us; if (Base.FindLastChar(TCHAR('_'), Us) && Base.Mid(Us + 1).IsNumeric()) return Base.Left(Us); }
  }
  return S;
}
static UEdGraphPin* FindPinFuzzy(UEdGraphNode* N, const FString& Name, EEdGraphPinDirection Dir = EGPD_MAX) {
  for (UEdGraphPin* P : N->Pins) if (P->PinName.ToString() == Name && (Dir == EGPD_MAX || P->Direction == Dir)) return P;
  const FString W = Norm(Name);
  for (UEdGraphPin* P : N->Pins) if (Norm(P->PinName.ToString()) == W && (Dir == EGPD_MAX || P->Direction == Dir)) return P;
  for (UEdGraphPin* P : N->Pins) if ((Norm(StripGuid(P->PinName.ToString())) == W || Norm(P->PinFriendlyName.ToString()) == W) && (Dir == EGPD_MAX || P->Direction == Dir)) return P;
  // cast output "AsXyz": prefix match
  if (W.StartsWith(TEXT("as")))
    for (UEdGraphPin* P : N->Pins) if (Norm(P->PinName.ToString()).StartsWith(W) && (Dir == EGPD_MAX || P->Direction == Dir)) return P;
  return nullptr;
}
static FString PinList(UEdGraphNode* N) { FString S; for (UEdGraphPin* P : N->Pins) S += FString::Printf(TEXT("%s%s "), P->Direction == EGPD_Input ? TEXT("<") : TEXT(">"), *P->PinName.ToString()); return S; }

static bool SetPinDefault(const UEdGraphSchema_K2* Schema, UEdGraphPin* Pin, const FString& Val, FString& Err) {
  const FName Cat = Pin->PinType.PinCategory;
  if ((Cat == UEdGraphSchema_K2::PC_Object || Cat == UEdGraphSchema_K2::PC_Class) && Val.StartsWith(TEXT("/"))) {
    UObject* O = BPGenTypes::LoadObj(Val);
    if (!O) { Err = TEXT("default object not found ") + Val; return false; }
    Schema->TrySetDefaultObject(*Pin, O); return true;
  }
  if (Cat == UEdGraphSchema_K2::PC_Text) { Schema->TrySetDefaultText(*Pin, FText::FromString(Val)); return true; }
  Schema->TrySetDefaultValue(*Pin, Val); return true;
}

static UEdGraph* FindMacro(const FString& Name) {
  UBlueprint* Macros = LoadObject<UBlueprint>(nullptr, TEXT("/Engine/EditorBlueprintResources/StandardMacros.StandardMacros"));
  if (!Macros) return nullptr;
  for (UEdGraph* G : Macros->MacroGraphs) if (G->GetName() == Name) return G;
  return nullptr;
}

template<typename T> static T* NewNode(UEdGraph* G, int32 X, int32 Y, TFunction<void(T*)> Init) {
  FGraphNodeCreator<T> C(*G); T* N = C.CreateNode(); N->NodePosX = X; N->NodePosY = Y; if (Init) Init(N); C.Finalize(); return N;
}

bool BPGenGraph::BuildGraph(UBlueprint* BP, UEdGraph* G, const TSharedPtr<FJsonObject>& J, FString& Err) {
  if (!G) { Err = TEXT("graph is null"); return false; }
  const UEdGraphSchema_K2* Schema = GetDefault<UEdGraphSchema_K2>();
  // clear the graph (keep entry/result) – we own these graphs completely
  for (UEdGraphNode* N : TArray<UEdGraphNode*>(G->Nodes))
    if (!N->IsA<UK2Node_FunctionEntry>() && !N->IsA<UK2Node_FunctionResult>()) { N->BreakAllNodeLinks(); G->RemoveNode(N); }
  TMap<FString, UEdGraphNode*> Ids;
  { TArray<UK2Node_FunctionEntry*> E; G->GetNodesOfClass(E); if (E.Num()) Ids.Add(TEXT("entry"), E[0]);
    TArray<UK2Node_FunctionResult*> R; G->GetNodesOfClass(R); if (R.Num()) Ids.Add(TEXT("return"), R[0]); }
  const TArray<TSharedPtr<FJsonValue>>* Nodes = nullptr; J->TryGetArrayField(TEXT("nodes"), Nodes);
  int32 Idx = 0;
  if (Nodes) for (const auto& NV : *Nodes) {
    const TSharedPtr<FJsonObject> N = NV->AsObject(); const FString Id = JS(N, TEXT("id")), Kind = JS(N, TEXT("kind"));
    const int32 X = 320 * (Idx % 8), Y = 260 * (Idx / 8); ++Idx;
    UEdGraphNode* Node = nullptr;
    if (Kind == TEXT("event")) {
      UClass* C = BPGenTypes::LoadClassChecked(JS(N, TEXT("class"))); const FName FnName(*JS(N, TEXT("name")));
      if (!C || !C->FindFunctionByName(FnName)) { Err = TEXT("event not found ") + JS(N, TEXT("name")); return false; }
      Node = NewNode<UK2Node_Event>(G, X, Y, [&](UK2Node_Event* E) { E->EventReference.SetExternalMember(FnName, C); E->bOverrideFunction = true; });
    } else if (Kind == TEXT("custom_event")) {
      UK2Node_CustomEvent* E = NewNode<UK2Node_CustomEvent>(G, X, Y, [&](UK2Node_CustomEvent* CE) { CE->CustomFunctionName = FName(*JS(N, TEXT("name"))); });
      const TArray<TSharedPtr<FJsonValue>>* Ins = nullptr; N->TryGetArrayField(TEXT("inputs"), Ins);
      if (Ins) for (const auto& PV : *Ins) { const auto P = PV->AsObject(); FEdGraphPinType T;
        if (!BPGenTypes::PinTypeFromSpec(JS(P, TEXT("type")), JS(P, TEXT("container")), JS(P, TEXT("value_type")), T, Err)) return false;
        E->CreateUserDefinedPin(FName(*JS(P, TEXT("name"))), T, EGPD_Output); }
      Node = E;
    } else if (Kind == TEXT("call")) {
      UClass* C = BPGenTypes::LoadClassChecked(JS(N, TEXT("class"))); const FName FnName(*JS(N, TEXT("function")));
      UFunction* F = C ? C->FindFunctionByName(FnName) : nullptr;
      if (!F) { Err = FString::Printf(TEXT("function not found %s::%s"), *JS(N, TEXT("class")), *FnName.ToString()); return false; }
      if (F->HasMetaData(FBlueprintMetadata::MD_ArrayParam)) Node = NewNode<UK2Node_CallArrayFunction>(G, X, Y, [&](UK2Node_CallArrayFunction* CF) { CF->SetFromFunction(F); });
      else Node = NewNode<UK2Node_CallFunction>(G, X, Y, [&](UK2Node_CallFunction* CF) { CF->SetFromFunction(F); });
    } else if (Kind == TEXT("get") || Kind == TEXT("set")) {
      const FName Var(*JS(N, TEXT("var"))); const FString Cls = JS(N, TEXT("class"));
      UClass* Ext = Cls.IsEmpty() ? nullptr : BPGenTypes::LoadClassChecked(Cls);
      if (!Cls.IsEmpty() && !Ext) { Err = TEXT("var class not found ") + Cls; return false; }
      if (Kind == TEXT("get")) Node = NewNode<UK2Node_VariableGet>(G, X, Y, [&](UK2Node_VariableGet* V) { if (Ext) V->VariableReference.SetExternalMember(Var, Ext); else V->VariableReference.SetSelfMember(Var); });
      else Node = NewNode<UK2Node_VariableSet>(G, X, Y, [&](UK2Node_VariableSet* V) { if (Ext) V->VariableReference.SetExternalMember(Var, Ext); else V->VariableReference.SetSelfMember(Var); });
    } else if (Kind == TEXT("branch")) Node = NewNode<UK2Node_IfThenElse>(G, X, Y, nullptr);
    else if (Kind == TEXT("sequence")) { UK2Node_ExecutionSequence* S = NewNode<UK2Node_ExecutionSequence>(G, X, Y, nullptr); for (int32 i = 2; i < JI(N, TEXT("count"), 2); ++i) S->AddInputPin(); Node = S; }
    else if (Kind == TEXT("cast")) { UClass* C = BPGenTypes::LoadClassChecked(JS(N, TEXT("class"))); if (!C) { Err = TEXT("cast class not found ") + JS(N, TEXT("class")); return false; }
      const bool bPure = N->HasTypedField<EJson::Boolean>(TEXT("pure")) && N->GetBoolField(TEXT("pure"));
      UK2Node_DynamicCast* DC = NewNode<UK2Node_DynamicCast>(G, X, Y, [&](UK2Node_DynamicCast* D) { D->TargetType = C; });
      DC->SetPurity(bPure);  // after Finalize: PostPlacedNewNode would otherwise apply the editor default
      Node = DC; }
    else if (Kind == TEXT("class_cast")) { UClass* C = BPGenTypes::LoadClassChecked(JS(N, TEXT("class"))); if (!C) { Err = TEXT("class_cast class not found ") + JS(N, TEXT("class")); return false; }
      const bool bPure = N->HasTypedField<EJson::Boolean>(TEXT("pure")) && N->GetBoolField(TEXT("pure"));
      UK2Node_ClassDynamicCast* CC = NewNode<UK2Node_ClassDynamicCast>(G, X, Y, [&](UK2Node_ClassDynamicCast* D) { D->TargetType = C; });
      CC->SetPurity(bPure); Node = CC; }
    else if (Kind == TEXT("self")) Node = NewNode<UK2Node_Self>(G, X, Y, nullptr);
    else if (Kind == TEXT("spawn")) { UK2Node_SpawnActorFromClass* S = NewNode<UK2Node_SpawnActorFromClass>(G, X, Y, nullptr);
      if (UEdGraphPin* CP = S->GetClassPin()) { const FString Cls = JS(N, TEXT("class")); if (!Cls.IsEmpty()) { if (!SetPinDefault(Schema, CP, Cls, Err)) return false; S->ReconstructNode(); } }
      Node = S; }
    else if (Kind == TEXT("get_row")) {
      UDataTable* DT = Cast<UDataTable>(BPGenTypes::LoadObj(JS(N, TEXT("table"))));
      if (!DT) { Err = TEXT("get_row: table not found ") + JS(N, TEXT("table")); return false; }
      UK2Node_GetDataTableRow* R = NewNode<UK2Node_GetDataTableRow>(G, X, Y, nullptr);
      UEdGraphPin* TP = R->GetDataTablePin(); Schema->TrySetDefaultObject(*TP, DT); R->PinDefaultValueChanged(TP);
      Node = R; }
    else if (Kind == TEXT("macro")) { UEdGraph* M = FindMacro(JS(N, TEXT("name"))); if (!M) { Err = TEXT("macro not found ") + JS(N, TEXT("name")); return false; }
      Node = NewNode<UK2Node_MacroInstance>(G, X, Y, [&](UK2Node_MacroInstance* MI) { MI->SetMacroGraph(M); }); }
    else if (Kind == TEXT("call_self")) {
      const FName FnName(*JS(N, TEXT("function")));
      UFunction* F = BP->SkeletonGeneratedClass ? BP->SkeletonGeneratedClass->FindFunctionByName(FnName) : nullptr;
      if (!F) { Err = TEXT("call_self: function not in skeleton class: ") + FnName.ToString(); return false; }
      Node = NewNode<UK2Node_CallFunction>(G, X, Y, [&](UK2Node_CallFunction* CF) { CF->SetFromFunction(F); }); }
    else if (Kind == TEXT("foreach")) { UEdGraph* M = FindMacro(TEXT("ForEachLoop")); if (!M) { Err = TEXT("ForEachLoop macro not found"); return false; }
      Node = NewNode<UK2Node_MacroInstance>(G, X, Y, [&](UK2Node_MacroInstance* MI) { MI->SetMacroGraph(M); }); }
    else if (Kind == TEXT("make_array")) { UK2Node_MakeArray* MA = NewNode<UK2Node_MakeArray>(G, X, Y, nullptr);
      for (int32 i = 1; i < JI(N, TEXT("count"), 1); ++i) MA->AddInputPin();
      const FString TS = JS(N, TEXT("type")); if (!TS.IsEmpty()) { FEdGraphPinType T; if (!BPGenTypes::PinTypeFromSpec(TS, TEXT(""), TEXT(""), T, Err)) return false;
        for (UEdGraphPin* P : MA->Pins) { if (P->Direction == EGPD_Input) P->PinType = T; else { P->PinType = T; P->PinType.ContainerType = EPinContainerType::Array; } } }
      Node = MA; }
    else if (Kind == TEXT("break") || Kind == TEXT("make")) { UScriptStruct* S = Cast<UScriptStruct>(BPGenTypes::LoadObj(JS(N, TEXT("struct")))); if (!S) { Err = TEXT("struct not found ") + JS(N, TEXT("struct")); return false; }
      if (Kind == TEXT("break")) Node = NewNode<UK2Node_BreakStruct>(G, X, Y, [&](UK2Node_BreakStruct* B) { B->StructType = S; });
      else Node = NewNode<UK2Node_MakeStruct>(G, X, Y, [&](UK2Node_MakeStruct* B) { B->StructType = S; }); }
    else if (Kind == TEXT("input_key")) { const FKey Key(*JS(N, TEXT("key"))); if (!Key.IsValid()) { Err = TEXT("invalid key ") + JS(N, TEXT("key")); return false; }
      // "consume": false -> the key stays visible to lower input components (pawn, controller, other mods' actors); default true
      const bool bConsume = !N->HasTypedField<EJson::Boolean>(TEXT("consume")) || N->GetBoolField(TEXT("consume"));
      Node = NewNode<UK2Node_InputKey>(G, X, Y, [&](UK2Node_InputKey* K) { K->InputKey = Key; K->bConsumeInput = bConsume; K->bOverrideParentBinding = true; }); }
    else if (Kind == TEXT("return_new")) {   // additional return node (pins like the primary result node)
      UK2Node_FunctionResult* R = NewNode<UK2Node_FunctionResult>(G, X, Y, nullptr); Node = R; }   // PostPlacedNewNode synchronises the pins
    else if (Kind == TEXT("return") || Kind == TEXT("entry")) { Node = Ids.FindRef(Kind); if (!Node) { Err = TEXT("graph has no ") + Kind; return false; } }
    else { Err = TEXT("unknown node kind ") + Kind; return false; }
    if (Kind != TEXT("return") && Kind != TEXT("entry") && Ids.Contains(Id)) { Err = TEXT("duplicate node id (FString keys are case-insensitive) ") + Id; return false; }
    Ids.Add(Id, Node);
    const TSharedPtr<FJsonObject>* Defs = nullptr;
    if (N->TryGetObjectField(TEXT("defaults"), Defs))
      for (const auto& KV : (*Defs)->Values) { UEdGraphPin* P = FindPinFuzzy(Node, KV.Key, EGPD_Input);
        if (!P) { Err = FString::Printf(TEXT("default pin not found %s.%s pins: %s"), *Id, *KV.Key, *PinList(Node)); return false; }
        if (!SetPinDefault(Schema, P, KV.Value->AsString(), Err)) return false; }
    // optional pin subclasses (e.g. SoftClass<Actor> instead of SoftClass<Object>)
    const TSharedPtr<FJsonObject>* Subs = nullptr;
    if (N->TryGetObjectField(TEXT("pin_subclass"), Subs))
      for (const auto& KV : (*Subs)->Values) { UEdGraphPin* P = FindPinFuzzy(Node, KV.Key); UClass* C = BPGenTypes::LoadClassChecked(KV.Value->AsString());
        if (!P || !C) { Err = FString::Printf(TEXT("pin_subclass: pin or class missing %s.%s"), *Id, *KV.Key); return false; }
        P->PinType.PinSubCategoryObject = C; }
  }
  // short form "in": {"Pin": "@node.pin" | "literal"} -> link or default
  TArray<TPair<FString, FString>> ExtraLinks;
  if (Nodes) for (const auto& NV : *Nodes) {
    const TSharedPtr<FJsonObject> N = NV->AsObject(); const FString Id = JS(N, TEXT("id"));
    const TSharedPtr<FJsonObject>* In = nullptr;
    if (!N->TryGetObjectField(TEXT("in"), In)) continue;
    UEdGraphNode* Node = Ids.FindRef(Id);
    for (const auto& KV : (*In)->Values) {
      const FString V = KV.Value->AsString();
      if (V.StartsWith(TEXT("@"))) { ExtraLinks.Add(TPair<FString, FString>(V.Mid(1), Id + TEXT(".") + KV.Key)); continue; }
      UEdGraphPin* P = FindPinFuzzy(Node, KV.Key, EGPD_Input);
      if (!P) { Err = FString::Printf(TEXT("in: pin not found %s.%s pins: %s"), *Id, *KV.Key, *PinList(Node)); return false; }
      if (!SetPinDefault(Schema, P, V, Err)) return false;
    }
  }
  // short form "exec": [["a","b:Completed","c"], ...] -> connect the first exec pins ("id:pin" selects the output pin)
  const TArray<TSharedPtr<FJsonValue>>* Chains = nullptr; J->TryGetArrayField(TEXT("exec"), Chains);
  if (Chains) for (const auto& CV : *Chains) {
    const TArray<TSharedPtr<FJsonValue>>& C = CV->AsArray();
    for (int32 i = 0; i + 1 < C.Num(); ++i) {
      FString AId = C[i]->AsString(), APin, BId = C[i + 1]->AsString(), BPin;
      AId.Split(TEXT(":"), &AId, &APin); BId.Split(TEXT(":"), &BId, &BPin);
      UEdGraphNode* A = Ids.FindRef(AId); UEdGraphNode* B = Ids.FindRef(BId);
      if (!A || !B) { Err = FString::Printf(TEXT("exec: unknown node %s or %s"), *AId, *BId); return false; }
      if (APin.IsEmpty()) for (UEdGraphPin* P : A->Pins) if (P->Direction == EGPD_Output && P->PinType.PinCategory == UEdGraphSchema_K2::PC_Exec) { APin = P->PinName.ToString(); break; }
      if (BPin.IsEmpty()) for (UEdGraphPin* P : B->Pins) if (P->Direction == EGPD_Input && P->PinType.PinCategory == UEdGraphSchema_K2::PC_Exec) { BPin = P->PinName.ToString(); break; }
      if (APin.IsEmpty() || BPin.IsEmpty()) { Err = FString::Printf(TEXT("exec: no exec pin on %s or %s"), *AId, *BId); return false; }
      ExtraLinks.Add(TPair<FString, FString>(AId + TEXT(".") + APin, BId + TEXT(".") + BPin));
    }
  }
  TArray<TPair<FString, FString>> AllLinks = ExtraLinks;
  const TArray<TSharedPtr<FJsonValue>>* Links = nullptr; J->TryGetArrayField(TEXT("links"), Links);
  if (Links) for (const auto& LV : *Links) {
    const TArray<TSharedPtr<FJsonValue>>& L = LV->AsArray(); if (L.Num() != 2) { Err = TEXT("link needs 2 entries"); return false; }
    AllLinks.Add(TPair<FString, FString>(L[0]->AsString(), L[1]->AsString()));
  }
  for (const auto& LK : AllLinks) {
    FString AId, APin, BId, BPin; LK.Key.Split(TEXT("."), &AId, &APin); LK.Value.Split(TEXT("."), &BId, &BPin);
    UEdGraphNode* A = Ids.FindRef(AId); UEdGraphNode* B = Ids.FindRef(BId);
    if (!A || !B) { Err = FString::Printf(TEXT("link: unknown node %s or %s"), *AId, *BId); return false; }
    UEdGraphPin* PA = FindPinFuzzy(A, APin, EGPD_Output); UEdGraphPin* PB = FindPinFuzzy(B, BPin, EGPD_Input);
    if (!PA) { Err = FString::Printf(TEXT("link: pin %s.%s not found; pins: %s"), *AId, *APin, *PinList(A)); return false; }
    if (!PB) { Err = FString::Printf(TEXT("link: pin %s.%s not found; pins: %s"), *BId, *BPin, *PinList(B)); return false; }
    if (!Schema->TryCreateConnection(PA, PB)) { Err = FString::Printf(TEXT("link refused %s.%s -> %s.%s: %s"), *AId, *APin, *BId, *BPin, *Schema->CanCreateConnection(PA, PB).Message.ToString()); return false; }
    UE_LOG(LogBPGen, Verbose, TEXT("BPGEN link %s.%s -> %s.%s (linked=%d/%d)"), *AId, *PA->PinName.ToString(), *BId, *PB->PinName.ToString(), PA->LinkedTo.Num(), PB->LinkedTo.Num());
  }
  return true;
}

static bool ImportProps(UObject* Target, const TSharedPtr<FJsonObject>& Props, const FString& Label, FString& Err) {
  if (!Props.IsValid()) return true;
  for (const auto& KV : Props->Values) {
    FProperty* P = Target->GetClass()->FindPropertyByName(*KV.Key);
    if (!P) { Err = FString::Printf(TEXT("%s: property not found %s on %s"), *Label, *KV.Key, *Target->GetClass()->GetName()); return false; }
    FString Val = KV.Value->Type == EJson::String ? KV.Value->AsString() : (KV.Value->Type == EJson::Boolean ? (KV.Value->AsBool() ? TEXT("true") : TEXT("false")) : FString::SanitizeFloat(KV.Value->AsNumber()));
    if (!P->ImportText(*Val, P->ContainerPtrToValuePtr<void>(Target), PPF_None, Target)) { Err = FString::Printf(TEXT("%s: import failed %s=%s"), *Label, *KV.Key, *Val); return false; }
  }
  return true;
}

static UWidget* BuildWidgetNode(UWidgetBlueprint* WBP, UPanelWidget* Parent, const TSharedPtr<FJsonObject>& J, FString& Err) {
  UClass* C = BPGenTypes::LoadClassChecked(JS(J, TEXT("class")));
  if (!C || !C->IsChildOf(UWidget::StaticClass())) { Err = TEXT("widget class not found ") + JS(J, TEXT("class")); return nullptr; }
  const FString Name = JS(J, TEXT("name"));
  UWidget* Wd = WBP->WidgetTree->ConstructWidget<UWidget>(C, Name.IsEmpty() ? NAME_None : FName(*Name));
  Wd->bIsVariable = !Name.IsEmpty();
  const TSharedPtr<FJsonObject>* Props = nullptr;
  if (J->TryGetObjectField(TEXT("props"), Props) && !ImportProps(Wd, *Props, Name, Err)) return nullptr;
  if (Parent) {
    UPanelSlot* Slot = Parent->AddChild(Wd);
    const TSharedPtr<FJsonObject>* SlotProps = nullptr;
    if (Slot && J->TryGetObjectField(TEXT("slot"), SlotProps) && !ImportProps(Slot, *SlotProps, Name + TEXT(".slot"), Err)) return nullptr;
  }
  const TArray<TSharedPtr<FJsonValue>>* Children = nullptr;
  if (J->TryGetArrayField(TEXT("children"), Children) && Children->Num() > 0) {
    UPanelWidget* PW = Cast<UPanelWidget>(Wd);
    if (!PW) { Err = TEXT("children on non-panel widget ") + Name; return nullptr; }
    for (const auto& CV : *Children) if (!BuildWidgetNode(WBP, PW, CV->AsObject(), Err)) return nullptr;
  }
  return Wd;
}

bool BPGenGraph::BuildWidgetTree(UBlueprint* BP, const TSharedPtr<FJsonObject>& J, FString& Err) {
  UWidgetBlueprint* WBP = Cast<UWidgetBlueprint>(BP);
  if (!WBP) { Err = TEXT("widget_tree on non-widget blueprint"); return false; }
  // idempotence: discard the old tree
  if (WBP->WidgetTree->RootWidget) {
    TArray<UWidget*> All; WBP->WidgetTree->GetAllWidgets(All);
    for (UWidget* Old : All) {
      WBP->WidgetTree->RemoveWidget(Old);
      Old->Rename(nullptr, GetTransientPackage(), REN_DontCreateRedirectors | REN_NonTransactional | REN_DoNotDirty);
      Old->MarkPendingKill();
    }
    WBP->WidgetTree->RootWidget = nullptr;
  }
  UWidget* Root = BuildWidgetNode(WBP, nullptr, J, Err);
  if (!Root) return false;
  WBP->WidgetTree->RootWidget = Root;
  WBP->WidgetTree->Modify();
  return true;
}
