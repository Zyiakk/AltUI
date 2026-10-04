#pragma once
#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
class UPackage;

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
  void SimCloth(const FString& MeshPath);    // SIMCLOTH lines: the mesh in a game world, ticked and moved - how far its cloth moves   // DUMPCLOTH lines: a mesh's clothing assets, their config and weight maps                // DUMPGRAPH lines: expressions and their inputs                     // DUMPMAT lines: every scalar/vector/texture/switch parameter
}
