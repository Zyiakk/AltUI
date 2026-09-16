#include "BPGenTypes.h"
#include "Engine/Blueprint.h"
#include "Engine/UserDefinedStruct.h"
#include "Engine/UserDefinedEnum.h"
#include "EdGraphSchema_K2.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/Package.h"
#include "Misc/PackageName.h"

UObject* BPGenTypes::LoadObj(const FString& InPath) {
  FString Path = InPath;
  UObject* Obj = nullptr;
  if (Path.StartsWith(TEXT("/Script/"))) {
    Obj = FindObject<UObject>(ANY_PACKAGE, *Path);
    if (!Obj) Obj = LoadObject<UObject>(nullptr, *Path);
    return Obj;
  }
  FString PackageName = Path, ObjectName;
  if (Path.Contains(TEXT("."))) { Path.Split(TEXT("."), &PackageName, &ObjectName); }
  UPackage* Pkg = LoadPackage(nullptr, *PackageName, LOAD_None);
  if (!Pkg) return nullptr;
  if (ObjectName.IsEmpty()) ObjectName = FPackageName::GetShortName(PackageName);
  Obj = FindObject<UObject>(Pkg, *ObjectName);
  if (!Obj && ObjectName.EndsWith(TEXT("_C"))) Obj = FindObject<UObject>(Pkg, *ObjectName.LeftChop(2));
  if (UBlueprint* BP = Cast<UBlueprint>(Obj)) return BP->GeneratedClass;
  return Obj;
}

UClass* BPGenTypes::LoadClassChecked(const FString& Path) { return Cast<UClass>(LoadObj(Path)); }

static bool BaseType(const FString& Spec, FEdGraphPinType& T, FString& Err) {
  FString Kind = Spec, Arg;
  Spec.Split(TEXT(":"), &Kind, &Arg);
  Kind = Kind.ToLower();
  T.PinSubCategoryObject = nullptr;
  if (Kind == TEXT("bool")) T.PinCategory = UEdGraphSchema_K2::PC_Boolean;
  else if (Kind == TEXT("int")) T.PinCategory = UEdGraphSchema_K2::PC_Int;
  else if (Kind == TEXT("int64")) T.PinCategory = UEdGraphSchema_K2::PC_Int64;
  else if (Kind == TEXT("float")) T.PinCategory = UEdGraphSchema_K2::PC_Float;
  else if (Kind == TEXT("name")) T.PinCategory = UEdGraphSchema_K2::PC_Name;
  else if (Kind == TEXT("string")) T.PinCategory = UEdGraphSchema_K2::PC_String;
  else if (Kind == TEXT("text")) T.PinCategory = UEdGraphSchema_K2::PC_Text;
  else if (Kind == TEXT("byte")) T.PinCategory = UEdGraphSchema_K2::PC_Byte;
  else if (Kind == TEXT("object") || Kind == TEXT("class") || Kind == TEXT("softobject") || Kind == TEXT("softclass")) {
    UClass* C = BPGenTypes::LoadClassChecked(Arg);
    if (!C) { Err = TEXT("class not found: ") + Arg; return false; }
    T.PinCategory = Kind == TEXT("object") ? UEdGraphSchema_K2::PC_Object : Kind == TEXT("class") ? UEdGraphSchema_K2::PC_Class
                  : Kind == TEXT("softobject") ? UEdGraphSchema_K2::PC_SoftObject : UEdGraphSchema_K2::PC_SoftClass;
    T.PinSubCategoryObject = C;
  }
  else if (Kind == TEXT("struct")) {
    UScriptStruct* S = Cast<UScriptStruct>(BPGenTypes::LoadObj(Arg));
    if (!S) { Err = TEXT("struct not found: ") + Arg; return false; }
    T.PinCategory = UEdGraphSchema_K2::PC_Struct; T.PinSubCategoryObject = S;
  }
  else if (Kind == TEXT("enum")) {
    UEnum* E = Cast<UEnum>(BPGenTypes::LoadObj(Arg));
    if (!E) { Err = TEXT("enum not found: ") + Arg; return false; }
    T.PinCategory = UEdGraphSchema_K2::PC_Byte; T.PinSubCategoryObject = E;
  }
  else { Err = TEXT("unknown type spec: ") + Spec; return false; }
  return true;
}

bool BPGenTypes::PinTypeFromSpec(const FString& Spec, const FString& Container, const FString& ValueSpec, FEdGraphPinType& Out, FString& Err) {
  Out = FEdGraphPinType();
  if (!BaseType(Spec, Out, Err)) return false;
  const FString C = Container.ToLower();
  if (C == TEXT("array")) Out.ContainerType = EPinContainerType::Array;
  else if (C == TEXT("set")) Out.ContainerType = EPinContainerType::Set;
  else if (C == TEXT("map")) {
    Out.ContainerType = EPinContainerType::Map;
    FEdGraphPinType V; if (!BaseType(ValueSpec, V, Err)) return false;
    Out.PinValueType.TerminalCategory = V.PinCategory; Out.PinValueType.TerminalSubCategoryObject = V.PinSubCategoryObject;
  }
  return true;
}

FString BPGenTypes::PinTypeToString(const FEdGraphPinType& T) { return UEdGraphSchema_K2::TypeToText(T).ToString(); }
