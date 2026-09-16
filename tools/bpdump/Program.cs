using UAssetAPI;
using UAssetAPI.UnrealTypes;
using UAssetAPI.ExportTypes;
using UAssetAPI.Kismet;
using Newtonsoft.Json.Linq;
var a = new UAsset(args[0], EngineVersion.VER_UE4_27);
KismetSerializer.asset = a;
var root = new JObject();
foreach (var e in a.Exports) {
  if (e is FunctionExport fe) {
    root[fe.ObjectName.ToString()] = KismetSerializer.SerializeScript(fe.ScriptBytecode);
  }
}
File.WriteAllText(args[1], root.ToString());
Console.WriteLine("ok " + root.Count);
