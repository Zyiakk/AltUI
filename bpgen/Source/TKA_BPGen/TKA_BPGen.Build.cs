using UnrealBuildTool;
public class TKA_BPGen : ModuleRules {
  public TKA_BPGen(ReadOnlyTargetRules Target) : base(Target) {
    PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
    PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
    PrivateDependencyModuleNames.AddRange(new string[] {
      "UnrealEd", "Kismet", "KismetCompiler", "BlueprintGraph", "UMG", "UMGEditor",
      "Json", "JsonUtilities", "AssetRegistry", "AssetTools", "DataTableEditor", "InputCore", "Slate", "SlateCore", "ImageWrapper" });
  }
}
