# Android
Building your app for android
## Requirements
 - `buildozer`
## Steps
1) Create `buildozer.spec` with `buildozer init`
2) Customize it (example [here](https://github.com/Pyxelsuft/goodgame/blob/main/buildozer.spec))
3) Build you app with `buildozer android debug deploy run`
4) Test with your android phone or emulator, use `adb` for debugging
## Notes
Buildozer uses an old pysdl2 version, idk why. <br />
So, you can download [latest pysdl2 release](https://github.com/py-sdl/py-sdl2/releases/latest) and put `sdl2` folder next to your project to bypass this.