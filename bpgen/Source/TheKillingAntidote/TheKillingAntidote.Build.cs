using UnrealBuildTool;
// Stand-ins for native types of the game's own module (/Script/TheKillingAntidote) that the kit does not have: AltUI's
// Blueprints can then name them; in the game the paths resolve to the real types. Never packed (no binaries in a pak).
public class TheKillingAntidote : ModuleRules {
  public TheKillingAntidote(ReadOnlyTargetRules Target) : base(Target) {
    PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
    PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
  }
}
