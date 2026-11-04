// A rendered still-stage review. This does not capture the screen or record editing.
import Foundation
import AVFoundation
import AppKit
import CoreVideo
let a=CommandLine.arguments
if a.count != 3 { fatalError("Usage: swift rendered_stage_video.swift cards-folder output.mp4") }
let folder=URL(fileURLWithPath:a[1],isDirectory:true),output=URL(fileURLWithPath:a[2])
let width=1280,height=800,fps:Int32=24,seconds=6
let writer=try AVAssetWriter(outputURL:output,fileType:.mp4)
let input=AVAssetWriterInput(mediaType:.video,outputSettings:[AVVideoCodecKey:AVVideoCodecType.h264,AVVideoWidthKey:width,AVVideoHeightKey:height])
let adaptor=AVAssetWriterInputPixelBufferAdaptor(assetWriterInput:input,sourcePixelBufferAttributes:[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32ARGB,kCVPixelBufferWidthKey as String:width,kCVPixelBufferHeightKey as String:height,kCVPixelBufferCGImageCompatibilityKey as String:true,kCVPixelBufferCGBitmapContextCompatibilityKey as String:true])
writer.add(input);writer.startWriting();writer.startSession(atSourceTime:.zero)
for stage in 1...4 {
 let path=folder.appendingPathComponent(String(format:"%02d.png",stage));let ns=NSImage(contentsOf:path)!
 var rect=CGRect(x:0,y:0,width:width,height:height)
 let image=ns.cgImage(forProposedRect:&rect,context:nil,hints:nil)!
 var pixel:CVPixelBuffer?;CVPixelBufferCreate(kCFAllocatorDefault,width,height,kCVPixelFormatType_32ARGB,nil,&pixel)
 let buffer=pixel!;CVPixelBufferLockBaseAddress(buffer,[])
 let ctx=CGContext(data:CVPixelBufferGetBaseAddress(buffer),width:width,height:height,bitsPerComponent:8,bytesPerRow:CVPixelBufferGetBytesPerRow(buffer),space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.noneSkipFirst.rawValue)!
 ctx.draw(image,in:rect);CVPixelBufferUnlockBaseAddress(buffer,[])
 for f in 0..<(Int(fps)*seconds) {
  while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval:0.005) }
  let index=(stage-1)*Int(fps)*seconds+f
  if !adaptor.append(buffer,withPresentationTime:CMTime(value:Int64(index),timescale:fps)) { fatalError("Frame failed: \(String(describing:writer.error))") }
 }
}
input.markAsFinished()
writer.finishWriting {
 if writer.status != .completed { fatalError("Video failed: \(String(describing:writer.error))") }
 Task {
  do {
   let asset=AVURLAsset(url:output),duration=try await AVURLAsset(url:output).load(.duration).seconds
   let tracks=try await asset.loadTracks(withMediaType:.video)
   let generator=AVAssetImageGenerator(asset:asset);generator.appliesPreferredTrackTransform=true
   let frame=try await generator.image(at:CMTime(seconds:19,preferredTimescale:600))
   let png=NSBitmapImageRep(cgImage:frame.image).representation(using:.png,properties:[:])!
   try png.write(to:folder.appendingPathComponent("verified-video-frame.png"))
   print("Verified MP4: \(duration)s, \(tracks.count) video track; decoded frame at 19s. No audio.");exit(0)
  } catch { print(error);exit(1) }
 }
}
dispatchMain()
