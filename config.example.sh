# Copy to config.sh and adjust. All build scripts source config.sh.
export W="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"          # this checkout
export KIT="$HOME/Unreal Projects/TheKillingAntidote_Ani_And_Hair"  # the developer's sample mod project (UE 4.27) with Plugins/TKA_BPGen -> $W/bpgen
export UPROJECT="$KIT/TheKillingAntidote.uproject"
export ENGINE="$HOME/UnrealEngine-4.27"                            # UE 4.27 source build
export UE_CMD="$ENGINE/Engine/Binaries/Linux/UE4Editor-Cmd"
export UNREALPAK="$ENGINE/Engine/Binaries/Linux/UnrealPak"
export GAME="$HOME/.steam/steam/steamapps/common/TheKillingAntidote/TheKillingAntidote"   # deploy target
export COOKED="$KIT/Saved/Cooked/LinuxNoEditor/TheKillingAntidote/Content"
export BUILD="$W/build"
# optional checks (unset = skipped): GAME_API_DIR = directory with one <Class>.txt signature dump per game class (verify_stubs),
# GAME_PAK_FILELIST = text file listing every file in the game paks (verify_pak import-target check)
