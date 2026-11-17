#pragma once
#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
class UPackage;
class UAnimSequenceBase;

namespace BPGenAssets {
  bool Process(const TSharedPtr<FJsonObject>& A, FString& Err);   // dispatch by "type"
  extern FString BaseDir;   // directory of the current manifest file (for relative "file" paths)
  bool SaveAsset(UObject* Asset);
  UPackage* MakePackage(const FString& PackagePath, FString& OutName);
  void Dump(const FString& PackagePath);
  bool ExportFbx(const FString& ObjectPath, const FString& File);   // any exportable asset (SkeletalMesh -> FBX), exporter by extension
  void DumpMaterial(const FString& MaterialPath);
  void DumpMaterialGraph(const FString& MaterialPath);
  void DumpCloth(const FString& MeshPath);
  // animation (BPGenAnim.cpp)
  bool AddNotifies(UAnimSequenceBase* S, const TArray<TSharedPtr<FJsonValue>>& Notes, FString& Err);   // [name, t] or {time, class, duration, values, name, track}
  bool MakeMontage(const TSharedPtr<FJsonObject>& A, FString& Err);
  bool MakeObjectStub(const TSharedPtr<FJsonObject>& A, FString& Err);
  bool MakeBlendSpace1D(const TSharedPtr<FJsonObject>& A, FString& Err);
  bool MakeAnimPlayer(const TSharedPtr<FJsonObject>& A, FString& Err);
  bool MakeSubobjectDefaults(const TSharedPtr<FJsonObject>& A, FString& Err);   // BPGenAssets.cpp
  TArray<FString> DescribeAnimAsset(UObject* Asset);   // BLENDSPACE / SAMPLE / ELEMENT lines, ABP / VAR / NODE / LINK lines
  TArray<FString> DescribeAnim(UAnimSequenceBase* S);   // ANIM / BLEND / SLOT / SEGMENT / SECTION / NOTIFY / VALUE lines
  void DumpAnim(const FString& Path);                   // DUMPANIM lines (DescribeAnim) of a sequence or montage
  void SimCloth(const FString& MeshPath);    // SIMCLOTH lines: the mesh in a game world, ticked and moved - how far its cloth moves   // DUMPCLOTH lines: a mesh's clothing assets, their config and weight maps                // DUMPGRAPH lines: expressions and their inputs                     // DUMPMAT lines: every scalar/vector/texture/switch parameter
}
