#include "BPGenCommandlet.h"
#include "BPGenAssets.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
DEFINE_LOG_CATEGORY(LogBPGen);
UBPGenCommandlet::UBPGenCommandlet() { IsClient = false; IsServer = false; IsEditor = true; LogToConsole = true; }

static bool RunManifest(const FString& File) {
  FString Text; if (!FFileHelper::LoadFileToString(Text, *File)) { UE_LOG(LogBPGen, Error, TEXT("BPGEN cannot read %s"), *File); return false; }
  TSharedPtr<FJsonObject> Root; TSharedRef<TJsonReader<>> R = TJsonReaderFactory<>::Create(Text);
  if (!FJsonSerializer::Deserialize(R, Root) || !Root.IsValid()) { UE_LOG(LogBPGen, Error, TEXT("BPGEN json parse error in %s"), *File); return false; }
  BPGenAssets::BaseDir = FPaths::GetPath(File);
  const TArray<TSharedPtr<FJsonValue>>* Assets = nullptr;
  if (!Root->TryGetArrayField(TEXT("assets"), Assets)) { UE_LOG(LogBPGen, Error, TEXT("BPGEN no assets in %s"), *File); return false; }
  for (const auto& V : *Assets) {
    FString Err;
    if (!BPGenAssets::Process(V->AsObject(), Err)) { UE_LOG(LogBPGen, Error, TEXT("BPGEN FAILED %s: %s"), *File, *Err); return false; }
  }
  UE_LOG(LogBPGen, Display, TEXT("BPGEN manifest ok %s"), *File); return true;
}

int32 UBPGenCommandlet::Main(const FString& Params) {
  UE_LOG(LogBPGen, Display, TEXT("BPGEN version 0.1 params=%s"), *Params);
  if (Params.Contains(TEXT("-selftest"))) { UE_LOG(LogBPGen, Display, TEXT("BPGEN selftest ok")); return 0; }
  FString Manifest, DumpPath;
  if (FParse::Value(*Params, TEXT("-manifest="), Manifest)) {
    if (Manifest.EndsWith(TEXT(".txt"))) {
      FString List; FFileHelper::LoadFileToString(List, *Manifest);
      TArray<FString> Lines; List.ParseIntoArrayLines(Lines);
      const FString Dir = FPaths::GetPath(Manifest);
      for (FString L : Lines) { L.TrimStartAndEndInline(); if (L.IsEmpty() || L.StartsWith(TEXT("#"))) continue; if (!RunManifest(FPaths::Combine(Dir, L))) return 1; }
    } else if (!RunManifest(Manifest)) return 1;
  }
  if (FParse::Value(*Params, TEXT("-dump="), DumpPath)) BPGenAssets::Dump(DumpPath);
  return 0;
}
