// Project-only recording: ScreenCaptureKit desktop-independent Blender window.
// Never captures the desktop, other app windows, microphone or system audio.
import Foundation
import ScreenCaptureKit
import AVFoundation
import AppKit
let args=CommandLine.arguments
if args.count != 4 && args.count != 5 { fatalError("Usage: swift record_blender_window.swift output.mp4 seconds frames-folder [exact-project-title]") }
let destination=URL(fileURLWithPath:args[1]),seconds=Double(args[2])!,frames=URL(fileURLWithPath:args[3],isDirectory:true)
class RecorderDelegate:NSObject,SCRecordingOutputDelegate {
 func recordingOutputDidStartRecording(_ recordingOutput:SCRecordingOutput) { print("Started Blender-only window recording.");fflush(stdout) }
 func recordingOutput(_ recordingOutput:SCRecordingOutput,didFailWithError error:Error) { print("Recording failed: \(error)");exit(1) }
 func recordingOutputDidFinishRecording(_ recordingOutput:SCRecordingOutput) {
  Task {
   do {
    let asset=AVURLAsset(url:destination);let duration=try await asset.load(.duration).seconds
    let video=try await asset.loadTracks(withMediaType:.video),audio=try await asset.loadTracks(withMediaType:.audio)
    let generator=AVAssetImageGenerator(asset:asset);generator.appliesPreferredTrackTransform=true;generator.maximumSize=CGSize(width:1280,height:900)
    try FileManager.default.createDirectory(at:frames,withIntermediateDirectories:true)
    for second in [2.0,8.0,16.0] where second<duration {
     let frame=try await generator.image(at:CMTime(seconds:second,preferredTimescale:600));let png=NSBitmapImageRep(cgImage:frame.image).representation(using:.png,properties:[:])!
     try png.write(to:frames.appendingPathComponent("window-\(Int(second))s.png"))
    }
    print("Verified: \(duration)s, \(video.count) video, \(audio.count) audio tracks; decoded window frames.");exit(0)
   } catch { print(error);exit(1) }
  }
 }
}
let application=NSApplication.shared
let delegate=RecorderDelegate()
Task { @MainActor in
 do {
  let content=try await SCShareableContent.excludingDesktopWindows(false,onScreenWindowsOnly:false)
  guard let window=content.windows.first(where:{$0.owningApplication?.bundleIdentifier=="org.blenderfoundation.blender" && ($0.title ?? "").contains(args.count == 5 ? args[4] : "Circular-Ribbon-Cloud")}) else { fatalError("Intended Blender project window unavailable; no desktop fallback.") }
  let filter=SCContentFilter(desktopIndependentWindow:window),config=SCStreamConfiguration()
  config.width=1440;config.height=Int((1440*window.frame.height/window.frame.width)/2)*2;config.minimumFrameInterval=CMTime(value:1,timescale:24);config.showsCursor=false;config.capturesAudio=false;config.captureMicrophone=false
  let settings=SCRecordingOutputConfiguration();settings.outputURL=destination;settings.videoCodecType = .h264;settings.outputFileType = .mp4
  let output=SCRecordingOutput(configuration:settings,delegate:delegate),stream=SCStream(filter:filter,configuration:config,delegate:nil)
  try stream.addRecordingOutput(output);try await stream.startCapture()
  try await Task.sleep(nanoseconds:UInt64(seconds*1_000_000_000));try await stream.stopCapture()
  // Stream/output remain referenced through the recording completion callback.
  try await Task.sleep(nanoseconds:15_000_000_000);print("Timed out waiting for file completion.");exit(1)
 } catch { print(error);exit(1) }
}
application.run()
