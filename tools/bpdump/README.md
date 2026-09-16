# bpdump – Blueprint bytecode from cooked assets

Dumps every function of a cooked Blueprint (UE 4.27) as Kismet JSON (UAssetAPI `KismetSerializer`, with statement offsets);
`scripts/kismet_pp.py` prints it as readable pseudocode (push/pop = execution-flow stack, `goto` = byte offset).
Used to check what actually ended up in a build, e.g. `BP_AltUIManager` from the cooked output.

```bash
cd tools/bpdump && dotnet build -c Release          # once (fetches UAssetAPI from NuGet)
tools/bpdump/bin/Release/net10.0/bpdump <cooked>/Mod/AltUI/BP_AltUIManager.uasset build/mgr.json
python3 scripts/kismet_pp.py build/mgr.json "Capture Photo" "Toggle Panel"     # filters = substrings of function names
```
Events end up in `ExecuteUbergraph_*`; the event's stub calls `ExecuteUbergraph(EntryPoint)` – that offset is the entry point.
