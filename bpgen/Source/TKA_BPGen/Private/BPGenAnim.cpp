// Animation assets beyond the FBX import: notifies with a class and values (animimport and montage), "montage", "object_stub", "blendspace1d",
// "animplayer", and the read-back (DescribeAnim: the commandlet's -dumpanim= and BPGenAnimLib.DescribeAnim for editor tests; DescribeAnimAsset
// for blend spaces and animation blueprints).
#include "BPGenAssets.h"
#include "BPGenTypes.h"
#include "BPGenAnimLib.h"
#include "BPGenCommandlet.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimMontage.h"
#include "Animation/BlendSpace1D.h"
#include "Animation/AnimBlueprint.h"
#include "Animation/AnimBlueprintGeneratedClass.h"
#include "Animation/AnimInstance.h"
#include "AnimationGraph.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_BlendSpacePlayer.h"
#include "AnimGraphNode_Slot.h"
#include "AnimGraphNode_SequencePlayer.h"
#include "AnimGraphNode_ApplyAdditive.h"
#include "K2Node_VariableGet.h"
#include "EdGraphSchema_K2.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/CompilerResultsLog.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "Animation/Skeleton.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "AssetRegistryModule.h"
#include "Misc/PackageName.h"
#include "Misc/SecureHash.h"
#include "UObject/Package.h"
#include "UObject/UObjectGlobals.h"

static FString AnimJStr(const TSharedPtr<FJsonObject>& O, const TCHAR* K, const FString& Def = TEXT("")) { FString V; return O->TryGetStringField(K, V) ? V : Def; }

// A key this code does not know is an error: a misspelt "duration" or "values" would otherwise vanish without a trace.
static bool CheckKeys(const TSharedPtr<FJsonObject>& O, const TArray<FString>& Known, const FString& Where, FString& Err) {
  for (const auto& KV : O->Values) if (!Known.Contains(KV.Key)) { Err = Where + TEXT(": unknown key \"") + KV.Key + TEXT("\" (known: ") + FString::Join(Known, TEXT(", ")) + TEXT(")"); return false; }
  return true;
}

static bool NumField(const TSharedPtr<FJsonObject>& O, const TCHAR* K, float& Out, const FString& Where, FString& Err, bool bRequired) {
  const TSharedPtr<FJsonValue> V = O->TryGetField(K);
  if (!V.IsValid()) { if (bRequired) Err = Where + TEXT(": \"") + K + TEXT("\" missing"); return !bRequired; }
  if (V->Type != EJson::Number) { Err = Where + TEXT(": \"") + K + TEXT("\" must be a number"); return false; }
  Out = (float)V->AsNumber(); return true;
}

// One value on a notify object, by the variable's name. Object / class values by path (loaded and type-checked), numbers only into numeric
// properties, bools only into bools, strings into names / strings / texts / enums. Anything else fails the build.
static bool SetNotifyValue(UObject* Obj, const FString& Key, const TSharedPtr<FJsonValue>& V, const FString& Where, FString& Err) {
  FProperty* P = Obj->GetClass()->FindPropertyByName(FName(*Key));
  if (!P) {
    FString Have;
    for (TFieldIterator<FProperty> It(Obj->GetClass()); It; ++It) if (It->HasAnyPropertyFlags(CPF_Edit)) Have += (Have.IsEmpty() ? TEXT("") : TEXT(", ")) + It->GetName();
    Err = Where + TEXT(": ") + Obj->GetClass()->GetName() + TEXT(" has no variable \"") + Key + TEXT("\" (editable: ") + Have + TEXT(")"); return false;
  }
  void* Ptr = P->ContainerPtrToValuePtr<void>(Obj);
  const FString What = Where + TEXT(" ") + Key;
  if (FClassProperty* CP = CastField<FClassProperty>(P)) {
    if (V->Type != EJson::String) { Err = What + TEXT(": class value must be a path"); return false; }
    UClass* C = BPGenTypes::LoadClassChecked(V->AsString());
    if (!C) { Err = What + TEXT(": class not found ") + V->AsString(); return false; }
    if (!C->IsChildOf(CP->MetaClass)) { Err = What + TEXT(": ") + C->GetName() + TEXT(" is no ") + CP->MetaClass->GetName(); return false; }
    CP->SetObjectPropertyValue(Ptr, C); return true;
  }
  if (FObjectPropertyBase* OP = CastField<FObjectPropertyBase>(P)) {
    if (V->Type != EJson::String) { Err = What + TEXT(": object value must be a path"); return false; }
    UObject* O = BPGenTypes::LoadObj(V->AsString());
    if (!O) { Err = What + TEXT(": object not found ") + V->AsString(); return false; }
    if (!O->IsA(OP->PropertyClass)) { Err = What + TEXT(": ") + O->GetClass()->GetName() + TEXT(" is no ") + OP->PropertyClass->GetName(); return false; }
    OP->SetObjectPropertyValue(Ptr, O); return true;
  }
  FString Text;
  if (FBoolProperty* BP = CastField<FBoolProperty>(P)) {
    if (V->Type != EJson::Boolean) { Err = What + TEXT(": bool expected"); return false; }
    BP->SetPropertyValue(Ptr, V->AsBool()); return true;
  }
  if (FNumericProperty* NP = CastField<FNumericProperty>(P)) {
    if (CastField<FByteProperty>(P) && CastField<FByteProperty>(P)->Enum) { if (V->Type != EJson::String) { Err = What + TEXT(": enum value by name expected"); return false; } Text = V->AsString(); }
    else {
      if (V->Type != EJson::Number) { Err = What + TEXT(": number expected"); return false; }
      if (NP->IsInteger()) { const double D = V->AsNumber(); if (D != FMath::RoundToDouble(D)) { Err = What + TEXT(": integer expected"); return false; } NP->SetIntPropertyValue(Ptr, (int64)D); }
      else NP->SetFloatingPointPropertyValue(Ptr, V->AsNumber());
      return true;
    }
  } else if (P->IsA<FNameProperty>() || P->IsA<FStrProperty>() || P->IsA<FTextProperty>() || P->IsA<FEnumProperty>()) {
    if (V->Type != EJson::String) { Err = What + TEXT(": string expected"); return false; }
    Text = V->AsString();
  } else { Err = What + TEXT(": property type ") + P->GetCPPType() + TEXT(" not supported"); return false; }
  if (!P->ImportText(*Text, Ptr, PPF_None, Obj)) { Err = What + TEXT(": cannot take \"") + Text + TEXT("\""); return false; }
  return true;
}

// The game's notify names: a Blueprint notify by its class name ("Shake_Notify_C"), an engine one without the prefix ("PlaySound").
static FName NotifyNameFor(UClass* C) {
  FString N = C->GetName();
  if (!Cast<UBlueprintGeneratedClass>(C)) for (const TCHAR* Pre : {TEXT("AnimNotifyState_"), TEXT("AnimNotify_")}) if (N.StartsWith(Pre)) { N.RightChopInline(FCString::Strlen(Pre)); break; }
  return FName(*N);
}

// "notifies": [name, time] (by name only, as before) or {time, class?, name?, duration?, values?, track?}. For a montage the times are montage
// time and the notifies link to the segment under them, as the editor does.
bool BPGenAssets::AddNotifies(UAnimSequenceBase* S, const TArray<TSharedPtr<FJsonValue>>& Notes, FString& Err) {
  const FString Asset = S->GetName();
  const float Len = S->SequenceLength;
  for (int32 i = 0; i < Notes.Num(); ++i) {
    const FString Where = FString::Printf(TEXT("%s notify %d"), *Asset, i);
    FString Name, ClassPath; float Time = 0, Duration = -1; int32 Track = 0;
    const TSharedPtr<FJsonObject>* ValuesObj = nullptr; bool bHasDuration = false;
    if (Notes[i]->Type == EJson::Array) {
      const auto& P = Notes[i]->AsArray();
      if (P.Num() != 2 || P[0]->Type != EJson::String || P[1]->Type != EJson::Number) { Err = Where + TEXT(": [name, time] expected"); return false; }
      Name = P[0]->AsString(); Time = (float)P[1]->AsNumber();
    } else if (Notes[i]->Type == EJson::Object) {
      const TSharedPtr<FJsonObject> O = Notes[i]->AsObject();
      if (!CheckKeys(O, {TEXT("time"), TEXT("class"), TEXT("name"), TEXT("duration"), TEXT("values"), TEXT("track")}, Where, Err)) return false;
      if (!NumField(O, TEXT("time"), Time, Where, Err, true)) return false;
      bHasDuration = O->HasField(TEXT("duration"));
      if (bHasDuration && !NumField(O, TEXT("duration"), Duration, Where, Err, true)) return false;
      ClassPath = AnimJStr(O, TEXT("class")); Name = AnimJStr(O, TEXT("name"));
      float T = 0; if (O->HasField(TEXT("track"))) { if (!NumField(O, TEXT("track"), T, Where, Err, true)) return false; Track = (int32)T; }
      if (O->HasField(TEXT("values")) && !O->TryGetObjectField(TEXT("values"), ValuesObj)) { Err = Where + TEXT(": \"values\" must be an object"); return false; }
    } else { Err = Where + TEXT(": array or object expected"); return false; }
    if (ClassPath.IsEmpty() && Name.IsEmpty()) { Err = Where + TEXT(": neither class nor name"); return false; }
    if (Time < 0 || Time > Len + 1e-4f) { Err = Where + FString::Printf(TEXT(": time %.4f outside 0..%.4f"), Time, Len); return false; }
    if (Track < 0 || Track > 20) { Err = Where + TEXT(": track out of range"); return false; }
    UClass* C = nullptr;
    if (!ClassPath.IsEmpty()) {
      C = BPGenTypes::LoadClassChecked(ClassPath);
      if (!C) { Err = Where + TEXT(": class not found ") + ClassPath; return false; }
      const bool bState = C->IsChildOf(UAnimNotifyState::StaticClass());
      if (!bState && !C->IsChildOf(UAnimNotify::StaticClass())) { Err = Where + TEXT(": ") + C->GetName() + TEXT(" is no AnimNotify / AnimNotifyState"); return false; }
      if (C->HasAnyClassFlags(CLASS_Abstract)) { Err = Where + TEXT(": ") + C->GetName() + TEXT(" is abstract"); return false; }
      if (bState && !bHasDuration) { Err = Where + TEXT(": ") + C->GetName() + TEXT(" is a NotifyState and needs a duration"); return false; }
      if (!bState && bHasDuration) { Err = Where + TEXT(": ") + C->GetName() + TEXT(" is a plain notify, it takes no duration"); return false; }
      if (bState && (Duration <= 0 || Time + Duration > Len + 1e-4f)) { Err = Where + FString::Printf(TEXT(": window %.4f + %.4f outside 0..%.4f"), Time, Duration, Len); return false; }
    } else {
      if (bHasDuration || ValuesObj) { Err = Where + TEXT(": duration / values need a class"); return false; }
    }
    while (S->AnimNotifyTracks.Num() <= Track) S->AnimNotifyTracks.Add(FAnimNotifyTrack(*FString::FromInt(S->AnimNotifyTracks.Num() + 1), FLinearColor::White));
    FAnimNotifyEvent E;
    E.NotifyName = C ? (Name.IsEmpty() ? NotifyNameFor(C) : FName(*Name)) : FName(*Name);
    // stable per asset and index (editor only; the notify panel tells notifies apart by it), so a rebuild does not change it
    const FString H = FMD5::HashAnsiString(*FString::Printf(TEXT("%s#%d"), *S->GetPathName(), i));
    FGuid::Parse(H, E.Guid);
    E.Link(S, Time);
    E.TriggerTimeOffset = GetTriggerTimeOffsetForType(S->CalculateOffsetForNotify(Time));
    E.TrackIndex = Track;
    if (C) {
      UObject* N = NewObject<UObject>(S, C, NAME_None, RF_Transactional);
      E.Notify = Cast<UAnimNotify>(N); E.NotifyStateClass = Cast<UAnimNotifyState>(N);
      if (E.NotifyStateClass) {
        E.SetDuration(Duration);
        E.EndLink.Link(S, E.EndLink.GetTime());
        E.EndTriggerTimeOffset = GetTriggerTimeOffsetForType(S->CalculateOffsetForNotify(Time + Duration));
        E.NotifyStateClass->OnAnimNotifyCreatedInEditor(E);
      } else E.Notify->OnAnimNotifyCreatedInEditor(E);
      if (ValuesObj) for (const auto& KV : (*ValuesObj)->Values) if (!SetNotifyValue(N, KV.Key, KV.Value, Where, Err)) return false;
    }
    S->Notifies.Add(E);
  }
  return true;
}

// "montage": {path, skeleton, slot, segments [{anim, start?, length?, rate?}], sections [{name, time, next?}], notifies, blend_in?, blend_out?,
// blend_out_trigger?, auto_blend_out?}. Built from scratch each time (an existing one at the path is moved away first).
bool BPGenAssets::MakeMontage(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = AnimJStr(A, TEXT("path"));
  if (!CheckKeys(A, {TEXT("type"), TEXT("path"), TEXT("skeleton"), TEXT("slot"), TEXT("segments"), TEXT("sections"), TEXT("notifies"), TEXT("blend_in"),
                     TEXT("blend_out"), TEXT("blend_out_trigger"), TEXT("auto_blend_out")}, TEXT("montage ") + Path, Err)) return false;
  USkeleton* Skel = Cast<USkeleton>(BPGenTypes::LoadObj(AnimJStr(A, TEXT("skeleton"))));
  if (!Skel) { Err = TEXT("montage: skeleton not found ") + AnimJStr(A, TEXT("skeleton")); return false; }
  const FName Slot(*AnimJStr(A, TEXT("slot")));
  if (Slot.IsNone() || !Skel->ContainsSlotName(Slot)) {
    FString Have; for (const FAnimSlotGroup& G : Skel->GetSlotGroups()) for (const FName& N : G.SlotNames) Have += G.GroupName.ToString() + TEXT(".") + N.ToString() + TEXT(" ");
    Err = TEXT("montage: slot \"") + Slot.ToString() + TEXT("\" unknown to ") + Skel->GetName() + TEXT(" (has: ") + Have + TEXT(")"); return false;
  }
  FString Name; UPackage* Pkg = BPGenAssets::MakePackage(Path, Name);
  if (UObject* Old = FindObject<UObject>(Pkg, *Name)) {   // rebuilt from scratch: no leftover sections or notify objects
    Old->Rename(*MakeUniqueObjectName(GetTransientPackage(), Old->GetClass()).ToString(), GetTransientPackage(), REN_DontCreateRedirectors | REN_NonTransactional | REN_ForceNoResetLoaders);
    Old->ClearFlags(RF_Public | RF_Standalone); Old->MarkPendingKill();
  }
  UAnimMontage* M = NewObject<UAnimMontage>(Pkg, *Name, RF_Public | RF_Standalone | RF_Transactional);
  M->SetSkeleton(Skel);
  FSlotAnimationTrack& Track = M->SlotAnimTracks[0];
  Track.SlotName = Slot;
  const TArray<TSharedPtr<FJsonValue>>* Segs = nullptr;
  if (!A->TryGetArrayField(TEXT("segments"), Segs) || Segs->Num() == 0) { Err = TEXT("montage: no segments"); return false; }
  float Pos = 0;
  for (int32 i = 0; i < Segs->Num(); ++i) {
    const FString Where = FString::Printf(TEXT("montage %s segment %d"), *Name, i);
    const TSharedPtr<FJsonObject> G = (*Segs)[i]->AsObject();
    if (!G.IsValid() || !CheckKeys(G, {TEXT("anim"), TEXT("start"), TEXT("length"), TEXT("rate")}, Where, Err)) { if (Err.IsEmpty()) Err = Where + TEXT(": object expected"); return false; }
    UAnimSequenceBase* Seq = Cast<UAnimSequenceBase>(BPGenTypes::LoadObj(AnimJStr(G, TEXT("anim"))));
    if (!Seq || Seq->IsA<UAnimMontage>()) { Err = Where + TEXT(": sequence not found ") + AnimJStr(G, TEXT("anim")); return false; }
    if (Seq->GetSkeleton() != Skel) { Err = Where + TEXT(": ") + Seq->GetName() + TEXT(" is on another skeleton"); return false; }
    float Start = 0, Length = Seq->SequenceLength, Rate = 1;
    if (!NumField(G, TEXT("start"), Start, Where, Err, false) || !NumField(G, TEXT("rate"), Rate, Where, Err, false)) return false;
    Length = Seq->SequenceLength - Start;
    if (!NumField(G, TEXT("length"), Length, Where, Err, false)) return false;
    if (Start < 0 || Length <= 0 || Rate <= 0 || Start + Length > Seq->SequenceLength + 1e-3f) {
      Err = Where + FString::Printf(TEXT(": start %.4f length %.4f rate %.3f do not fit %s (%.4f s)"), Start, Length, Rate, *Seq->GetName(), Seq->SequenceLength); return false; }
    FAnimSegment Seg;
    Seg.AnimReference = Seq; Seg.StartPos = Pos; Seg.AnimStartTime = Start; Seg.AnimEndTime = FMath::Min(Start + Length, Seq->SequenceLength);
    Seg.AnimPlayRate = Rate; Seg.LoopingCount = 1;
    Track.AnimTrack.AnimSegments.Add(Seg);
    Pos += Seg.GetLength();
  }
  M->SetSequenceLength(M->CalculateSequenceLength());
  // sections: in time order, the first at 0; AddAnimCompositeSection chains a new one to the previous - every "next" is set explicitly below
  const TArray<TSharedPtr<FJsonValue>>* Secs = nullptr; A->TryGetArrayField(TEXT("sections"), Secs);
  TArray<TSharedPtr<FJsonValue>> DefaultSecs;
  if (!Secs || Secs->Num() == 0) { TSharedPtr<FJsonObject> D = MakeShared<FJsonObject>(); D->SetStringField(TEXT("name"), TEXT("Default")); D->SetNumberField(TEXT("time"), 0); DefaultSecs.Add(MakeShared<FJsonValueObject>(D)); Secs = &DefaultSecs; }
  float Prev = -1;
  for (int32 i = 0; i < Secs->Num(); ++i) {
    const FString Where = FString::Printf(TEXT("montage %s section %d"), *Name, i);
    const TSharedPtr<FJsonObject> O = (*Secs)[i]->AsObject();
    if (!O.IsValid() || !CheckKeys(O, {TEXT("name"), TEXT("time"), TEXT("next")}, Where, Err)) { if (Err.IsEmpty()) Err = Where + TEXT(": object expected"); return false; }
    float T = 0; if (!NumField(O, TEXT("time"), T, Where, Err, true)) return false;
    if ((i == 0 && T != 0) || T <= Prev || T >= M->SequenceLength) { Err = Where + FString::Printf(TEXT(": time %.4f (first at 0, ascending, before the end %.4f)"), T, M->SequenceLength); return false; }
    Prev = T;
    const FString SecName = AnimJStr(O, TEXT("name"));
    if (SecName.IsEmpty()) { Err = Where + TEXT(": name empty"); return false; }
    if (M->AddAnimCompositeSection(FName(*SecName), T) == INDEX_NONE) { Err = Where + TEXT(": name twice: ") + SecName; return false; }
  }
  for (int32 i = 0; i < Secs->Num(); ++i) {
    const FString Next = AnimJStr((*Secs)[i]->AsObject(), TEXT("next"));
    if (!Next.IsEmpty() && M->GetSectionIndex(FName(*Next)) == INDEX_NONE) { Err = FString::Printf(TEXT("montage %s section %d: next \"%s\" unknown"), *Name, i, *Next); return false; }
    M->CompositeSections[i].NextSectionName = Next.IsEmpty() ? NAME_None : FName(*Next);
  }
  float BI = M->BlendIn.GetBlendTime(), BO = M->BlendOut.GetBlendTime(), Trig = M->BlendOutTriggerTime;
  if (!NumField(A, TEXT("blend_in"), BI, TEXT("montage ") + Name, Err, false) || !NumField(A, TEXT("blend_out"), BO, TEXT("montage ") + Name, Err, false)
      || !NumField(A, TEXT("blend_out_trigger"), Trig, TEXT("montage ") + Name, Err, false)) return false;
  M->BlendIn.SetBlendTime(BI); M->BlendOut.SetBlendTime(BO); M->BlendOutTriggerTime = Trig;
  if (A->HasField(TEXT("auto_blend_out"))) { bool B; if (!A->TryGetBoolField(TEXT("auto_blend_out"), B)) { Err = TEXT("montage: auto_blend_out must be a bool"); return false; } M->bEnableAutoBlendOut = B; }
  const TArray<TSharedPtr<FJsonValue>>* Notes = nullptr;
  if (A->TryGetArrayField(TEXT("notifies"), Notes) && !AddNotifies(M, *Notes, Err)) return false;
  if (M->AnimNotifyTracks.Num() == 0) M->AnimNotifyTracks.Add(FAnimNotifyTrack(TEXT("1"), FLinearColor::White));
  M->UpdateLinkableElements();
  M->RefreshCacheData();
  M->PostEditChange(); M->MarkPackageDirty();
  UE_LOG(LogBPGen, Display, TEXT("BPGEN montage %s len=%.4f slot=%s segments=%d sections=%d notifies=%d"), *Name, M->SequenceLength, *Slot.ToString(),
    Track.AnimTrack.AnimSegments.Num(), M->CompositeSections.Num(), M->Notifies.Num());
  return BPGenAssets::SaveAsset(M);
}

// "object_stub": {path, class} - an empty object of that class where the kit lacks a game asset (a SoundCue a notify names). Only created when
// nothing is at the path, never packed; in the game the reference resolves to the real asset by path.
bool BPGenAssets::MakeObjectStub(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = AnimJStr(A, TEXT("path"));
  if (!CheckKeys(A, {TEXT("type"), TEXT("path"), TEXT("class")}, TEXT("object_stub ") + Path, Err)) return false;
  UClass* C = BPGenTypes::LoadClassChecked(AnimJStr(A, TEXT("class")));
  if (!C || C->HasAnyClassFlags(CLASS_Abstract)) { Err = TEXT("object_stub: class not found or abstract ") + AnimJStr(A, TEXT("class")); return false; }
  const FString Name = FPackageName::GetShortName(Path);
  if (UObject* Have = LoadObject<UObject>(nullptr, *(Path + TEXT(".") + Name), nullptr, LOAD_NoWarn | LOAD_Quiet)) {
    if (!Have->IsA(C)) { Err = TEXT("object_stub: ") + Path + TEXT(" exists as ") + Have->GetClass()->GetName(); return false; }
    return true;
  }
  UPackage* Pkg = CreatePackage(*Path);
  UObject* O = NewObject<UObject>(Pkg, C, *Name, RF_Public | RF_Standalone);
  FAssetRegistryModule::AssetCreated(O); Pkg->MarkPackageDirty();
  UE_LOG(LogBPGen, Display, TEXT("BPGEN object stub %s (%s)"), *Path, *C->GetName());
  return BPGenAssets::SaveAsset(O);
}

// "blendspace1d": {path, skeleton, axis {name, min, max, grid}, samples [[anim, value]], smoothing?, scale_animation?}. Built from scratch each
// time. The grid elements the runtime reads (GridSamples) are normally computed by the blend space editor window only; here they are
// computed the same way (each grid point weighted linearly between its two neighbouring samples, outside the samples fully on the outer one).
bool BPGenAssets::MakeBlendSpace1D(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = AnimJStr(A, TEXT("path")); const FString Where = TEXT("blendspace1d ") + Path;
  if (!CheckKeys(A, {TEXT("type"), TEXT("path"), TEXT("skeleton"), TEXT("axis"), TEXT("samples"), TEXT("smoothing"), TEXT("scale_animation")}, Where, Err)) return false;
  USkeleton* Skel = Cast<USkeleton>(BPGenTypes::LoadObj(AnimJStr(A, TEXT("skeleton"))));
  if (!Skel) { Err = Where + TEXT(": skeleton not found ") + AnimJStr(A, TEXT("skeleton")); return false; }
  const TSharedPtr<FJsonObject>* AxisP = nullptr;
  if (!A->TryGetObjectField(TEXT("axis"), AxisP) || !CheckKeys(*AxisP, {TEXT("name"), TEXT("min"), TEXT("max"), TEXT("grid")}, Where + TEXT(" axis"), Err)) {
    if (Err.IsEmpty()) Err = Where + TEXT(": axis missing"); return false; }
  float Min = 0, Max = 0, GridF = 0, Smooth = 0;
  if (!NumField(*AxisP, TEXT("min"), Min, Where, Err, true) || !NumField(*AxisP, TEXT("max"), Max, Where, Err, true) || !NumField(*AxisP, TEXT("grid"), GridF, Where, Err, true)
      || !NumField(A, TEXT("smoothing"), Smooth, Where, Err, false)) return false;
  const int32 Grid = FMath::RoundToInt(GridF);
  if (Max <= Min || Grid < 1 || !FMath::IsNearlyEqual(GridF, (float)Grid)) { Err = Where + FString::Printf(TEXT(": axis %.3f..%.3f grid %.3f"), Min, Max, GridF); return false; }
  if (AnimJStr(*AxisP, TEXT("name")).IsEmpty()) { Err = Where + TEXT(": axis has no name"); return false; }
  if (Smooth < 0.f) { Err = Where + FString::Printf(TEXT(": smoothing %.3f is negative"), Smooth); return false; }
  const float Step = (Max - Min) / Grid;
  const TArray<TSharedPtr<FJsonValue>>* Samples = nullptr;
  if (!A->TryGetArrayField(TEXT("samples"), Samples) || Samples->Num() < 2) { Err = Where + TEXT(": needs at least two samples"); return false; }
  FString Name; UPackage* Pkg = BPGenAssets::MakePackage(Path, Name);
  if (UObject* Old = FindObject<UObject>(Pkg, *Name)) {   // rebuilt from scratch, as montage does
    Old->Rename(*MakeUniqueObjectName(GetTransientPackage(), Old->GetClass()).ToString(), GetTransientPackage(), REN_DontCreateRedirectors | REN_NonTransactional | REN_ForceNoResetLoaders);
    Old->ClearFlags(RF_Public | RF_Standalone); Old->MarkPendingKill();
  }
  UBlendSpace1D* BS = NewObject<UBlendSpace1D>(Pkg, *Name, RF_Public | RF_Standalone | RF_Transactional);
  BS->SetSkeleton(Skel);
  FStructProperty* PP = FindFProperty<FStructProperty>(UBlendSpaceBase::StaticClass(), TEXT("BlendParameters"));   // protected member
  if (!PP || PP->Struct != FBlendParameter::StaticStruct()) { Err = Where + TEXT(": BlendParameters property not found"); return false; }
  FBlendParameter* P0 = PP->ContainerPtrToValuePtr<FBlendParameter>(BS, 0);
  P0->DisplayName = AnimJStr(*AxisP, TEXT("name")); P0->Min = Min; P0->Max = Max; P0->GridNum = Grid;
  BS->InterpolationParam[0].InterpolationTime = Smooth; BS->InterpolationParam[0].InterpolationType = EFilterInterpolationType::BSIT_Average;
  bool bScale = false; if (A->HasField(TEXT("scale_animation")) && !A->TryGetBoolField(TEXT("scale_animation"), bScale)) { Err = Where + TEXT(": scale_animation must be a bool"); return false; }
  BS->bScaleAnimation = bScale;
  TArray<float> Values; TArray<int32> GridPoints;   // duplicates by grid point: two values within the off-grid tolerance are the same sample
  for (int32 i = 0; i < Samples->Num(); ++i) {
    const TArray<TSharedPtr<FJsonValue>>& S = (*Samples)[i]->AsArray();
    const FString W = FString::Printf(TEXT("%s sample %d"), *Where, i);
    if (S.Num() != 2 || S[0]->Type != EJson::String || S[1]->Type != EJson::Number) { Err = W + TEXT(": [anim, value] expected"); return false; }
    UAnimSequence* Seq = Cast<UAnimSequence>(BPGenTypes::LoadObj(S[0]->AsString()));
    if (!Seq) { Err = W + TEXT(": sequence not found ") + S[0]->AsString(); return false; }
    if (Seq->GetSkeleton() != Skel) { Err = W + TEXT(": ") + Seq->GetName() + TEXT(" is on another skeleton"); return false; }
    if (Seq->IsValidAdditive()) { Err = W + TEXT(": ") + Seq->GetName() + TEXT(" is additive"); return false; }
    const float V = (float)S[1]->AsNumber(); const float K = (V - Min) / Step;
    if (V < Min || V > Max) { Err = W + FString::Printf(TEXT(": value %.3f outside %.3f..%.3f"), V, Min, Max); return false; }
    if (!FMath::IsNearlyEqual(K, (float)FMath::RoundToInt(K), 1e-3f)) { Err = W + FString::Printf(TEXT(": value %.3f is off the grid (step %.3f)"), V, Step); return false; }
    if (GridPoints.Contains(FMath::RoundToInt(K))) { Err = W + FString::Printf(TEXT(": value %.3f twice"), V); return false; }
    if (!BS->AddSample(Seq, FVector(V, 0.f, 0.f))) { Err = W + TEXT(": AddSample refused ") + Seq->GetName(); return false; }
    Values.Add(V); GridPoints.Add(FMath::RoundToInt(K));
  }
  BS->ValidateSampleData();
  if (BS->GetNumberOfBlendSamples() != Samples->Num()) { Err = Where + FString::Printf(TEXT(": %d samples after validation, expected %d"), BS->GetNumberOfBlendSamples(), Samples->Num()); return false; }
  // grid elements (SBlendSpaceEditor1D::ResampleData + FLineElementGenerator, recomputed): point list sorted, element i at Min + i * Step
  TArray<int32> Order; for (int32 i = 0; i < Values.Num(); ++i) Order.Add(i);
  Order.Sort([&](int32 a, int32 b) { return Values[a] < Values[b]; });
  TArray<FEditorElement> Elements; Elements.AddDefaulted(Grid + 1);
  for (int32 g = 0; g <= Grid; ++g) {
    const float X = Min + Step * g; FEditorElement& E = Elements[g];
    if (X <= Values[Order[0]]) { E.Indices[0] = 0; E.Weights[0] = 1.f; continue; }
    if (X >= Values[Order.Last()]) { E.Indices[0] = Order.Num() - 1; E.Weights[0] = 1.f; continue; }
    for (int32 p = 0; p + 1 < Order.Num(); ++p) {
      const float A0 = Values[Order[p]], A1 = Values[Order[p + 1]];
      if (X >= A0 && X <= A1) { E.Indices[0] = p + 1; E.Weights[0] = (X - A0) / (A1 - A0); E.Indices[1] = p; E.Weights[1] = 1.f - E.Weights[0]; break; }
    }
  }
  BS->FillupGridElements(Order, Elements);   // point index -> sample index
  if (BS->GetGridSamples().Num() != Grid + 1) { Err = Where + FString::Printf(TEXT(": %d grid elements, expected %d"), BS->GetGridSamples().Num(), Grid + 1); return false; }
  for (int32 i = 0; i < BS->GetNumberOfBlendSamples(); ++i)
    if (!BS->GetBlendSample(i).bIsValid) { Err = Where + FString::Printf(TEXT(": sample %d invalid after validation"), i); return false; }
  FAssetRegistryModule::AssetCreated(BS); BS->MarkPackageDirty();
  UE_LOG(LogBPGen, Display, TEXT("BPGEN blendspace1d %s axis=%s %.1f..%.1f grid=%d samples=%d elements=%d"), *Name, *P0->DisplayName, Min, Max, Grid,
    BS->GetNumberOfBlendSamples(), BS->GetGridSamples().Num());
  return BPGenAssets::SaveAsset(BS);
}

// ---------- animplayer ----------
static UEdGraphPin* AnimPosePin(UEdGraphNode* N, EEdGraphPinDirection Dir) {   // as PosePin in BPGenAssets.cpp
  for (UEdGraphPin* P : N->Pins) {
    if (P->Direction != Dir) continue;
    UObject* Sub = P->PinType.PinSubCategoryObject.Get();
    if (Sub == FPoseLink::StaticStruct() || Sub == FComponentSpacePoseLink::StaticStruct()) return P;
  }
  return nullptr;
}

// "animplayer": a standalone animation blueprint: BlendSpacePlayer (X <- float variable) -> Slot -> Apply Additive (looping overlay sequence,
// Alpha <- float variable) -> Output Pose. For creatures driven by one speed value, with montages in the slot and an additive overlay on top.
bool BPGenAssets::MakeAnimPlayer(const TSharedPtr<FJsonObject>& A, FString& Err) {
  const FString Path = AnimJStr(A, TEXT("path")); const FString Where = TEXT("animplayer ") + Path;
  if (!CheckKeys(A, {TEXT("type"), TEXT("path"), TEXT("skeleton"), TEXT("blendspace"), TEXT("overlay"), TEXT("speed_var"), TEXT("alpha_var"), TEXT("alpha_default"),
                     TEXT("slot"), TEXT("add_slot"), TEXT("make_overlay_additive")}, Where, Err)) return false;
  USkeleton* Skel = Cast<USkeleton>(BPGenTypes::LoadObj(AnimJStr(A, TEXT("skeleton"))));
  if (!Skel) { Err = Where + TEXT(": skeleton not found ") + AnimJStr(A, TEXT("skeleton")); return false; }
  UBlendSpaceBase* BSp = Cast<UBlendSpaceBase>(BPGenTypes::LoadObj(AnimJStr(A, TEXT("blendspace"))));
  if (!BSp || BSp->GetSkeleton() != Skel) { Err = Where + TEXT(": blend space not found or on another skeleton ") + AnimJStr(A, TEXT("blendspace")); return false; }
  UAnimSequence* Ov = Cast<UAnimSequence>(BPGenTypes::LoadObj(AnimJStr(A, TEXT("overlay"))));
  if (!Ov || Ov->GetSkeleton() != Skel) { Err = Where + TEXT(": overlay not found or on another skeleton ") + AnimJStr(A, TEXT("overlay")); return false; }
  bool bAddSlot = false, bMakeAdd = false; float AlphaDefault = 1.f;   // JSON strings / numbers would be coerced by TryGetBoolField: check the type
  if (A->HasField(TEXT("add_slot")) && (A->GetField<EJson::None>(TEXT("add_slot"))->Type != EJson::Boolean || !A->TryGetBoolField(TEXT("add_slot"), bAddSlot))) { Err = Where + TEXT(": add_slot must be a bool"); return false; }
  if (A->HasField(TEXT("make_overlay_additive")) && (A->GetField<EJson::None>(TEXT("make_overlay_additive"))->Type != EJson::Boolean || !A->TryGetBoolField(TEXT("make_overlay_additive"), bMakeAdd))) { Err = Where + TEXT(": make_overlay_additive must be a bool"); return false; }
  if (!NumField(A, TEXT("alpha_default"), AlphaDefault, Where, Err, false)) return false;
  const FString SlotS = AnimJStr(A, TEXT("slot")); const FName Slot(*SlotS);
  if (SlotS.IsEmpty()) { Err = Where + TEXT(": no slot"); return false; }
  const bool bNewSlot = !Skel->ContainsSlotName(Slot);
  if (bNewSlot) {
    if (!bAddSlot) { Err = Where + TEXT(": slot \"") + SlotS + TEXT("\" unknown to ") + Skel->GetName(); return false; }
  }
  FString Name; UPackage* Pkg = BPGenAssets::MakePackage(Path, Name);
  if (FindObject<UAnimBlueprint>(Pkg, *Name)) { Err = Where + TEXT(": exists (delete the mod folder before the run)"); return false; }
  if (Ov->AdditiveAnimType != AAT_LocalSpaceBase && !bMakeAdd) { Err = Where + TEXT(": overlay ") + Ov->GetName() + TEXT(" is not additive"); return false; }
  for (const FBlendSample& S : BSp->GetBlendSamples()) if (S.Animation == Ov) { Err = Where + TEXT(": overlay ") + Ov->GetName() + TEXT(" is a sample of ") + BSp->GetName(); return false; }
  if (Ov->AdditiveAnimType != AAT_LocalSpaceBase) {
    Ov->Modify(); Ov->AdditiveAnimType = AAT_LocalSpaceBase; Ov->RefPoseType = ABPT_RefPose;
    // the property must be named: a bare PostEditChange() does not count as an additive change and leaves the compressed data non-additive
    FPropertyChangedEvent AddEv(UAnimSequence::StaticClass()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(UAnimSequence, AdditiveAnimType)));
    Ov->PostEditChangeProperty(AddEv);
    if (!Ov->IsValidAdditive()) { Err = Where + TEXT(": overlay ") + Ov->GetName() + TEXT(" not valid as additive"); return false; }
    if (!BPGenAssets::SaveAsset(Ov)) { Err = Where + TEXT(": saving the overlay failed"); return false; }
    UE_LOG(LogBPGen, Display, TEXT("BPGEN overlay made additive %s"), *Ov->GetName());
  }
  bool bSlotAdded = false;
  if (bNewSlot) { Skel->Modify(); Skel->SetSlotGroupName(Slot, FAnimSlotGroup::DefaultGroupName); bSlotAdded = true; }
  UAnimBlueprint* BP = Cast<UAnimBlueprint>(FKismetEditorUtilities::CreateBlueprint(UAnimInstance::StaticClass(), Pkg, *Name, BPTYPE_Normal,
      UAnimBlueprint::StaticClass(), UAnimBlueprintGeneratedClass::StaticClass(), FName("BPGen")));
  if (!BP) { Err = Where + TEXT(": CreateBlueprint failed"); return false; }
  BP->TargetSkeleton = Skel;
  const FName SpeedVar(*AnimJStr(A, TEXT("speed_var"), TEXT("Speed"))), AlphaVar(*AnimJStr(A, TEXT("alpha_var"), TEXT("OverlayAlpha")));
  FEdGraphPinType FloatT; FloatT.PinCategory = UEdGraphSchema_K2::PC_Float;
  if (!FBlueprintEditorUtils::AddMemberVariable(BP, SpeedVar, FloatT, TEXT("0.0"))
      || !FBlueprintEditorUtils::AddMemberVariable(BP, AlphaVar, FloatT, FString::SanitizeFloat(AlphaDefault))) { Err = Where + TEXT(": AddMemberVariable failed"); return false; }
  FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
  UEdGraph* G = nullptr; for (UEdGraph* FG : BP->FunctionGraphs) if (FG->IsA<UAnimationGraph>()) G = FG;
  TArray<UAnimGraphNode_Root*> Roots; if (G) G->GetNodesOfClass(Roots);
  if (!G || Roots.Num() == 0) { Err = Where + TEXT(": no AnimGraph / Output Pose"); return false; }
  const UEdGraphSchema* Schema = G->GetSchema();
  auto LinkVar = [&](UEdGraphNode* N, const FName Var, const TCHAR* PinName, int32 X, int32 Y) -> bool {
    UEdGraphPin* Pin = N->FindPin(PinName);
    if (!Pin) { Err = Where + TEXT(": node has no pin ") + PinName; return false; }
    FGraphNodeCreator<UK2Node_VariableGet> CG(*G); UK2Node_VariableGet* GetV = CG.CreateNode(); GetV->NodePosX = X; GetV->NodePosY = Y;
    GetV->VariableReference.SetSelfMember(Var); CG.Finalize();
    UEdGraphPin* Out = nullptr; for (UEdGraphPin* P : GetV->Pins) if (P->Direction == EGPD_Output) Out = P;
    if (!Out || !Schema->TryCreateConnection(Out, Pin)) { Err = Where + TEXT(": variable->") + PinName + TEXT(" link failed: ") + Var.ToString(); return false; }
    return true;
  };
  FGraphNodeCreator<UAnimGraphNode_BlendSpacePlayer> CB(*G); UAnimGraphNode_BlendSpacePlayer* BSPn = CB.CreateNode(); BSPn->NodePosX = -900;
  BSPn->Node.BlendSpace = BSp; BSPn->Node.bLoop = true; CB.Finalize();
  if (!LinkVar(BSPn, SpeedVar, TEXT("X"), -1150, 0)) return false;
  FGraphNodeCreator<UAnimGraphNode_Slot> CS(*G); UAnimGraphNode_Slot* SN = CS.CreateNode(); SN->NodePosX = -600; SN->Node.SlotName = Slot; CS.Finalize();
  if (!Schema->TryCreateConnection(AnimPosePin(BSPn, EGPD_Output), AnimPosePin(SN, EGPD_Input))) { Err = Where + TEXT(": link blend space->Slot failed"); return false; }
  FGraphNodeCreator<UAnimGraphNode_SequencePlayer> CP(*G); UAnimGraphNode_SequencePlayer* SP = CP.CreateNode(); SP->NodePosX = -600; SP->NodePosY = 250;
  SP->Node.Sequence = Ov; SP->Node.bLoopAnimation = true; CP.Finalize();
  FGraphNodeCreator<UAnimGraphNode_ApplyAdditive> CA(*G); UAnimGraphNode_ApplyAdditive* AA = CA.CreateNode(); AA->NodePosX = -300; CA.Finalize();
  UEdGraphPin* BasePin = AA->FindPin(TEXT("Base")); UEdGraphPin* AddPin = AA->FindPin(TEXT("Additive"));
  if (!BasePin || !AddPin) { Err = Where + TEXT(": Apply Additive has no Base / Additive pin"); return false; }
  if (!Schema->TryCreateConnection(AnimPosePin(SN, EGPD_Output), BasePin) || !Schema->TryCreateConnection(AnimPosePin(SP, EGPD_Output), AddPin)) {
    Err = Where + TEXT(": link ->Apply Additive failed"); return false; }
  if (!LinkVar(AA, AlphaVar, TEXT("Alpha"), -450, 450)) return false;
  Roots[0]->NodePosX = 0;
  if (!Schema->TryCreateConnection(AnimPosePin(AA, EGPD_Output), AnimPosePin(Roots[0], EGPD_Input))) { Err = Where + TEXT(": link ->Output Pose failed"); return false; }
  FCompilerResultsLog Results; Results.bSilentMode = false;
  FKismetEditorUtilities::CompileBlueprint(BP, EBlueprintCompileOptions::SkipGarbageCollection, &Results);
  UE_LOG(LogBPGen, Display, TEXT("BPGEN compiled %s errors=%d warnings=%d"), *Path, Results.NumErrors, Results.NumWarnings);
  if (BP->Status == BS_Error || Results.NumErrors > 0 || Results.NumWarnings > 0) { Err = FString::Printf(TEXT("%s: compile errors=%d warnings=%d"), *Where, Results.NumErrors, Results.NumWarnings); return false; }
  if (bSlotAdded) {
    if (!BPGenAssets::SaveAsset(Skel)) { Err = Where + TEXT(": saving the skeleton failed"); return false; }
    UE_LOG(LogBPGen, Display, TEXT("BPGEN skeleton slot added %s.%s"), *Skel->GetSlotGroupName(Slot).ToString(), *SlotS);
  }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN animplayer %s blendspace=%s slot=%s overlay=%s"), *Name, *BSp->GetName(), *SlotS, *Ov->GetName());
  return BPGenAssets::SaveAsset(BP);
}

// ---------- read-back ----------
static FString LinkStr(const FAnimLinkableElement& L) {
  static const TCHAR* Methods[] = {TEXT("Absolute"), TEXT("Relative"), TEXT("Proportional")};
  const int32 M = (int32)L.GetLinkMethod();
  return FString::Printf(TEXT("seg=%d:%d link=%s"), L.GetSlotIndex(), L.GetSegmentIndex(), M >= 0 && M < 3 ? Methods[M] : TEXT("?"));
}

TArray<FString> BPGenAssets::DescribeAnim(UAnimSequenceBase* S) {
  TArray<FString> L;
  if (!S) { L.Add(TEXT("ANIM none")); return L; }
  L.Add(FString::Printf(TEXT("ANIM %s class=%s length=%.4f ratescale=%.4f skeleton=%s"), *S->GetName(), *S->GetClass()->GetName(), S->SequenceLength, S->RateScale,
    S->GetSkeleton() ? *S->GetSkeleton()->GetPathName() : TEXT("-")));
  if (UAnimMontage* M = Cast<UAnimMontage>(S)) {
    L.Add(FString::Printf(TEXT("BLEND in=%.4f out=%.4f trigger=%.4f auto=%d"), M->BlendIn.GetBlendTime(), M->BlendOut.GetBlendTime(), M->BlendOutTriggerTime, M->bEnableAutoBlendOut ? 1 : 0));
    for (int32 t = 0; t < M->SlotAnimTracks.Num(); ++t) {
      const FSlotAnimationTrack& T = M->SlotAnimTracks[t];
      L.Add(FString::Printf(TEXT("SLOT %d %s group=%s"), t, *T.SlotName.ToString(), M->GetSkeleton() ? *M->GetSkeleton()->GetSlotGroupName(T.SlotName).ToString() : TEXT("-")));
      for (int32 i = 0; i < T.AnimTrack.AnimSegments.Num(); ++i) {
        const FAnimSegment& G = T.AnimTrack.AnimSegments[i];
        L.Add(FString::Printf(TEXT("SEGMENT %d %d anim=%s pos=%.4f start=%.4f end=%.4f rate=%.4f loops=%d"), t, i, G.AnimReference ? *G.AnimReference->GetPathName() : TEXT("-"),
          G.StartPos, G.AnimStartTime, G.AnimEndTime, G.AnimPlayRate, G.LoopingCount));
      }
    }
    for (int32 i = 0; i < M->CompositeSections.Num(); ++i) {
      const FCompositeSection& C = M->CompositeSections[i];
      L.Add(FString::Printf(TEXT("SECTION %d %s time=%.4f next=%s %s"), i, *C.SectionName.ToString(), C.GetTime(), *C.NextSectionName.ToString(), *LinkStr(C)));
    }
  }
  for (int32 i = 0; i < S->Notifies.Num(); ++i) {
    const FAnimNotifyEvent& E = S->Notifies[i];
    UObject* N = E.Notify ? (UObject*)E.Notify : (UObject*)E.NotifyStateClass;
    L.Add(FString::Printf(TEXT("NOTIFY %d name=%s class=%s object=%s time=%.4f duration=%.4f track=%d %s end=%s"), i, *E.NotifyName.ToString(),
      N ? *N->GetClass()->GetPathName() : TEXT("-"), N ? *N->GetName() : TEXT("-"), E.GetTime(), E.GetDuration(), E.TrackIndex, *LinkStr(E),
      E.NotifyStateClass ? *LinkStr(E.EndLink) : TEXT("-")));
    if (!N) continue;
    // the values: every property the notify's own classes add (below AnimNotify / AnimNotifyState)
    UClass* Base = E.Notify ? UAnimNotify::StaticClass() : UAnimNotifyState::StaticClass();
    for (TFieldIterator<FProperty> It(N->GetClass()); It; ++It) {
      if (It->GetOwnerClass() && It->GetOwnerClass()->IsChildOf(Base) && It->GetOwnerClass() != Base && It->GetName() != TEXT("UberGraphFrame")) {
        FString V; It->ExportTextItem(V, It->ContainerPtrToValuePtr<void>(N), nullptr, N, PPF_None);
        L.Add(FString::Printf(TEXT("VALUE %d %s=%s"), i, *It->GetName(), *V));
      }
    }
  }
  return L;
}

void BPGenAssets::DumpAnim(const FString& Path) {
  for (const FString& Line : DescribeAnim(Cast<UAnimSequenceBase>(BPGenTypes::LoadObj(Path)))) UE_LOG(LogBPGen, Display, TEXT("DUMPANIM %s"), *Line);
}

TArray<FString> UBPGenAnimLib::DescribeAnim(UAnimSequenceBase* Anim) { return BPGenAssets::DescribeAnim(Anim); }

TArray<FString> BPGenAssets::DescribeAnimAsset(UObject* Asset) {
  TArray<FString> L;
  if (UBlendSpaceBase* BS = Cast<UBlendSpaceBase>(Asset)) {
    const FBlendParameter& P = BS->GetBlendParameter(0); const UBlendSpace1D* B1 = Cast<UBlendSpace1D>(BS);
    L.Add(FString::Printf(TEXT("BLENDSPACE %s class=%s skeleton=%s axis=%s min=%.4f max=%.4f grid=%d interp=%.4f scale=%d"), *BS->GetName(), *BS->GetClass()->GetName(),
      BS->GetSkeleton() ? *BS->GetSkeleton()->GetPathName() : TEXT("-"), *P.DisplayName, P.Min, P.Max, P.GridNum, BS->InterpolationParam[0].InterpolationTime, B1 && B1->bScaleAnimation ? 1 : 0));
    for (int32 i = 0; i < BS->GetBlendSamples().Num(); ++i) { const FBlendSample& S = BS->GetBlendSample(i);
      L.Add(FString::Printf(TEXT("SAMPLE %d anim=%s value=%.4f valid=%d"), i, S.Animation ? *S.Animation->GetPathName() : TEXT("-"), S.SampleValue.X, S.bIsValid ? 1 : 0)); }
    for (int32 i = 0; i < BS->GetGridSamples().Num(); ++i) { const FEditorElement& E = BS->GetGridSamples()[i];
      L.Add(FString::Printf(TEXT("ELEMENT %d idx=%d,%d,%d w=%.4f,%.4f,%.4f"), i, E.Indices[0], E.Indices[1], E.Indices[2], E.Weights[0], E.Weights[1], E.Weights[2])); }
    return L;
  }
  if (UAnimBlueprint* BP = Cast<UAnimBlueprint>(Asset)) {
    L.Add(FString::Printf(TEXT("ABP %s skeleton=%s status=%d"), *BP->GetName(), BP->TargetSkeleton ? *BP->TargetSkeleton->GetPathName() : TEXT("-"), (int32)BP->Status));
    // a full compile moves the default into the class default object and empties FBPVariableDescription::DefaultValue: read it from there
    UObject* CDO = BP->GeneratedClass ? BP->GeneratedClass->GetDefaultObject(false) : nullptr;
    for (FBPVariableDescription& V : BP->NewVariables) {
      FString Def = V.DefaultValue;
      if (FProperty* VP = CDO ? BP->GeneratedClass->FindPropertyByName(V.VarName) : nullptr) {
        if (FFloatProperty* FP = CastField<FFloatProperty>(VP)) Def = FString::SanitizeFloat(FP->GetPropertyValue_InContainer(CDO));
        else { Def.Reset(); VP->ExportTextItem(Def, VP->ContainerPtrToValuePtr<void>(CDO), nullptr, CDO, PPF_None); }
      }
      L.Add(FString::Printf(TEXT("VAR %s type=%s default=%s"), *V.VarName.ToString(), *V.VarType.PinCategory.ToString(), *Def));
    }
    for (UEdGraph* G : BP->FunctionGraphs) if (G->IsA<UAnimationGraph>()) {
      TArray<UEdGraphNode*> Nodes = G->Nodes; Nodes.Sort([](const UEdGraphNode& a, const UEdGraphNode& b) { return a.GetClass()->GetName() < b.GetClass()->GetName(); });
      for (UEdGraphNode* N : Nodes) {
        FString D;
        if (auto* B = Cast<UAnimGraphNode_BlendSpacePlayer>(N)) D = FString::Printf(TEXT(" blendspace=%s loop=%d"), B->Node.BlendSpace ? *B->Node.BlendSpace->GetPathName() : TEXT("-"), B->Node.bLoop ? 1 : 0);
        else if (auto* S = Cast<UAnimGraphNode_Slot>(N)) D = FString::Printf(TEXT(" slot=%s group=%s"), *S->Node.SlotName.ToString(), BP->TargetSkeleton ? *BP->TargetSkeleton->GetSlotGroupName(S->Node.SlotName).ToString() : TEXT("-"));
        else if (auto* P = Cast<UAnimGraphNode_SequencePlayer>(N)) D = FString::Printf(TEXT(" sequence=%s loop=%d additive=%d"), P->Node.Sequence ? *P->Node.Sequence->GetPathName() : TEXT("-"), P->Node.bLoopAnimation ? 1 : 0,
                                                                         P->Node.Sequence ? (int32)P->Node.Sequence->GetAdditiveAnimType() : -1);
        else if (auto* V = Cast<UK2Node_VariableGet>(N)) D = TEXT(" var=") + V->VariableReference.GetMemberName().ToString();
        L.Add(TEXT("NODE ") + N->GetClass()->GetName() + D);
        for (UEdGraphPin* Pin : N->Pins) if (Pin->Direction == EGPD_Input) for (UEdGraphPin* From : Pin->LinkedTo) {
          UEdGraphNode* FN = From->GetOwningNode(); const UK2Node_VariableGet* FV = Cast<UK2Node_VariableGet>(FN);
          L.Add(FString::Printf(TEXT("LINK %s -> %s.%s"), FV ? *(TEXT("var:") + FV->VariableReference.GetMemberName().ToString()) : *FN->GetClass()->GetName(), *N->GetClass()->GetName(), *Pin->PinName.ToString()));
        }
      }
    }
    return L;
  }
  L.Add(TEXT("ASSET unsupported ") + (Asset ? Asset->GetPathName() : FString(TEXT("none"))));
  return L;
}
TArray<FString> UBPGenAnimLib::DescribeAnimAsset(UObject* Asset) { return BPGenAssets::DescribeAnimAsset(Asset); }
