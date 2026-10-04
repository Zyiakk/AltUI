#include "BPGenCommandlet.h"
#include "BPGenAssets.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "HAL/PlatformMemory.h"
#include "HAL/FileManager.h"
#include "Misc/SecureHash.h"
#include "Misc/PackageName.h"
#include "Serialization/JsonWriter.h"
#include "UObject/UObjectGlobals.h"
DEFINE_LOG_CATEGORY(LogBPGen);
UBPGenCommandlet::UBPGenCommandlet() { IsClient = false; IsServer = false; IsEditor = true; LogToConsole = true; }

// ---- incremental builds: one hash per asset path over all its entries (+ the signature files); unchanged and on disk -> skipped
static TMap<FString, FString> GOldHashes, GNewHashes;
static TSet<FString> GSkip;
static bool GIncremental = false;
static TArray<FString> GFreshPrefixes;

static FString EntryJson(const TSharedPtr<FJsonObject>& O) {
  FString S; TSharedRef<TJsonWriter<>> W = TJsonWriterFactory<>::Create(&S); FJsonSerializer::Serialize(O.ToSharedRef(), W); return S;
}

static bool LoadAssets(const FString& File, TArray<TSharedPtr<FJsonValue>>& Out) {
  FString Text; if (!FFileHelper::LoadFileToString(Text, *File)) { UE_LOG(LogBPGen, Error, TEXT("BPGEN cannot read %s"), *File); return false; }
  TSharedPtr<FJsonObject> Root; TSharedRef<TJsonReader<>> R = TJsonReaderFactory<>::Create(Text);
  if (!FJsonSerializer::Deserialize(R, Root) || !Root.IsValid()) { UE_LOG(LogBPGen, Error, TEXT("BPGEN json parse error in %s"), *File); return false; }
  const TArray<TSharedPtr<FJsonValue>>* Assets = nullptr;
  if (!Root->TryGetArrayField(TEXT("assets"), Assets)) { UE_LOG(LogBPGen, Error, TEXT("BPGEN no assets in %s"), *File); return false; }
  Out = *Assets; return true;
}

static FString PackageFile(const FString& Path) { return FPackageName::LongPackageNameToFilename(Path, FPackageName::GetAssetPackageExtension()); }

// Pre-pass over every manifest file: new hashes, the set to skip, and fresh starts for changed assets bpgen creates itself.
static bool PlanIncremental(const TArray<FString>& Files, const FString& SigHash) {
  TMap<FString, FString> Joined; TSet<FString> Created;
  for (const FString& F : Files) {
    TArray<TSharedPtr<FJsonValue>> Assets; if (!LoadAssets(F, Assets)) return false;
    for (const auto& V : Assets) {
      const TSharedPtr<FJsonObject> O = V->AsObject(); const FString Path = O->GetStringField(TEXT("path"));
      Joined.FindOrAdd(Path) += EntryJson(O);
      FString Mode; if (!O->TryGetStringField(TEXT("mode"), Mode) || Mode != TEXT("augment")) Created.Add(Path);
    }
  }
  TSet<FString> Changed;
  for (const auto& KV : Joined) {
    const FString H = FMD5::HashAnsiString(*(SigHash + KV.Value)); GNewHashes.Add(KV.Key, H);
    const FString* Old = GOldHashes.Find(KV.Key);
    if (!(Old && *Old == H && FPaths::FileExists(PackageFile(KV.Key)))) Changed.Add(KV.Key);
  }
  // An asset that refers to a changed one is rebuilt too (transitively): a fresh start deletes and recreates the changed
  // class, and a skipped blueprint that was loaded against the old one keeps pins to a dead class (seen with W_ModField
  // -> BP_AltUIManager). References are found as the path string in the asset's own entries.
  for (;;) {
    TSet<FString> Add;
    for (const auto& KV : Joined) {
      if (Changed.Contains(KV.Key)) continue;
      for (const FString& C : Changed) if (KV.Value.Contains(C + TEXT(".")) || KV.Value.Contains(C + TEXT("\""))) { Add.Add(KV.Key); break; }
    }
    if (Add.Num() == 0) break;
    Changed.Append(Add);
  }
  int32 NSkip = 0, NBuild = 0;
  for (const auto& KV : Joined) {
    const bool bOnDisk = FPaths::FileExists(PackageFile(KV.Key));
    if (!Changed.Contains(KV.Key)) { GSkip.Add(KV.Key); ++NSkip; continue; }
    ++NBuild;
    // changed -> built from scratch (no stale functions), but only below -freshprefix=: the stubs of the game's classes refer
    // to each other and are always rewritten in place - deleting one breaks the pin types of the others that load meanwhile
    bool bFresh = false; for (const FString& P : GFreshPrefixes) bFresh |= KV.Key.StartsWith(P);
    if (bOnDisk && bFresh && Created.Contains(KV.Key)) IFileManager::Get().Delete(*PackageFile(KV.Key));
  }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN incremental: %d to build, %d unchanged"), NBuild, NSkip); return true;
}

static void LogMem(const FString& What) {
  const FPlatformMemoryStats M = FPlatformMemory::GetStats();
  UE_LOG(LogBPGen, Display, TEXT("BPGEN mem %s used=%lluMB peak=%lluMB"), *What, (uint64)M.UsedPhysical >> 20, (uint64)M.PeakUsedPhysical >> 20);
}

static bool RunManifest(const FString& File) {
  TArray<TSharedPtr<FJsonValue>> Assets; if (!LoadAssets(File, Assets)) return false;
  BPGenAssets::BaseDir = FPaths::GetPath(File);
  for (const auto& V : Assets) {
    const FString Path = V->AsObject()->GetStringField(TEXT("path"));
    if (GIncremental && GSkip.Contains(Path)) { UE_LOG(LogBPGen, Display, TEXT("BPGEN skip %s"), *Path); continue; }
    FString Err;
    if (!BPGenAssets::Process(V->AsObject(), Err)) { UE_LOG(LogBPGen, Error, TEXT("BPGEN FAILED %s: %s"), *File, *Err); return false; }
    CollectGarbage(GARBAGE_COLLECTION_KEEPFLAGS);   // saved assets are on disk; free what building them took
    LogMem(Path);
  }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN manifest ok %s"), *File); return true;
}

int32 UBPGenCommandlet::Main(const FString& Params) {
  UE_LOG(LogBPGen, Display, TEXT("BPGEN version 0.1 params=%s"), *Params);
  if (Params.Contains(TEXT("-selftest"))) { UE_LOG(LogBPGen, Display, TEXT("BPGEN selftest ok")); return 0; }
  FString Manifest, DumpPath;
  if (FParse::Value(*Params, TEXT("-manifest="), Manifest)) {
    TArray<FString> Files;
    if (Manifest.EndsWith(TEXT(".txt"))) {
      FString List; FFileHelper::LoadFileToString(List, *Manifest);
      TArray<FString> Lines; List.ParseIntoArrayLines(Lines);
      const FString Dir = FPaths::GetPath(Manifest);
      for (FString L : Lines) { L.TrimStartAndEndInline(); if (L.IsEmpty() || L.StartsWith(TEXT("#"))) continue; Files.Add(FPaths::Combine(Dir, L)); }
    } else Files.Add(Manifest);
    // -hashes=<file>: skip assets whose entries (and the signature files in -sigfiles=a,b next to the manifest) did not change
    FString HashFile, SigFiles;
    if (FParse::Value(*Params, TEXT("-hashes="), HashFile)) {
      GIncremental = true;
      FString Old; if (FFileHelper::LoadFileToString(Old, *HashFile)) {
        TSharedPtr<FJsonObject> O; TSharedRef<TJsonReader<>> R = TJsonReaderFactory<>::Create(Old);
        if (FJsonSerializer::Deserialize(R, O) && O.IsValid()) for (const auto& KV : O->Values) GOldHashes.Add(KV.Key, KV.Value->AsString());
      }
      FString Fresh; if (FParse::Value(*Params, TEXT("-freshprefix="), Fresh)) Fresh.ParseIntoArray(GFreshPrefixes, TEXT(","), true);
      FString Sig;
      if (FParse::Value(*Params, TEXT("-sigfiles="), SigFiles)) {
        TArray<FString> SF; SigFiles.ParseIntoArray(SF, TEXT(","), true);
        for (const FString& F : SF) { FString T; FFileHelper::LoadFileToString(T, *FPaths::Combine(FPaths::GetPath(Manifest), F)); Sig += FMD5::HashAnsiString(*T); }
      }
      if (!PlanIncremental(Files, Sig)) return 1;
    }
    for (const FString& F : Files) if (!RunManifest(F)) return 1;
    if (GIncremental) {   // only after every manifest went through: a failed run keeps the old hashes, so it is redone next time
      TSharedRef<FJsonObject> O = MakeShared<FJsonObject>(); for (const auto& KV : GNewHashes) O->SetStringField(KV.Key, KV.Value);
      FString S; TSharedRef<TJsonWriter<>> W = TJsonWriterFactory<>::Create(&S); FJsonSerializer::Serialize(O, W);
      FFileHelper::SaveStringToFile(S, *HashFile);
    }
  }
  if (FParse::Value(*Params, TEXT("-dump="), DumpPath, /*bShouldStopOnSeparator*/ false)) {   // one or more class paths, comma separated (one editor start instead of one per dump)
    TArray<FString> Paths; DumpPath.ParseIntoArray(Paths, TEXT(","), true);
    for (const FString& P : Paths) BPGenAssets::Dump(P);
  }
  FString ExportArg, DumpMatArg;
  if (FParse::Value(*Params, TEXT("-exportfbx="), ExportArg, false)) {   // object=file[,object=file]
    TArray<FString> Pairs; ExportArg.ParseIntoArray(Pairs, TEXT(","), true);
    for (const FString& P : Pairs) { FString O, F; if (P.Split(TEXT("="), &O, &F)) BPGenAssets::ExportFbx(O, F); }
  }
  if (FParse::Value(*Params, TEXT("-dumpmat="), DumpMatArg, false)) {    // material paths, comma separated
    TArray<FString> Paths; DumpMatArg.ParseIntoArray(Paths, TEXT(","), true);
    for (const FString& P : Paths) BPGenAssets::DumpMaterial(P);
  }
  FString GraphArg;
  if (FParse::Value(*Params, TEXT("-dumpgraph="), GraphArg, false)) {    // base materials, comma separated
    TArray<FString> Paths; GraphArg.ParseIntoArray(Paths, TEXT(","), true);
    for (const FString& P : Paths) BPGenAssets::DumpMaterialGraph(P);
  }
  FString ClothArg;
  if (FParse::Value(*Params, TEXT("-dumpcloth="), ClothArg, false)) {    // skeletal meshes, comma separated
    TArray<FString> Paths; ClothArg.ParseIntoArray(Paths, TEXT(","), true);
    for (const FString& P : Paths) BPGenAssets::DumpCloth(P);
  }
  FString SimArg;
  if (FParse::Value(*Params, TEXT("-simcloth="), SimArg, false)) {      // skeletal meshes, comma separated
    TArray<FString> Paths; SimArg.ParseIntoArray(Paths, TEXT(","), true);
    for (const FString& P : Paths) BPGenAssets::SimCloth(P);
  }
  if (Params.Contains(TEXT("-fastexit"))) {   // everything is saved synchronously above; the engine teardown alone takes ~50 s after a manifest run
    UE_LOG(LogBPGen, Display, TEXT("BPGEN OK (fast exit)")); GLog->Flush();
    FPlatformMisc::RequestExit(true);
  }
  return 0;
}
